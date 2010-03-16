from django.conf.urls.defaults import *

from satchmo_store.urls import urlpatterns

from django.conf import settings
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

