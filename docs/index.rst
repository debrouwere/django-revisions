=============================================
Welcome to  django-versioning's documentation!
=============================================

Contents:

.. toctree::
   :glob:
   
   *

``django-revisions`` is a Django app that allows you to keep a version history for model instances. It has a simple API, but is also integrated with the Django admin interface. ``django-revisions`` doesn't add any tables to your database, nor does it work by serializing old revisions -- making this app very natural to work with and migration-friendly, as opposed to other solutions out there. (See :doc:`design`.)

* Access and revert to any previous model save with a convenient and minimally intrusive API.
* Utilities that make it easy to redirect users to the latest revision, when they try to access older versions. Don't worry about web content with changing slugs anymore.
* An optional trash bin for deleted content.
* Admin integration: restore trash, revert content to an older revision, view version history and do diffs.
* Works flawlessly with migration tools like `South <http://south.aeracode.org/>`_

``django-revisions`` takes care of model instance version history. If you found this page while looking for asset versioning of media files, like javascript or CSS, take a look at ``django-css`` and related apps instead.

===============
Getting Started
===============

Installation
============

Models
------

Working with existing models -----

**Currently, this application does not work with concrete inheritance (i.e. models spread out over multiple tables, joined together by primary key). It will soon.**

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

- regular
- convenience shortcuts

Some examples
-------------

Methods and attributes
----------------------

.. automodule:: revisions.models
   :show-inheritance:
   :members:
   :undoc-members:

Development: reporting bugs, helping out, running the test suite
================================================================

Development takes place on GitHub. Feel free to fork, and please report any bugs or feature requests over there. Run the test suite simply by executing ``python manage.py test revisions``. ``django-versioning`` has only been tested on Django 1.2, but will probably work on any 1.x installation.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`