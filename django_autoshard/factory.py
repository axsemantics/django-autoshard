from collections import OrderedDict

from django.apps import apps
from django.conf import settings as django_settings
from django.core import exceptions
from django.db import connection
from .shard import Shard
from . import utils


class ShardingFactory:

    def configure(self):
        shards = dict()
        nodes = django_settings.DATABASES.copy()
        for node, db in nodes.items():
            try:
                _ = db['NAME']
            except KeyError:
                raise exceptions.ImproperlyConfigured('Node {} does not have a database name.'.format(node))
            try:
                _ = db['RANGE']
            except KeyError:
                raise exceptions.ImproperlyConfigured('Node {} does not specify a shard range.'.format(node))

            node_shards = self.set_logical_shards(node, db)
            shards.update(node_shards)

        django_settings.SHARDS = OrderedDict(sorted(shards.items()))
        django_settings.DATABASE_ROUTERS = ('django_autoshard.routers.ShardRouter', )
        self.check_related_models()

    def set_logical_shards(self, node, config):
        result = dict()
        for i in config['RANGE']:
            shard = config.copy()
            del shard['RANGE']
            shard['NAME'] = '{}_{}'.format(config['NAME'], i)
            alias = '{}_{}'.format(node, i)
            django_settings.DATABASES[alias] = shard
            node_index = utils.get_shard_index(alias)
            replicas = self.set_replicas(config)
            result[node_index] = Shard(node_index, alias, replicas)
        return result

    def set_replicas(self, config):
        return {}

    def check_related_models(self):
        with connection.cursor() as cursor:
            cursor.execute('SET foreign_key_checks = 0;')
