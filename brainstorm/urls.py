from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework import routers

from blog import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'brainstorm.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include(router.urls)),
    #url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
)
