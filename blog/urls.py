from django.conf.urls import patterns, include, url

from rest_framework import routers

from . import views

# Use DRF router for RESTful API url generation
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'ideas', views.IdeaViewSet)
router.register(r'thoughts', views.ThoughtViewSet)

urlpatterns = patterns('',
    # index url
    url(r'^$', views.MainSiteView.index, name='index'),

    # site skeleton urls
    url(r'^dashboard', views.MainSiteView.dashboard, name='dashboard'),

    url(r'^ideas/(?P<idea_id>[0-9]+)', views.MainSiteView.idea_detail, name='idea_detail'),

    # RESTful api urls (it is very important that this app has no namespace...)
    url(r'^api/', include(router.urls)),

    url(r'^api/forms/ideas/', views.FormIdeaView.as_view(), name='forms-ideas'),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
