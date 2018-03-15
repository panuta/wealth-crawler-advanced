LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


# Scrapyd
SCRAPYD_URL = 'http://scrapyd:6800'
SCRAPY_PROJECT_NAME = 'spiders'


# Spiders deployment
CRAWLER_SPIDERS_REPO = 'git@bitbucket.org:chaostheory_th/crawler_spiders.git'
CRAWLER_SPIDERS_BRANCH = 'v2'

CRAWLER_SPIDERS_SETTINGS_FILENAME = 'spiders.json'

DEPLOY_TEMP_PATH = '/tmp'
LOCAL_SPIDERS_MODULE = 'scrapy_project'


# Cron timezone
CRONTAB_TIMEZONE = 7  # 0 means UTC
