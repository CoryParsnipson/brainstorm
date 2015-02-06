from django.conf import settings
from django.conf.urls.static import static
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

    url(r'^login/', views.login_page, name='login-page'),
    url(r'^logout/', views.logout_page, name='logout-page'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/ideas/$', views.dashboard_ideas, name='dashboard-ideas'),
    url(r'^dashboard/thoughts/$', views.dashboard_thoughts, name='dashboard-thoughts'),
    url(r'^dashboard/author/$', views.dashboard_author, name='dashboard-author'),
    url(r'^dashboard/drafts/$', views.dashboard_drafts, name='dashboard-drafts'),
    url(r'^dashboard/trash/$', views.dashboard_trash, name='dashboard-trash'),
    url(r'^dashboard/backend/$', views.dashboard_backend, name='dashboard-backend'),

    url(r'^about/', views.about, name='about'),
    url(r'^ideas/$', views.ideas, name='idea-catalog-page'),
    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/$', views.idea_detail, name='idea-page'),

    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/(?P<thought_slug>[a-z0-9\-]+)/', views.thought_detail, name='thought-page'),

    # RESTful api urls (it is very important that this app has no namespace...)
    url(r'^api/', include(router.urls)),

    # not part of DRF, but part of API, see views.py "Miscellaneous API"
    url(r'^api/login/', views.login, name='login'),
    url(r'^api/logout/', views.logout, name='logout'),
    url(r'^api/upload/', views.upload, name='upload'),

    url(r'^api/docs/', include('rest_framework_swagger.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/forms/idea/', views.FormIdeaView.as_view(), name='forms-idea'),
    url(r'^api/forms/thought/', views.FormThoughtView.as_view(), name='forms-thought'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)