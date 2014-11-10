from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.MainSiteView.index, name='index'),
    url(r'^dashboard', views.MainSiteView.dashboard, name='dashboard'),

    url(r'^ideas/(?P<idea_id>[0-9]+)', views.MainSiteView.idea_detail, name='idea_detail'),
)
