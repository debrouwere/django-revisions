from django.db import models
from revisions.models import VersionedModelBase, VersionedModel, TrashableModel
from revisions import shortcuts
from django.template.defaultfilters import slugify
from revisions import managers
from django_extensions.db.fields import UUIDField

class Story(VersionedModel):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    body = models.TextField(blank=True)

    def save(self, *vargs, **kwargs):
        self.slug = slugify(self.title)
        super(Story, self).save(*vargs, **kwargs)
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'stories'
    
    class Versioning:
        clear_each_revision = ['title', 'slug']
        publication_date = None

class ManualStory(VersionedModelBase):
    alt_id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    body = models.TextField(blank=True)

    def save(self, *vargs, **kwargs):
        self.slug = slugify(self.title)
        super(ManualStory, self).save(*vargs, **kwargs)
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'manual stories'
    
    class Versioning:
        clear_each_revision = ['title', 'slug']
        publication_date = None

class UUIDStory(VersionedModelBase):
    alt_id = UUIDField(primary_key=True)

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    body = models.TextField(blank=True)
    changed = models.DateTimeField(auto_now=True)

    def save(self, *vargs, **kwargs):
        self.slug = slugify(self.title)
        super(UUIDStory, self).save(*vargs, **kwargs)
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'uuid-based stories'
    
    class Versioning:
        clear_each_revision = ['title', 'slug']
        publication_date = None
        comparator = 'changed'

class UniqueStory(VersionedModel):
    class Meta:
        verbose_name_plural = 'unique stories'
        unique_together = ("title", "body", )

    class Versioning:
        unique = ("body", )
        unique_together = ("title", "slug", )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    body = models.TextField(blank=True)

    def save(self, *vargs, **kwargs):
        self.slug = slugify(self.title)
        super(UniqueStory, self).save(*vargs, **kwargs)
        
    def __unicode__(self):
        return self.title

class FancyStory(Story):
    is_very_fancy = models.BooleanField(default=True)

class FancyManualStory(ManualStory):
    is_very_fancy = models.BooleanField(default=True)

class ConvenientStory(Story, shortcuts.VersionedModelShortcuts):
    class Meta:
        proxy = True

@managers.trash_aware
class TrashableStory(VersionedModel, TrashableModel):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    body = models.TextField(blank=True)

    def save(self, *vargs, **kwargs):
        self.slug = slugify(self.title)
        super(TrashableStory, self).save(*vargs, **kwargs)
        
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'trashable stories'

# this model allows us to test whether the trash system works nicely in tandem
# with revisions together with concrete inheritance
@managers.trash_aware
class FancyTrashableStory(TrashableStory):
    is_very_fancy = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'trashable stories'

class Aside(VersionedModel):
    # serves to test synchronous versioning
    message = models.CharField(max_length=250)
    story = models.ForeignKey(Story) 

class Info(models.Model):
    # serves to test related but unversioned objects
    content = models.CharField(max_length=250)
    story = models.ForeignKey(Story)

class InfoToBundle(models.Model):
    # serves to test FKs to a bundle
    content = models.CharField(max_length=250)
    #story = models.ForeignKey(Story, to_field='cid')