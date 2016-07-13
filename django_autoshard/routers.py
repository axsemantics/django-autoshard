from django_autoshard.models import ShardedModel, ShardRelatedModel


class ShardRouter:
    def db_for_write(self, model, **hints):
        if not issubclass(model, ShardedModel) and not issubclass(model, ShardRelatedModel):
            return 'default'
        instance = hints.get('instance')
        shard = getattr(instance, 'shard', None)
        if shard is not None:
            return shard.alias

    def allow_relation(self, obj1, obj2, **hints):
        return True
