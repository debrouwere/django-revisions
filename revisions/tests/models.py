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

    clear_each_revision = ['title', 'slug']

    class Meta:
        verbose_name_plural = 'stories'

class ConvenientStory(Story, shortcuts.VersionedModel):
    class Meta:
        proxy = True

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
    # dit dient om synchrone versioning te testen
    message = models.CharField(max_length=250)
    story = models.ForeignKey(Story) 

class Info(models.Model):
    # dit om een gewoon gerelateerd model te testen
    content = models.CharField(max_length=250)
    story = models.ForeignKey(Story)

"""
class LoggedModel(models.Model):
    log_message = models.TextField(_('Log message'), 
        help_text = _('Leave a short message to describe your edit.'),
        blank=True)

    @property
    def log_messages(self):
        return [message[0] for message in self.log_message_history]
    
    # TODO: log_message en deze property in een apart
    # submodel steken (ook abstract) + een concrete instantiatie
    # die gebruikt kan worden om deze functionaliteit te unit testen.

    class Meta:
        abstract = True

class LoggedVersionedModel(VersionedModel, LoggedModel):
    class Meta:
        abstract = True
"""