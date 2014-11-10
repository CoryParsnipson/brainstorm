from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.MainSiteView.index, name='index'),
    url(r'^dashboard', views.MainSiteView.dashboard, name='dashboard'),

    url(r'^ideas/show/(?P<idea_id>[0-9]+)', views.MainSiteView.idea_show, name='idea_show'),

    #url(r'^thoughts/list/', )
    url(r'^thoughts/in_idea/(?P<idea_id>[0-9]+)', views.MainSiteView.thoughts_in_idea, name='thoughts_in_idea'),
)
