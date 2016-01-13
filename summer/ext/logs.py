import socket
from logging import Filter

from summer.settings import APP_CONFIG

class IPFilter(Filter):
    def __init__(self, name=''):
        super(IPFilter, self).__init__(name)
        self.ip = socket.gethostbyname(socket.gethostname())

    def filter(self, record):
        record.ip = self.ip + ':%s' % APP_CONFIG.get('port', '??')
        return True