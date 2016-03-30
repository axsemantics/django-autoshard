from django.conf import settings
from django.db import models

from django_autoshard import utils


class ShardedQuerySet(models.QuerySet):
    def filter(self, *args, **kwargs):
        if not hasattr(settings, 'SHARDS') or len(settings.SHARDS) == 0:
            return super(ShardedQuerySet, self).filter(*args, **kwargs)

        if 'pk' in kwargs:
            shard_index = utils.get_shard_index_from_uuid(kwargs['pk'])
            shard = utils.get_shard_from_index(shard_index)
            self._db = shard.alias
        elif self.model.SHARD_KEY in kwargs:
            shard = utils.get_shard(kwargs[self.model.SHARD_KEY])
            self._db = shard.alias
        return super(ShardedQuerySet, self).filter(*args, **kwargs)
