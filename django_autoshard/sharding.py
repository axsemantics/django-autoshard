from collections import OrderedDict
from hashlib import md5

from django.conf import settings as django_settings
from django.apps import apps
from django.db import connections
from django.db.models.signals import pre_save
from django.dispatch import receiver
from . import settings


class Shard:
    def __init__(self, alias, replicas):
        self.alias = alias
        self.replicas = replicas

    @property
    def connection(self):
        return connections[self.alias]

    def __str__(self):
        return self.alias


class Sharding:
    SHARDS = OrderedDict()

    def configure(self):
        for node, config in settings.SHARDS.items():
            try:
                _ = config['NAME']
            except KeyError:
                raise RuntimeError('Node {} does not have a database name.'.format(node))
            self.set_logical_shards(node, config)

        self.set_sharded_model()

        # self.SHARDS = sorted(self.SHARDS)
        self.SHARDS = OrderedDict(sorted(self.SHARDS.items()))
        print(self.SHARDS)
        # for connection in connections.all():
        #    print(connection.alias)

    def set_logical_shards(self, node: str, config: dict)->None:
        for i in config['RANGE']:
            shard = config
            shard['NAME'] = '{}_{}'.format(config['NAME'], i)
            node_name = '{}{}'.format(node, i)
            django_settings.DATABASES[node_name] = shard
            node_index = Sharding.get_shard_index(node_name)
            replicas = self.set_replicas(config)
            self.SHARDS[node_index] = Shard(node_name, replicas)

    def set_replicas(self, config):
        return {}

    def set_sharded_model(self):
        model = apps.get_model(settings.SHARDED_MODEL)
        print(model)

    @staticmethod
    def pre_save_sharded_model(sender, instance):
        pass

    @staticmethod
    def get_shard_index(key):
        _hash = md5(key.encode()).hexdigest()
        return int(_hash, 16) % settings.MAX_SHARDS
