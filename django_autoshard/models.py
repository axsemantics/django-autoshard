from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

from django_autoshard import utils
from django_autoshard.managers import ShardedManager


class ShardedModel(models.Model):
    uuid = models.BigIntegerField(null=True)

    objects = ShardedManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ShardedModel, self).__init__(*args, **kwargs)
        try:
            key = getattr(self, self.SHARD_KEY)  # kwargs[self.SHARD_KEY]
        except AttributeError:
            raise RuntimeError('{} does not define a SHARD_KEY'.format(self.__repr__()))
        except KeyError:
            raise RuntimeError('{} does not have {} set'.format(self.__repr__(), self.SHARD_KEY))
        self.__shard = utils.get_shard(key)

    @property
    def shard(self):
        return self.__shard

    def save(self, *args, **kwargs):
        kwargs['using'] = self.shard.alias
        if self.uuid is not None:
            return super(ShardedModel, self).save(*args, **kwargs)  # UPDATE

        with transaction.atomic():
            super(ShardedModel, self).save(*args, **kwargs)  # Set the auto-id
            self.uuid = utils.generate_uuid(self.pk, self.shard.index)
            return super(ShardedModel, self).save()


class User(ShardedModel, AbstractUser):
    SHARD_KEY = 'email'
