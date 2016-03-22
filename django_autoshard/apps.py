from django.apps import AppConfig


class DjangoAutoShardApp(AppConfig):
    name = 'django_autoshard'
    verbose_name = 'Django Autoshard'

    def ready(self):
        from .sharding import Sharding
        Sharding().configure()
