# encoding: utf-8

from datetime import datetime
from django.db import models
import inspect


def get_table_for_field(model, field_name):
    for field in model._meta.fields:
        if field_name == field.attname:
            return field.model._meta.db_table
    return None


class LatestQuerySet(models.query.QuerySet):
    # not too nice performance-wise, but the easiest solution
    # to make counts play nice with revisions
    def count(self):
        return len(list(self.iterator()))
        

class LatestManager(models.Manager):
    """ A manager that returns the latest revision of each bundle of content. """

    @property
    def current(self):
        qs = LatestQuerySet(self.model, using=self._db)
    
        # in case of concrete inheritance, we need the base table, not the leaf
        base = qs.query.model.get_base_model()
        base_table = base._meta.db_table

        # this may or may not be the fastest way to get the last revision of every
        # piece of content, depending on how your database query optimizer works, 
        # but it sure as hell is the easiest way to do it in Django without resorting
        # to multiple queries or working entirely with raw SQL.
        comparator_name = base.get_comparator_name()  
        comparator_table = get_table_for_field(qs.query.model, comparator_name)
        where = '{comparator_table}.{comparator} = (SELECT MAX({comparator}) FROM {table} as sub WHERE {table}.cid = sub.cid)'.format(
            table=base_table,
            comparator=comparator_name,
            comparator_table=comparator_table)
        
        qs = qs.extra(where=[where])
        return qs

    def get_query_set(self):              
        # Django uses the default manager (which on versioned models is this one)
        # to determine what to do when it saves a model instance. Because older
        # revisions aren't included in the queryset for LatestManager, when trying
        # to update such an older revision, the ORM gets confused and tries to insert 
        # a new record, or, when you pass force_update=True, Django complains that it 
        # couldn't find the right row to update.
        #
        # Specifically, you either get an IntegrityError saying "PRIMARY KEY must be unique" 
        # or a DatabaseError saying "Forced update did not affect any rows."
        #
        # We solve this little issue by simply using the plain models.Manager queryset
        # when saving. Simple fix, but it does require some trickery with the inspect
        # module and it does make this module prone to breakage whenever a new Django
        # version comes out.
        #
        # revisions.tests.AppTests.test_update_old_revision_in_place tests whether this works.
        #
        # The Django team advises against using a manager that filters out rows as the default one:
        # http://docs.djangoproject.com/en/dev/topics/db/managers/#do-not-filter-away-any-results-in-this-type-of-manager-subclass
        # ... but we feel that versioning should be an absolutely transparant concern, 
        # and work on related resources and in the admin without any fuss, leading us
        # to waive this concern.
   
        stack = inspect.stack()[3][3]
        # * 'save' for saving for plain models
        # * 'save_base' for saving models with inheritance
        # * '_collect_sub_objects' for deleting models with inheritance (Django 1.2)
        # * 'collect' for deleting models with inheritance (Django 1.3)
        if stack.startswith('save') or stack == 'collect' or stack == '_collect_sub_objects':
            return super(LatestManager, self).get_query_set()
        else:
            return self.current
            
    
def trash_aware(cls):
    for manager in cls._meta.abstract_managers:
        manager[2].trash = manager[2].filter(_is_trash=True)
        manager[2].live = manager[2].filter(_is_trash=False)
    return cls