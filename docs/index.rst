Welcome to django-versioning's documentation!
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

``django-revisions`` takes care of model instance version history. If you found this page while looking for asset versioning of media files, like javascript or CSS, take a look at ``django-css`` and related apps instead.

Development: reporting bugs, helping out, running the test suite
----------------------------------------------------------------

Development takes place on GitHub. Feel free to fork, and please report any bugs or feature requests over there. Run the test suite simply by executing ``python manage.py test revisions``. ``django-versioning`` has only been tested on Django 1.2, but will probably work on any 1.x installation.





Why django-revisions
--------------------

-> cf. design
-> cf. considerations
-> various conveniences (template tags, api, diffing, log messages)
-> well-documented
-> good test coverage, and getting better
-> support

Features
--------



===============
Getting Started
===============

Installation
============

Working with existing models
----------------------------

Admin integration
=================

API
===

Some examples
-------------

Methods and attributes
----------------------

.. automodule:: revisions.models
   :show-inheritance:
   :members:
   :undoc-members:

References to bundles or specific versions
==========================================

A foreign key to a versioned object will always point to a specific
version and not the bundle as a whole.  Sometimes, however, it's useful to be able
to make a reference to the *bundle* and not a specific version.

To get the latest revision from a piece of versioned content you're accessing through
a reference from another model, simply use the ``get_latest_revision`` method.

Accessing related objects the other way around, across multiple revisions, is easy too.
Say you have an Author model that refers to a Story model. On instances, you can simply
use ``story.related_authors`` to access all authors across versions and regardless of which
specific version or versions an author is linked to.

A side note: why you shouldn't use Django's to_field to reference content bundles
---------------------------------------------------------------------------------

In Django 1.0 you used to be able to abuse foreign keys to allow for
pseudo-foreign key references to a *bundle* instead of a specific version.

class Instructions(models.Model):
    # dit om een model te testen gerelateerd aan de bundel
    story = models.ForeignKey(Story, to_field='id')

Because ``VersionedModel.latest`` is the default manager for versioned content, 
such a foreign key attribute would then return the latest revision of the bundle
even though the bundle id field is be shared among revisions.

However, in Django 1.2, this no longer works, because foreign keys should by their
very nature only reference unique fields. See 
http://groups.google.com/group/django-users/browse_thread/thread/fcd3915a19ae333e
and 
http://code.djangoproject.com/ticket/11702
for more information.

(Voorbeeld geven waarom linken aan revisie steek kan houden: bv. als het content is die mee-gerevisioneerd wordt, of als je de oorspronkelijke context van de link wil kennen, bv. bij comments op een artikel.)

Adding your own managers
------------------------

=> make sure to add revisions.managers.LatestManager() back in.

Working with django-revisions in the admin interface
----------------------------------------------------


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`