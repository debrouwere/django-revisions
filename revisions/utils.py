# encoding: utf-8

# TODO: wil deze view ombouwen tot een generische decorator die oudere revisies
# of verkeerde urls kan laten doorverwijzen naar de juiste URL, enkel op basis
# van het model
#
# weet niet _hoe_ generisch ik dit kan krijgen (als men eerst transformaties wil toepassen
# op de inkomende argumenten, of men wil argumenten specifiëren bij get_absolute_url, of
# de urlresolver is verward... dan lukt het niet), maar 't is misschien wel 
# een 80% kind of solution
#
# ....
# pff, is toch echt niet generisch genoeg, misschien moet ik het opsplitsen in een paar
# functies die men naar goeddunken kan gebruiken in eigen views, eerder dan een decorator
# bv. een shortcut
#       confirm_canonical_or_redirect

def get_actual_url(obj):
    # REFACTOR: dit moet rechtstreekser de laatste revisie aanspreken, me dunkt
    # in het origineel staat er ook .get_absolute_url(printvriendelijk=printvriendelijk)
    # maar dat is misschien wel een heel moeilijke use-case om mee rekening te houden --
    # je geeft get_absolute_url normaliter geen argumenten mee en is misschien zelfs geen
    # best practice
    return obj.revisions.order_by('-vid')[0].get_absolute_url()

def is_actual_url(path, obj):
    actual_url = get_actual_url(obj)
    if path != actual_url:
        return False
    else:
        return True

"""
This resolver solves two problems: 

1. In the case where a url provides more information than is strictly necessary to fetch
   the object, multiple urls may lead to the same resource, which we should avoid
   e.g. if you only use the slug to fetch the object, both /2010/hello-world/ and
   /1972/hello-world/ would direct to the same resource, whereas the last URL
   should really redirect to the proper URL.
   
2. The URL for versioned content may change as e.g. its title changes, but we need
   to assure that people will still find the content. If we don't find what we're looking
   for among the latest revisions, we'll search through older ones and, if found, 
   redirect to the current url and the latest content.
"""

def view(maand, jaar, slug):
    Artikel.objects.filter(maand=maand, jaar=jaar, slug=slug)

def version_aware_resolver(view, model):
    """
    This version-aware resolver will catch requests for older versions
    of a piece of content, and redirects them to the latest version.
    It's meant specifically for detail pages (that is, pages that display
    a single object).
    
    Updating content can cause url slugs to change (e.g. the slug is based
    on a title field, and that title may get tweaked or edited around) 
    which in turn causes urls to break. This decorator is meant to 
    solve that issue by redirecting people who visit outdated urls, 
    instead of returning a 404.
    
    This resolver has a few important limitations to be aware of.
    * all arguments passed to the view have to be attributes
      on the model you want to display
    
    If it doesn't do what you want it to, you're probably best off
    tailoring it to your specific needs, using this code as inspiration.
    """
    # als we het artikel niet meteen terugvinden, zoeken we tussen 
    # slugs van oudere revisies van een artikel
    
    def new_view(*vargs, **kwargs):
        lookup = kwargs
    
        try:
            obj = model._default_manager.get(reqs)
        except model.DoesNotExist:
            # we try to find a matching model among older revisions;
            # if we don't find anything, we'll call a 404
            objs = model.objects.filter(reqs)
            
            if not len(objs):
                raise Http404
            else:
                obj = objs[0]
        
        if not is_actual_url(request.path, obj):
            redirect(obj)
        else:
            return view(obj, *vargs, **kwargs)
            
    return new_view