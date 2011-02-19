# encoding: utf-8

try:
    from django_extensions.db.fields import CreationDateTimeField
except:
    CreationDateTimeField = ImportError

# Since Django 1.2, a simple copy.copy(model) w/ pk = None stopped working.
class ClonableMixin(object):
    def clone(self):    
        duplicate = self.__class__()
        for field in self._meta.fields:
            pk = field.primary_key
            comparator = (field.name is self.comparator_name)
            # people expect these fields to work per-bundle, not per-revision, 
            # so we'll overwrite these values with the old ones
            auto_field = \
                isinstance(field, CreationDateTimeField) or \
                getattr(field, 'auto_now_add', False)

            if not (pk or auto_field or comparator):
                value = getattr(self, field.name)
                setattr(duplicate, field.name, value)
        
        duplicate.save()
        
        # ... but the trick loses all ManyToMany relations.
        for field in self._meta.many_to_many:
            source = getattr(self, field.attname)
            destination = getattr(duplicate, field.attname)
            for item in source.all():
                destination.add(item)

        return duplicate