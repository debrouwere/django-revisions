# encoding: utf-8

# TODO: we hebben een klein stukje middleware nodig om in de admin
# te detecteren dat iemand een oude revisie probeert te editten (wat 
# een 404 oplevert) en door te verwijzen naar de laatste VID

# based on the FlatpageFallbackMiddleware

from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import resolve, reverse, Resolver404
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType
from revisions.models import VersionedModel

class VersionedModelRedirectMiddleware(object):
    def process_response(self, request, response):
        if response.status_code == 404:
            try:
                route = resolve(request.path_info)
            except Resolver404:
                return response
            
            if route[0].__name__  == 'change_view':
                # 1. figure out which model instance the request was for
                app, model, pk = request.path_info.rstrip('/').split('/')[-3:]
                cls = ContentType.objects.get(app_label=app, model=model).model_class()
                
                # 2. get the latest revision for that content
                if issubclass(cls, VersionedModel):
                    obj = cls.objects.get(pk=pk).get_latest_revision()
                    # 3. redirect
                    return redirect(reverse('admin:%s_%s_change' % (app, model), args=[obj.pk]))

        return response