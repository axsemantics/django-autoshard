from collections import OrderedDict

from django.conf import settings as django_settings
from django_autoshard import settings
from .shard import Shard
from . import utils


class ShardingFactory:
    SHARDS = OrderedDict()

    def configure(self):
        for node, config in settings.SHARDS.items():
            try:
                _ = config['NAME']
            except KeyError:
                raise RuntimeError('Node {} does not have a database name.'.format(node))
            self.set_logical_shards(node, config)

        self.SHARDS = OrderedDict(sorted(self.SHARDS.items()))
        django_settings.SHARDS = self.SHARDS

    def set_logical_shards(self, node: str, config: dict)->None:
        for i in config['RANGE']:
            shard = config
            shard['NAME'] = '{}_{}'.format(config['NAME'], i)
            node_name = '{}{}'.format(node, i)
            django_settings.DATABASES[node_name] = shard
            node_index = utils.get_shard_index(node_name)
            replicas = self.set_replicas(config)
            self.SHARDS[node_index] = Shard(node_index, node_name, replicas)

    def set_replicas(self, config):
        return {}
