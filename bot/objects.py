class ProxymonObject(object):
    def __init__(self, name):
        self.name = name

    def dump(self):
        return self.name.upper().replace(" ", "_")
