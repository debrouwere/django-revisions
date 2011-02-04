Caveats when working with ``VersionedModel``
============================================

References to bundles or specific versions
------------------------------------------

A foreign key to a versioned object will always point to a specific
version and not the bundle as a whole.  Sometimes, however, it's useful to be able
to have a reference to the *bundle* and not a specific version — every revision of "client"
that's tied to a "project", say.

Provided you're accessing a piece of versioned content through a reference from another
model, you can get the latest revision of that reference with the ``get_latest_revision`` method.

The other way around is easy too. Say you have an Author model that refers to a versioned Story
model. On instances, you can simply use ``story.related_author_set`` (instead of ``story.author_set``)
to access all authors across versions and regardless of which specific version or versions an 
author is linked to.

A side note: why you shouldn't use Django's to_field to reference content bundles
---------------------------------------------------------------------------------

In Django 1.0 you used to be able to abuse foreign keys to allow for
pseudo-foreign key references to a *bundle* instead of a specific version.

class Instructions(models.Model):
    # dit om een model te testen gerelateerd aan de bundel
    story = models.ForeignKey(Story, to_field='id')

Because ``VersionedModel.latest`` is the default manager for versioned content, 
such a foreign key attribute would then return the latest revision of the bundle
even though the bundle id field is shared among revisions.

However, in Django 1.2, this no longer works, because foreign keys should by their
very nature only reference unique fields. See 
http://groups.google.com/group/django-users/browse_thread/thread/fcd3915a19ae333e
and 
http://code.djangoproject.com/ticket/11702
for more information.

Adding your own managers
------------------------

If you add your own managers to an object, make sure to add revisions.managers.LatestManager()
back in, preferably as the first and thus default manager. You'll probably also want to 
add django.db.managers.Manager() back in, as `objects`.