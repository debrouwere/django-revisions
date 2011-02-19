# encoding: utf-8

"""
To make sure ``django-versioning`` works smoothly with the admin interface, you should add ``revisions.middleware.VersionedModelRedirectMiddleware`` to your middlewares in ``settings.py``, e.g.::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'revisions.middleware.VersionedModelRedirectMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )
    
To enable versioning in the admin, subclass from revisions.admin.VersionedAdmin instead of from django.admin.ModelAdmin. By default, this class has ``revisions.admin.AutoRevisionForm`` as its form, but you're not tied to this ModelForm: 

* AutoRevisionForm makes sure to clear any revision-specific fields, like log messages. Since these are tied to each individual revision, revision-specific fields should be empty upon each new edit.
* RevisionForm inherits from AutoRevisionForm, but adds a checkbox to the form that allows users to specify they only want to make a small change, and that we ought to save it in-place rather than creating a new revision.
* If you need neither, feel free to use a regular ModelForm instead.

Specify fields that need to be cleared as a list of attribute names like so::

    class MyModel(VersionedModel):
        class Versioning:
            clear_each_revision = ['log_message', 'codename', ]

When in doubt, don't specify your own form and stick to the default: the AutoRevisionForm.
"""

from django.contrib import admin
from revisions.managers import LatestManager
from django import forms

class AutoRevisionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AutoRevisionForm, self).__init__(*args, **kwargs)
        
        for field in self.instance.Versioning.clear_each_revision:
            self.initial[field] = ''

class RevisionForm(AutoRevisionForm):
    small_change = forms.BooleanField(initial=False, 
        help_text="Fixed a typo, changed a couple of words. (Doesn't create a new revision)",
        required=False)

    def clean(self):
        self.instance.is_small_change = self.cleaned_data.get('small_change', False)
        del self.fields['small_change']
        del self.cleaned_data['small_change']
        return self.cleaned_data

class VersionedAdmin(admin.ModelAdmin):
    form = AutoRevisionForm
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.revise()