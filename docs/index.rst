=============================================
Welcome to  django-versioning's documentation!
=============================================

Contents:

.. toctree::
   :glob:
   
   *

``django-revisions`` is a Django app that allows you to keep a version history for model instances. It has a simple API, but is also integrated with the Django admin interface. ``django-revisions`` doesn't add any tables to your database, nor does it work by serializing old revisions -- making this app very natural to work with and migration-friendly, as opposed to other solutions out there. (See :doc:`design`.)

* Access and revert to any previous model save with a convenient and minimally intrusive API.
* An optional trash bin for deleted content.
* Admin integration: restore trash, revert content to an older revision.
* Works flawlessly with migration tools like `South <http://south.aeracode.org/>`_

``django-revisions`` takes care of model instance version history. If you found this page while looking for asset versioning of media files, like javascript or CSS, take a look at ``django-css`` and related apps instead.

===============
Getting Started
===============

Installation
============

Models
------

`django-revisions` works by adding `models.VersionedModel` as a base class to your model as well as — if you prefer — `shortcuts.VersionedModel`. You can enable a trash function by adding `models.TrashableModel` as a base class to your model *and* adding the class decorator `decorators.trash_aware` to any model for which you want to enable trash (that is, soft deletes).

All three classes are independent, so you'll have to add them in separately.

The models and API work with both single-table models and `joined tables <http://jacobian.org/writing/concrete-inheritance/>`_ (that is, `concrete inheritance <http://docs.djangoproject.com/en/dev/topics/db/models/#model-inheritance>`_).

`django-revisions` makes no effort to be a drop-in for existing models. It adds fields to your models, which means you'll have to run a South migration to get you started, and you'll have to run a small script to generate bundle IDs (they can just equal the object PK).

See :doc:`models` for more detail.

Admin integration
-----------------
    
.. automodule:: revisions.admin

Deleting and trashing versioned content
---------------------------------------

This application also includes a simple abstract model that will put deleted objects into a **trash bin**, rather than outright deleting them from the database. ``TrashableModel`` works with any model, versioned or not. It adds a single ``is_trash`` field to the database table, so make sure to add that in manually or remember to execute a migration.

Note that, for design reasons, you can't trash individual revisions. If you want to undo a revision, ``obj.revert_to(obj.get_revisions().prev)`` or ``obj.get_revisions().prev.make_current_revision()`` are the preferred methods. That way, the version history is kept intact.

Hard deleting indidual revisions is possible for administration purposes, using ``obj.delete_revision()``, but is highly discouraged.

API
===

`django-revisions` is still sorely lacking in documentation, though early adopters can get started by browsing through the methods available on `models.TrashableModel`, `models.VersionedModel` and the shortcuts in `shortcuts.VersionedModel`.

Some examples
-------------

    # models.py
    from django.db import models
    import revisions
    class Story(revisions.models.VersionedModel, revisions.shortcuts.VersionedModel):
        title = models.CharField(max_length=200)
        date = models.DateTimeField(auto_now=True)
        log = models.CharField(max_length=200)
    
        def __unicode__(self):
            return self.title
    
        class Versioning:
            publication_date = 'date'
            clear_each_revision = ['log']
    
    # interactive session
    >>> story = Story(title="a story (v1)")
    >>> story.save()
    >>> story.pk
    1
    >>> story.title = "a story (v2)"
    >>> story.save()
    >>> story.pk
    2
    >>> story.get_revisions()
    [<Story: a story (v1)>, <Story: a story (v2)>]
    >>> story.get_revisions()[0].make_current_revision()
    >>> story.pk
    3
    >>> story.get_revisions()
    [<Story: a story (v1)>, <Story: a story (v2)>, <Story: a story (v1)>]
    >>> old_story = story.get_revisions()[0]
    >>> # revert to a story
    >>> story.revert_to(old_story)
    >>> # or a primary key
    >>> story.revert_to(2)
    >>> # dates work as well
    >>> story.revert_to(old_story.date)
    >>> story.log = "Changed some stuff"
    >>> story.save()
    >>> # the Django admin clears out fields that have to be empty on each rev for you: 
    >>> story.prepare_for_writing()
    >>> story.log
    ''

Methods and attributes
----------------------

.. automodule:: revisions.models
   :show-inheritance:
   :members:
   :undoc-members:

Shortcuts
'''''''''

.. automodule:: revisions.shortcuts
   :show-inheritance:
   :members:
   :undoc-members:

Development: reporting bugs, helping out, running the test suite
================================================================

Development takes place on GitHub. Feel free to fork, and please report any bugs or feature requests over there. Run the test suite simply by executing ``python manage.py test revisions``. ``django-versioning`` has been known to work on Django 1.2 but only undergoes frequent testing on Django 1.3. That said, it will probably work on any 1.x installation.

Roadmap
=======

The first priority is better documentation. After that, there are some features that may or may not get added to the app:

* view version history and do diffs in the admin
* a view wrapper or query shortcut that can handle redirecting to the latest revision when users stumble on outdated content (e.g. when a new revision has a different slug)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`