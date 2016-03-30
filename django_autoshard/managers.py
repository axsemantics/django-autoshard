from django.conf import settings
from django.contrib.auth import get_user_model
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


class UserManager(ShardedManager):
    def create_user(self, username, email, password=None, save=True):  # pragma: no cover
        user = get_user_model()(username=username,
                    email=email)
        user.set_password(password)
        if save:
            user.save()
        return user

    def create_superuser(self, username, email, password):  # pragma: no cover
        user = self.create_user(username, email, password, False)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

