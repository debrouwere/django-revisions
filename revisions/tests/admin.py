# encoding: utf-8

from django.contrib import admin
from revisions.tests import models
from revisions.admin import RevisionForm

class AsideInline(admin.TabularInline):
    model = models.Aside

class InfoInline(admin.TabularInline):
    model = models.Info

class StoryAdmin(admin.ModelAdmin):
    form = RevisionForm
    inlines = [AsideInline, InfoInline,]

admin.site.register(models.Story, StoryAdmin)
admin.site.register(models.FancyStory, StoryAdmin)
admin.site.register(models.TrashableStory)