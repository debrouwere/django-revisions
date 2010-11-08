from django.views.generic import direct_to_template
from revisions.models import VersionedModel

def differ(request, compare_baseline_pk, compare_with_pk):
    raise NotImplementedError

def trashcan(request, model=None):
    if not model:
        models = VersionedModel.get_implementations()
    else:
        models = [model]
    
    raise NotImplementedError