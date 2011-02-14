====================================
The basic design of django-revisions
====================================

Ways of versioning
==================

``django-revisions`` works by linking different revisions of the same content together using a shared id, while identifying each individual revision using a version id (vid). The version id serves as the primary key. This is the same approach as used by content management systems like Wordpress and Drupal.

There are a couple of different architectures in use that each do versioning in a different way.

* `MessageDB <http://github.com/thisismedium/message-db>`_ is a dedicated versioned data store.
* A couple of systems use a version control system as the back-end for versioning, like `django-rcsfield <http://github.com/jezdez/django-rcsfield>`_ or the `Jekyll <http://github.com/mojombo/jekyll>`_ blog system.
* `django-reversion <https://github.com/etianen/django-reversion>`_ stores history in a serialized format (e.g. pickled, perhaps as a delta) on the model itself. This is the most popular choice right now.
* `django-modelhistory <http://code.google.com/p/django-modelhistory/>`_ (inactive), `django-history <http://github.com/shreddawg/django-history>`_ (inactive), `django-history-tables <http://code.google.com/p/django-history-tables/>`_ (inactive), `AuditTrail <http://code.djangoproject.com/wiki/AuditTrail>`_ (inactive), `Audit <https://basieproject.org/stable/svn/basie/trunk/apps/audit/>`_ (inactive), `django-versioning <http://github.com/brosner/django-versioning>`_ all store model history in a different table from the model data itself -- often but not always pickled.
* This app stores history is in the same database, in the same table(s), and unpickled: any version including the most recent one is stored in an identical format, plainly viewable in the database.

Advantages to same-table versioning
-----------------------------------

While storing old versions as serialized objects is easiest to implement, there are definite advantages to same-table same-format versioning.

* Any version is equal: old versions are easily queryable both from Django or from any other piece of software in any language, using plain SQL. Serialized data does not provide for easy querying, which makes certain use-cases tough or resource-heavy, like redirecting users who visit old content (perhaps with a different slug) to the latest version, or querying the database from systems other than Django.
* Migrations are a helluvalot easier with same-table versioning than with a versioning system that relies on serializing, as most do. Unless you write custom migration scripts, serialized data is very prone to schema conflicts when you update model definitions.

While using a version control system to keep version history might initially cater to our geek sensibilities, it comes with definite drawbacks.

* Everything in the same database, on the same model means one less thing to worry about: VCS-based systems leave you to figure out a backup strategy for yet another persistence layer, as a good ol' database dump would not contain any history. In ``django-revisions``, all history lives in your database.
* While people may work on the same code simultaneously, people never write or edit stories simultaneously (and indeed you may want to prevent this from happening, using e.g. `django-locking <http://github.com/stdbrouw/django-locking>`_), rendering all the stuff that we love so much in version control systems (like branching, forking, merging and easily fixing conflicts) pointless. It's overkill.

Reading
=======

http://code.djangoproject.com/wiki/FullHistory
http://blog.brunogola.com.br/2009/10/django-model-history-with-django-reversion/
http://lethain.com/entry/2008/oct/15/choosing-between-audittrail-and-django-rcsfield/