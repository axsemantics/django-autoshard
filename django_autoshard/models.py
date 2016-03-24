from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

from django_autoshard import utils


class ShardedUserModel(AbstractUser):
    uuid = models.BigIntegerField(null=True)

    def __init__(self, *args, **kwargs):
        kwargs['__shard'] = utils.get_shard(kwargs['email'])
        super().__init__(*args, **kwargs)

    @property
    def shard(self):
        return self.__shard

    def save(self, *args, **kwargs):
        if self.uuid is not None:
            return super().save(*args, **kwargs)  # UPDATE

        with transaction.atomic(using=self.shard.alias):
            super().save(*args, **kwargs)  # Set the auto-id
            uuid = utils.generate_uuid(self.pk, self.shard.index)
            return super().save(using=kwargs['using'], uuid=uuid)
