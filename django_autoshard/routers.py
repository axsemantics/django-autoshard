from django_autoshard.models import ShardedModel


class ShardRouter:
    def db_for_write(self, model, **hints):
        try:
            instance = hints['instance']
            if issubclass(model, ShardedModel) or isinstance(instance, ShardedModel):
                return instance.shard.alias
        except KeyError:
            pass
        return None
