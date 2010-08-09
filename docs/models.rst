Caveats when working with ``VersionedModel``
============================================

References to bundles or specific versions
------------------------------------------

A foreign key to a versioned object will always point to a specific
version and not the bundle as a whole.  Sometimes, however, it's useful to be able
to make a reference to the *bundle* and not a specific version.

To get the latest revision from a piece of versioned content you're accessing through
a reference from another model, simply use the ``get_latest_revision`` method.

Accessing related objects the other way around, across multiple revisions, is easy too.
Say you have an Author model that refers to a Story model. On instances, you can simply
use ``story.related_author_set`` (instead of ``story.author_set``) to access all authors
across versions and regardless of which specific version or versions an author is linked to.

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