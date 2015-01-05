from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from rest_framework import routers

from . import views

# Use DRF router for RESTful API url generation
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'ideas', views.IdeaViewSet)
router.register(r'thoughts', views.ThoughtViewSet)

urlpatterns = patterns('',
    # favicon
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),

    # site skeleton urls
    url(r'^$', views.index, name='index'),

    url(r'^login/', views.login_page, name='login_page'),
    url(r'^logout/', views.logout_page, name='logout_page'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/ideas/$', views.dashboard_ideas, name='dashboard-ideas'),
    url(r'^dashboard/ideas/backend/$', views.dashboard_ideas_backend, name='dashboard-ideas-backend'),
    url(r'^dashboard/manage/thought/$', views.dashboard_manage_thought, name='dashboard-manage-thought'),

    url(r'^about/', views.about, name='about'),
    url(r'^ideas/$', views.ideas, name='idea_list'),
    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/$', views.idea_detail, name='idea_detail'),

    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/(?P<thought_slug>[a-z0-9\-]+)/', views.thought_detail, name='thought_detail'),

    # RESTful api urls (it is very important that this app has no namespace...)
    url(r'^api/', include(router.urls)),

    url(r'^api/login/', views.login, name='login'),
    url(r'^api/logout/', views.logout, name='logout'),

    url(r'^api/docs/', include('rest_framework_swagger.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/forms/idea/', views.FormIdeaView.as_view(), name='forms-idea'),
    url(r'^api/forms/thought/', views.FormThoughtView.as_view(), name='forms-thought'),

)
