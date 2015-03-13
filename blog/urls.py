from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = patterns('',
    # favicon
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),

    # site skeleton urls
    url(r'^$', views.index, name='index'),

    url(r'^login/', views.login_page, name='login-page'),
    url(r'^logout/', views.logout_page, name='logout-page'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/books/$', views.dashboard_books, name='dashboard-books'),
    url(r'^dashboard/highlights/$', views.dashboard_highlights, name='dashboard-highlights'),
    url(r'^dashboard/ideas/$', views.dashboard_ideas, name='dashboard-ideas'),
    url(r'^dashboard/thoughts/$', views.dashboard_thoughts, name='dashboard-thoughts'),
    url(r'^dashboard/author/$', views.dashboard_author, name='dashboard-author'),
    url(r'^dashboard/drafts/$', views.dashboard_drafts, name='dashboard-drafts'),
    url(r'^dashboard/trash/$', views.dashboard_trash, name='dashboard-trash'),
    url(r'^dashboard/backend/$', views.dashboard_backend, name='dashboard-backend'),

    url(r'^about/', views.about, name='about'),
    url(r'^books/', views.books, name='books'),
    url(r'^highlights/', views.highlights, name='highlights'),
    url(r'^ideas/$', views.ideas, name='idea-catalog-page'),
    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/$', views.idea_detail, name='idea-page'),

    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/(?P<thought_slug>[a-z0-9\-]+)/', views.thought_detail, name='thought-page'),

    url(r'^api/login/', views.login, name='login'),
    url(r'^api/logout/', views.logout, name='logout'),
    url(r'^api/upload/', views.upload, name='upload'),
    url(r'^api/generate_upload_filename(?P<full_path>(\/full)?)/(?P<filename>.*)', views.generate_upload_filename, name='generate-upload-filename'),
    url(r'^api/search_aws/(?P<keywords>.*)', views.search_aws, name='search-aws'),

    url(r'^api/forms/idea/', views.FormIdeaView.as_view(), name='forms-idea'),
    url(r'^api/forms/thought/', views.FormThoughtView.as_view(), name='forms-thought'),
    url(r'^api/forms/highlight/', views.FormHighlightView.as_view(), name='forms-highlight'),
    url(r'^api/forms/readinglistitem/', views.FormReadingListView.as_view(), name='forms-readinglistitem'),
)

# setup serving of media asserts on development environment
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)