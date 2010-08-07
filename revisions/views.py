from django.views.generic import direct_to_template

def differ(request, compare_baseline_pk, compare_with_pk):
    raise NotImplementedError

def trash_can(request, model=None):
    if not model:
        pass
        # als er geen model werd opgegeven, 
        # alle modellen zoeken die inheriten van VersionedModel
    else:
        pass
    
    raise NotImplementedError