import os


class Env(object):
    def __init__(self, **kwargs):
        self.VARS = {key: value[0] for key, value in kwargs.items()}
        self.TYPES = {key: value[1] for key, value in kwargs.items()}

    def read_env(self, file_name='.env'):
        if os.path.exists(file_name):
            with open(file_name, 'r') as env_file:
                for line in env_file.readlines():
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', maxsplit=1)
                        if key in self.TYPES:
                            self.VARS[key] = self.TYPES[key](value)
                        else:
                            self.VARS[key] = value

    def __getitem__(self, key):
        if key in self.VARS:
            return self.VARS[key]
        else:
            raise KeyError('Key {key} did not exists in the enviroment'.format(key=key))

