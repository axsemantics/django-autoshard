from django.conf import settings
from django.db import models

from django_autoshard.querysets import ShardedQuerySet


class ShardedManager(models.Manager):
    _queryset_class = ShardedQuerySet

    def all(self, limit=None):
        if not hasattr(settings, 'SHARDS') or len(settings.SHARDS) == 0:
            return super(ShardedManager, self).all()
        result = []
        for data in self._all():
            result.extend(data)
            if len(result) >= limit:
                break
        return result

    def _all(self):
        for _, shard in settings.SHARDS.items():
            with shard.connection.cursor() as cursor:
                cursor.execute('SELECT * from %s' % self.model._meta.db_table)

                yield self.dictfetchall(cursor)
            shard.connection.close()

    def dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [
            self.model(**dict(zip(columns, row)))
            for row in cursor.fetchall()
        ]
