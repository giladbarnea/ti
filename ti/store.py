from os import path

import yaml


class Store(object):

    def __init__(self, filename):
        self.filename = filename

    def load(self):

        if path.exists(self.filename):
            with open(self.filename) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if 'work' not in data:
                    data['work'] = []
                if 'interrupt_stack' not in data:
                    data['interrupt_stack'] = []

        else:
            data = {'work': [], 'interrupt_stack': []}

        return data

    def dump(self, data):
        with open(self.filename, 'w') as f:
            # json.dump(data, f, separators=(',', ': '), indent=2)
            yaml.dump(data, f, indent=4)