from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework import routers

from blog import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'ideas', views.IdeaViewSet)
router.register(r'thoughts', views.ThoughtViewSet)

urlpatterns = patterns('',
    url(r'^', include('blog.urls', namespace='blog')),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
