import sys


def load_module_from_file(module_name, filepath, sys_path=None):
    if sys_path:
        sys.path.insert(0, sys_path)

    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    cls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cls)

    if sys_path:
        sys.path.remove(sys_path)

    return cls


def datetime_to_str(dt):
    return dt.strftime('%Y-%m-%dT%H:%M')


def merge_dict(existing_dict, new_dict):
    for config_name, config_value in new_dict.items():
        existing_dict[config_name] = config_value

    return existing_dict


def crontab_hour_to_utc(crontab_hour, timezone):
    import re

    rebuild_hour_items = []
    for hour_item in re.split(r'([-,])', crontab_hour):
        if hour_item in ['-', ',']:
            rebuild_hour_items.append(hour_item)
        else:
            try:
                hour_num = int(hour_item)
            except ValueError:
                # Error, return original
                return crontab_hour

            utc_hour = hour_num - timezone

            if utc_hour < 0:
                utc_hour = utc_hour + 24

            rebuild_hour_items.append(str(utc_hour))

    return ''.join(rebuild_hour_items)
