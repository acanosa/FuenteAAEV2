from django.conf.urls import patterns, include, url
from django.contrib import admin
import settings 

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aaev2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^static/aaev/imagenes/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^aaev/', include('aaev.urls', namespace='aaev')),  #mis url de la app
    #declaro un namespace para evitar lio al llamar URLs

)
