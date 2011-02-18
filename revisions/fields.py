# encoding: utf-8

from django.db import models

"""
1. Shouldn't trigger a django.core.management.validation error (which is tricky because it 
   doesn't check if the field is actually a regular ForeignKey, it just checks if it has a
   ``rel`` attribute.
2. Shouldn't add a true FK to databases that support it (that is, anything other than MySQL 
   and SQLite), but treat the foreign key as a regular integerfield/charfield that just
   happens to be a reference.
"""

# a pseudo-foreign key that supports referencing either the bundle or the individual revision
class ForeignKey(models.ForeignKey):
    def __init__(self):
        raise NotImplementedError()