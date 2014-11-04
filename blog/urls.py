from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.MainSiteView.index, name='index'),
    url(r'^dashboard', views.MainSiteView.dashboard, name='dashboard'),
)
