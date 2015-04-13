# -*- coding: utf-8 -*-

import os
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/.pypirc'))

servers = config.get('distutils', 'index-servers').split('\n')
servers = filter(lambda i: i, servers)

print '\n'.join(servers)
