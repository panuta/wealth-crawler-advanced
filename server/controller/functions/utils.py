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
