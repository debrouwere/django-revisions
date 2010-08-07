from django.contrib import admin
from revisions.managers import LatestManager
from django import forms

class RevisionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClearableForm, self).__init__(*args, **kwargs)
        
        clear_fields = getattr(self.instance, 'version_specific_fields', list())
        
        for field in clear_fields:
            self.initial[field] = ''