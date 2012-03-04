from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover( )

urlpatterns = patterns( '',
    url( r'^', include( 'core.urls' ) ),
    url( r'^api/', include( 'api.urls' ) ),
    url( r'^admin/', include( admin.site.urls ) ),
    url( r'^profile/', include( 'profile.urls' ) ),

    url( r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'core/login.html'}, name='core.login' ),
    url( r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='core.logout' ),
)
