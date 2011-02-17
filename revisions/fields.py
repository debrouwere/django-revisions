# encoding: utf-8

from django.db import models

# a pseudo-foreign key that supports referencing either the bundle or the individual revision
class ForeignKey(models.ForeignKey):
    def __init__(self):
        raise NotImplementedError()