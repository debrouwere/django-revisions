# encoding: utf-8

from django.db import models
from django.utils.translation import ugettext as _
from revisions import managers
import uuid
import difflib

class VersionedModel(models.Model):
    vid = models.AutoField(primary_key=True)
    id = models.CharField(max_length=36, editable=False, null=True, db_index=True)
    
    # managers
    latest = managers.LatestManager()
    objects = models.Manager()
    
    # all related revisions
    # it would be nice to be able to do obj.get_revisions().prev and .next as well, 
    # as added properties on the queryset object.
    def get_revisions(self):
        return self.__class__.objects.filter(id=self.id).order_by('vid')
    
    def check_if_latest_revision(self):
        return self.vid >= max([version.vid for version in self.get_revisions()])
    
    def revert_to(self, pk_or_instance):
        if isinstance(pk_or_instance, models.Model):
            pk = pk_or_instance.pk
        else:
            pk = pk_or_instance
    
        if pk in [version.pk for version in self.get_revisions()]:
            revert_to_obj = self.__class__.objects.get(pk=pk)
            revert_to_obj.save()
            return revert_to_obj
        else:
            # hmm, might not be the most descriptive of exceptions
            raise IndexError("Cannot revert to a primary key that is not part of the content bundle.")
    
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
            raise AttributeError

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
        objs = related_model._default_manager.filter(**{ref_name + '__in': self.get_revisions()})
        
        return objs
    
    # overriding getattr is tricky business, and should be extensively unit tested
    # to make sure we're not getting unexpected side-effects or get in the way of
    # existing Django magic
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
    
    # mleh, een generische oplossing voor de LoggedModel use-case zou wel interessant zijn
    # (dus velden die by default gecleared worden in de admin of als men
    # een prepare_for_change() methode aanroept, ipv. overgenomen van 
    # de vorige revisie) en een LoggedModel implementatie zou handig kunnen
    # zijn als voorbeeldcode (mss. zelfs gewoon in de documentatie)
    # maar lijkt me voor de rest toch iets te specifiek om nuttig te zijn
    def prepare_for_writing(self):
        """
        This method allows you to clear out certain fields in the model that are
        specific to each revision, like a log message.
        """
        
        clear_fields = getattr(self, 'clear_each_revision', False)
        if clear_fields:
            for field in clear_fields:
                super(VersionedModel, self).__setattr__(field, '')
    
    def save(self, new_revision=True, *vargs, **kwargs):
        # TODO: mensen duidelijk maken dat een wijzigingsdatum implementeren bij
        # versioned content ietsje anders moet, nl. dat je het best manueel doet
        # (hier evt. mee helpen met een methode daarvoor die men kan aanroepen, 
        # of een getter/setter voor wijzigingsdatum die men kan overriden waar
        # deze save-methode mee kan interageren, of een registratie-decorator
        # voor AOP)
        if new_revision:
            self.vid = None
        
        # The first revision of a piece of content won't have a bundle id yet, 
        # and because we haven't saved yet, there's no primary key either,
        # so we use a UUID as the bundle ID.
        #
        # (Note that Django chokes on using super/save() more than once 
        # in the save method, so doing a preliminary save to get the PK
        # and using that value for a bundle ID is sadly impossible.)
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

class TrashableModel(models.Model):
    """ Users wanting a version history may also expect a trash bin
    that allows them to recover deleted content, as is e.g. the
    case in WordPress. This is it. """
    
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