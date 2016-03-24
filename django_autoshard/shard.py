from django.db import connections


class Shard:
    def __init__(self, index, alias, replicas):
        self.__index = index
        self.__alias = alias
        self.__replicas = replicas

    @property
    def alias(self):
        return self.__alias

    @property
    def index(self):
        return self.__index

    @property
    def connection(self):
        return connections[self.alias]

    def __str__(self):
        return self.alias
