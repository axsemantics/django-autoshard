.. role:: python(code)
    :language: python

Django Logging
==============

A `Django <https://www.djangoproject.com/>`_ library that makes sharding easy, using the `Consistent Hashing <https://en.wikipedia.org/wiki/Consistent_hashing>`_ algorithm.

.. image:: https://badge.fury.io/py/django-autoshard.svg
    :target: https://badge.fury.io/py/django-autoshard
    
.. image:: https://img.shields.io/pypi/dm/django-autoshard.svg
    :target: https://img.shields.io/pypi/dm/django-autoshard.svg
    
.. image:: https://travis-ci.org/cipriantarta/django-autoshard.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/cipriantarta/django-autoshard

.. image:: https://coveralls.io/repos/github/cipriantarta/django-autoshard/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/github/cipriantarta/django-autoshard?branch=master


Notes
=====
Writing a general sharding library for all business models is practically impossible, but there are common particularities that apply to most of them.

If you are not familiar with sharding, you should first document yourself on what sharding means and how you could apply it to your own business model. You can start `here <https://en.wikipedia.org/wiki/Shard_(database_architecture)>`_.

This library was written with the following business model in mind.

An application usually has a user account that must be different from other user accounts either by using a unique email address, or username, or other information that can be considered unique across the application.

Each user account will be sharded using that unique constraint and all data that belongs to that user will live on the same shard that the user account does.

You can perhaps customize this business model to fit your own requirements, but the idea of this library was to add sharding to a Django app, with a minimum amount of effort.

The sharding algorithm used by this library is inspired by `Instagram's sharding solution <http://instagram-engineering.tumblr.com/post/10853187575/sharding-ids-at-instagram>`_, but instead of an auto-increment ID and stored procedures, this library uses a RNG for the local ID part. This probably means that when the stars align, you might get a collision if an insert is made in the same millisecond and the RNG gives you the same number.


Installation
============

:python:`pip install django-autoshard`

1. Add :python:`django_autoshard` to your INSTALLED_APPS settings like this:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_autoshard',
    )

2. Create a new user model that extends the :python:`ShardedModel` and extend all related models from :python:`ShardRelatedModel`

.. code-block:: python

    from django_autoshard.models import ShardedModel, ShardRelatedModel
    from django_autoshard.managers import ShardedManager


    class User(ShardedModel, AbstractUser):
        SHARD_KEY = 'email'
        objects = UserManager()


    class Book(ShardRelatedModel):
        user = models.ForeignKey(User)

3. Use this model as the default auth model in your :python:`settings.py` file.
    :python:`AUTH_USER_MODEL='<path.to.your.model>.User'`

4. Make sure you have set up the :python:`settings.DATABASES` correctly(any Django supported database back-end will work)
    and add a range of logical shards to each of your configured database node that you want to use for sharding.
        .. code-block:: python

            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'HOST': 'db_a',
                    'NAME': 'my_database',
                    'USER': 'root',
                    'PASSWORD': 'secretpass',
                    'RANGE': range(10),
                },
                'DB_B': {
                    'ENGINE': 'django.db.backends.mysql',
                    'HOST': 'db_b',
                    'NAME': 'my_database',
                    'USER': 'root',
                    'PASSWORD': 'secretpass',
                    'RANGE': range(10, 20),
                },
            }

5. Run :python:`python manage.py migrate`

6. Run :python:`python manage.py create_shards`

7. Run :python:`python manage.py migrate_shards`

8. Run :python:`python manage.py drop_constraints`

Commands
========
Management Commands that come with this library:

    1. create_shards:
        - this command will create all the logical shards(new databases) on all of the configured databases(nodes) in :python:`settings.DATABASES`

    2. migrate_shards:
        - this command will migrate all your application's models to all of the logical shards created with "create_shards"

    3. drop_constraints:
        - this command will drop all the foreign key constraints from the "default" database that have a relation with your "ShardedModel"

Settings
========
The settings are isolated into a single dict in your settings.py file like so:

.. code-block:: python

    DJANGO_AUTOSHARD = {
        'EPOCH': '2016-01-01',
        'MAX_SHARDS': 1000,
    }

:python:`EPOCH` - defaults to :python:`'2016-01-01'`. Must be in :python:`'%Y-%m-%d'` format.

:python:`MAX_SHARDS` - defaults to :python:`8192`. This should NEVER be changed after initial setup, unless you want to rehash all your sharded data.

Caveats
=======
- you will no longer be able to use database joins between your sharded models, but you can still use joins on models that are related to your sharded model(models on the same shard as the user)
- models that come from third party apps that are related to your sharded model and you don't have any control over, will need to have their foreign key dropped(use :python:`drop_constraints` command).
- instead of using :python:`Book.objects.create(...)` you will have to use :python:`book = Book(...)` and then :python:`book.save()`. This is because of how Django model managers work.
- if your business model requires to do searches on shard related models, or other fields of the sharded model besides the configured :python:`SHARD_KEY`, for example text based search, you will need to use tools like Elasticsearch, where you will store your text info and the shard id of tha object that this text info belongs to, in a single Elasticsearch document.
- :python:`ShardedModel` does not support :python:`count()` and :python:`all()`
- :python:`django.contrib.admin` will not work with sharded models

TODO
====

- Add replicas support
- Create shard migration script
- Create a benchmarking script
- Add more tests
- Test against Postgresql and Oracle

Change Log
==========

1.1 [2016-05-21]
----------------
- fixes management commands for python2 and python3 < 3.5
- raise :python:`NotImplementedError` when trying to use :python:`count()` or :python:`all()` on a :python:`ShardedModel`
- Update documentation

1.0(alpha) [2016-04-02]
-----------------------
- Initial release.
