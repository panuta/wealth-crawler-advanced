import configparser
import inspect
import os
import shortuuid
import shutil
import subprocess
from datetime import datetime

from git import Repo, GitCommandError

from server import config
from server.controller.models import Spider, Project
from server.utils import load_module_from_file


def pred(c):
    return inspect.isclass(c) and c.__module__ == pred.__module__


def _persist_spiders(clone_path, project):
    deploy_date = datetime.now()

    # Load SPIDER_MODULES settings from scrapy settings file
    # ------------------------------------------------------------------------------------------------------------------

    scrapy_settings_filepath = os.path.join(clone_path, 'crawler/settings.py')

    if not os.path.isfile(scrapy_settings_filepath):
        raise Exception('Scrapy settings is missing')

    scrapy_settings = load_module_from_file('scrapy_settings', scrapy_settings_filepath)
    spider_modules = set(getattr(scrapy_settings, 'SPIDER_MODULES', []))

    # Find spiders in SPIDER_MODULES
    # ------------------------------------------------------------------------------------------------------------------

    for spider_module_name in spider_modules:
        module_filepath = os.path.join(clone_path, '{}.py'.format(spider_module_name.replace('.', '/')))
        spider_module = load_module_from_file(
            spider_module_name, module_filepath, sys_path=clone_path)

        classmembers = inspect.getmembers(spider_module, inspect.isclass)

        for classmember in classmembers:
            if classmember[1].__module__ != spider_module_name:
                # Only include spiders defined within a module (not imported)
                continue

            is_spider_class = False
            for class_parent in inspect.getmro(classmember[1])[1:]:
                if class_parent.__module__ == 'scrapy.spiders' and class_parent.__name__ == 'Spider':
                    is_spider_class = True

            if is_spider_class and classmember[1].name:
                try:
                    spider = Spider.get(Spider.name == classmember[1].name)
                except Spider.DoesNotExist:
                    spider = Spider(
                        name=classmember[1].name,
                        project_name=project.project_name,
                        date_deployed=deploy_date,
                    )
                else:
                    spider.date_deployed = deploy_date

                spider.save()

    query = Spider.delete().where(Spider.date_deployed != deploy_date)
    query.execute()


def deploy(clone_url, branch=None):
    now = datetime.now()

    # Working paths
    # ------------------------------------------------------------------------------------------------------------------

    clone_pathname = 'deploy-{datetime}-{uuid}'.format(
        datetime=now.strftime('%Y-%m-%dT%H-%M'), uuid=shortuuid.uuid())
    clone_path = os.path.join(config.DEPLOY_TEMP_PATH, clone_pathname)

    # Clone spiders from git repo and copy to deploy location (override local project)
    # ------------------------------------------------------------------------------------------------------------------

    try:
        if branch:
            Repo.clone_from(clone_url, clone_path, branch=branch)
        else:
            Repo.clone_from(clone_url, clone_path)
    except GitCommandError as e:
        raise Exception('GitCommandError: {}'.format(e))

    # Get project name from scrapy.cfg
    # ------------------------------------------------------------------------------------------------------------------

    config_parser = configparser.ConfigParser()
    config_parser.read(os.path.join(clone_path, 'scrapy.cfg'))

    if config_parser.has_option('deploy', 'project'):
        project_name = config_parser['deploy']['project']
    else:
        raise Exception('scrapy.cfg not found or project name in scrapy.cfg not found')

    project, created = Project.get_or_create(project_name=project_name)

    # Keep spiders data in database
    # ------------------------------------------------------------------------------------------------------------------

    _persist_spiders(clone_path, project)

    # Call 'scrapyd-deploy' to create egg file and deploy to scrapyd
    # ------------------------------------------------------------------------------------------------------------------

    rc = subprocess.call(['scrapyd-deploy'], cwd=clone_path)

    if rc != 0:
        raise Exception('Error deploy spider to Scrapyd using scrapy-deploy')

    # Delete tmp
    # ------------------------------------------------------------------------------------------------------------------

    shutil.rmtree(clone_path, ignore_errors=True)
