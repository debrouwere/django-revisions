from django.db import models
from revisions.models import VersionedModel, TrashableModel
from revisions import shortcuts
from django.template.defaultfilters import slugify
from revisions import managers

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

class ConvenientStory(Story, shortcuts.VersionedModel):
    class Meta:
        proxy = True

class FancyStory(Story):
    is_very_fancy = models.BooleanField(default=True)

"""
# this model allows us to test whether the versioning system also works
# with inheritance (joined tables) as well as the TrashableModel functionality.

class TrashableStory(Story, TrashableModel):
    class Meta:
        verbose_name_plural = 'trashable stories'

... laat ons voorlopig 'ns enkel trashable proberen
"""	

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

class Aside(VersionedModel):
    # serves to test synchronous versioning
    message = models.CharField(max_length=250)
    story = models.ForeignKey(Story) 

class Info(models.Model):
    # serves to test related but unversioned objects
    content = models.CharField(max_length=250)
    story = models.ForeignKey(Story)