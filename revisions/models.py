# encoding: utf-8

import uuid
import difflib
from datetime import date
from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from revisions import managers
import inspect

class VersionedModel(models.Model):        
    @classmethod
    def get_implementations(cls):
        models = [contenttype.model_class() for contenttype in ContentType.objects.all()]
        return [model for model in models if isinstance(model, cls)]

    @property
    def _base_model(self):
        base = self
        while isinstance(base._meta.pk, models.OneToOneField):
            base = base._meta.pk.rel.to
        return base    

    @property
    def _base_table(self):
        return self._base_model._meta.db_table

    vid = models.AutoField(primary_key=True)
    id = models.CharField(max_length=36, editable=False, null=True, db_index=True)
    
    # managers
    latest = managers.LatestManager()
    objects = models.Manager()
    
    # all related revisions, plus easy shortcuts to the previous and next revision
    def get_revisions(self):
        qs = self.__class__.objects.filter(id=self.id).order_by('vid')
        
        try:
            qs.prev = qs.filter(vid__lt=self.vid).order_by('-vid')[0]
        except IndexError:
            qs.prev = None
        try:
            qs.next = qs.filter(vid__gt=self.vid)[0]
        except IndexError:
            qs.next = None
        
        return qs
    
    def check_if_latest_revision(self):
        return self.vid >= max([version.vid for version in self.get_revisions()])
    
    @classmethod
    def fetch(cls, criterion):
        if isinstance(criterion, int):
            return cls.objects.get(pk=criterion)
        elif isinstance(criterion, models.Model):
            return criterion
        elif isinstance(criterion, date):
            pub_date = cls.Versioning.publication_date
            if pub_date:
                return cls.objects.filter(**{pub_date + '__lte': criterion}).order('-vid')[0]
            else:
                raise ImproperlyConfigured("""Please specify which field counts as the publication
                    date for this model. You can do so inside a Versioning class. Read the docs 
                    for more info.""")
        else:
            raise TypeError("Can only fetch an object using a primary key, a date or a datetime object.")

    def revert_to(self, criterion):
        revert_to_obj = self.__class__.fetch(criterion)
    
        # You can only revert a model instance back to a previous instance.
        # Not any ol' object will do, and we check for that.
        if revert_to_obj.pk not in self.get_revisions().values_list('pk', flat=True):
            raise IndexError("Cannot revert to a primary key that is not part of the content bundle.")
        else:
            revert_to_obj.save()
            return revert_to_obj
            
    def get_latest_revision(self):
        return self.get_revisions().order_by('-vid')[0]
    
    def make_current_revision(self):
        if not self.check_if_latest_revision():
            self.save()

    def show_diff_to(self, to, field):
        frm = unicode(getattr(self, field)).split()
        to = unicode(getattr(to, field)).split()
        differ = difflib.HtmlDiff()
        return differ.make_table(frm, to)

    def _get_attribute_history(self, name):
        if self.__dict__.get(name, False):
            return [(version.__dict__[name], version) for version in self.get_revisions()]
        else:
            raise AttributeError(name)

    def _get_related_objects(self, relatedmanager):
        """ This method extends a regular related-manager by also including objects
        that are related to other versions of the same content, instead of just to
        this one object. """
        
        related_model = relatedmanager.model
        related_model_name = related_model._meta.module_name
        
        # The foreign key field name on related objects often, by convention,
        # coincides with the name of the class it relates to, but not always, 
        # e.g. you could do something like
        #   class Book(models.Model):
        #       thingmabob = models.ForeignKey(Author)
        #
        # There is, afaik, no elegant way to get a RelatedManager to tell us that
        # related objects refer to this class by 'thingmabob', leading to this
        # kind of convoluted deep dive into the internals of the related class.
        #
        # By all means, I'd welcome suggestions for prettier code.
        ref_name = self._meta._name_map[related_model_name][0].field.name
        pks = [story.pk for story in self.get_revisions()]        
        objs = related_model._default_manager.filter(**{ref_name + '__in': pks})
        
        return objs
    
    def __getattr__(self, name):
        # we catch all lookups that start with 'related_'
        if name.startswith('related_'):
            related_name = "_".join(name.split("_")[1:])
            attribute = getattr(self, related_name, False)
            # we piggyback off of an existing relationship,
            # so the attribute has to exist and it has to be a 
            # RelatedManager or ManyRelatedManager
            if attribute:
                # (we check the module instead of using isinstance, since 
                # ManyRelatedManager is created using a factory so doesn't
                # actually exist inside of the module)
                if attribute.__class__.__dict__['__module__'] == 'django.db.models.fields.related':
                    return self._get_related_objects(attribute)

        if name.endswith('_history'):
            attribute = name.replace('_history', '')
            return self._get_attribute_history(attribute)

        raise AttributeError(name)
            
    def prepare_for_writing(self):
        """
        This method allows you to clear out certain fields in the model that are
        specific to each revision, like a log message.
        """
        for field in self.Versioning.clear_each_revision:
            super(VersionedModel, self).__setattr__(field, '')
    
    def save(self, new_revision=True, *vargs, **kwargs):
        # If we set the primary key (vid) to None, Django is smart
        # enough to save a new revision for us, instead of updating
        # the existing one.
        # 
        # We don't make a new revision for small changes.
        if new_revision and not getattr(self, 'is_small_change', False):
            # little known Django implementation detail: 
            # to clone a model in cases of concrete inheritance, you must
            # set both the self.pk reference and the actual primary key
            # to None
            self.pk = self.vid = None
        
        # The first revision of a piece of content won't have a bundle id yet, 
        # and because the object isn't persisted in the database, there's no 
        # primary key either, so we use a UUID as the bundle ID.
        # 
        # (Note for smart alecks: Django chokes on using super/save() more than
        # once in the save method, so doing a preliminary save to get the PK
        # and using that value for a bundle ID is rather hard.)
        if not self.id:
            self.id = uuid.uuid4().hex
        
        super(VersionedModel, self).save(*vargs, **kwargs)
        
    def delete_revision(self, *vargs, **kwargs):
        super(VersionedModel, self).delete(*vargs, **kwargs)
    
    def delete(self, *vargs, **kwargs):
        for revision in self.get_revisions():
            revision.delete_revision(*vargs, **kwargs)
    
    class Meta:
        abstract = True
    
    class Versioning:
        clear_each_revision = []
        publication_date = None

class TrashableModel(models.Model):
    """ Users wanting a version history may also expect a trash bin
    that allows them to recover deleted content, as is e.g. the
    case in WordPress. This is that thing. """
    
    _is_trash = models.BooleanField(db_column='is_trash', default=False, editable=False)
    
    @property
    def is_trash(self):
        return self._is_trash
    
    def get_content_bundle(self):
        if isinstance(self, VersionedModel):
            return self.get_revisions()
        else:
            return [self]        
    
    def delete(self):
        """
        It makes no sense to trash individual revisions: either you keep a version history or you don't.
        If you want to undo a revision, you should use obj.revert_to(preferred_revision) instead.
        """
        for obj in self.get_content_bundle():
            obj._is_trash = True
            if isinstance(obj, VersionedModel):
                obj.save(new_revision=False)
            else:
                obj.save()
    
    def delete_permanently(self):
        for obj in self.get_content_bundle():
            super(TrashableModel, obj).delete()
    
    class Meta:
        abstract = True