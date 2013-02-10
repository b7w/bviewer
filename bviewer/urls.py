from django.conf.urls import patterns, include, url
from django.contrib import admin
import djcelery


admin.autodiscover()
djcelery.setup_loader()

urlpatterns = patterns('',
    url(r'^', include('bviewer.core.urls')),
    url(r'^', include('bviewer.archive.urls')),
    url(r'^api/', include('bviewer.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', include('bviewer.profile.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'core/login.html'}, name='core.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='core.logout'),
)
