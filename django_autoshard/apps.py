from django.apps import AppConfig
from django.conf import settings


class DjangoAutoShardApp(AppConfig):
    name = 'django_autoshard'
    verbose_name = 'Django Autoshard'

    def __init__(self, app_name, app_module):
        settings.AUTH_USER_MODEL = 'django_autoshard.ShardedUserModel'
        super().__init__(app_name, app_module)

    def ready(self):
        from .factory import ShardingFactory
        ShardingFactory().configure()
