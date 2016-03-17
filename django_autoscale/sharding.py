from django.conf import settings as django_settings
from django.db import connections
from . import settings


def configure():
    nodes = settings.NODES
    for node, config in nodes.items():
        try:
            db_name = config['NAME']
        except KeyError:
            raise RuntimeError('Node {} does not have a database name.'.format(node))

        for i in config['RANGE']:
            shard = config
            shard['NAME'] = '{}_{}'.format(db_name, i)
            django_settings.DATABASES['{}{}'.format(node, i)] = shard

    for connection in connections.all():
        print(connection.alias)
