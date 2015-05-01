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
    url(r'^about/', views.about, name='about'),
    url(r'^books/', views.books, name='books'),
    url(r'^highlights/', views.highlights, name='highlights'),
    url(r'^ideas/$', views.ideas, name='catalog'),
    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/$', views.idea_detail, name='idea-page'),
    url(r'^ideas/(?P<idea_slug>[a-z0-9\-]+)/(?P<thought_slug>[a-z0-9\-]+)/', views.thought_detail, name='thought-page'),

    # dashboard urls, admin only!
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/books/$', views.dashboard_books, name='dashboard-books'),
    url(r'^dashboard/highlights/$', views.dashboard_highlights, name='dashboard-highlights'),
    url(r'^dashboard/tasks/$', views.dashboard_todo, name='dashboard-todo'),
    url(r'^dashboard/notes/$', views.dashboard_notes, name='dashboard-notes'),
    url(r'^dashboard/ideas/$', views.dashboard_ideas, name='dashboard-ideas'),
    url(r'^dashboard/thoughts/$', views.dashboard_thoughts, name='dashboard-thoughts'),
    url(r'^dashboard/author/$', views.dashboard_author, name='dashboard-author'),
    url(r'^dashboard/drafts/$', views.dashboard_drafts, name='dashboard-drafts'),
    url(r'^dashboard/trash/$', views.dashboard_trash, name='dashboard-trash'),
    url(r'^dashboard/backend/$', views.dashboard_backend, name='dashboard-backend'),

    # site api
    url(r'^api/login/', views.login, name='login'),
    url(r'^api/logout/', views.logout, name='logout'),
    url(r'^api/upload/', views.upload, name='upload'),
    url(r'^api/generate_upload_filename(?P<full_path>(\/full)?)/(?P<filename>.*)', views.generate_upload_filename, name='generate-upload-filename'),
    url(r'^api/search_aws/(?P<keywords>.*)', views.search_aws, name='search-aws'),

    url(r'^api/forms/idea/', views.FormIdeaView.as_view(), name='forms-idea'),
    url(r'^api/forms/thought/', views.FormThoughtView.as_view(), name='forms-thought'),
    url(r'^api/forms/highlight/', views.FormHighlightView.as_view(), name='forms-highlight'),
    url(r'^api/forms/readinglistitem/', views.FormReadingListView.as_view(), name='forms-readinglistitem'),
    url(r'^api/forms/task/$', views.FormTaskView.as_view(), name='forms-task'),
    url(r'^api/forms/task/(?P<id>[0-9]+)/mark', views.FormTaskView.mark_complete, name='forms-task-mark'),
    url(r'^api/forms/task/(?P<id>[0-9]+)/priority/(?P<priority>[0-9]+)', views.FormTaskView.change_priority, name='forms-task-priority'),
    url(r'^api/forms/task/(?P<id>[0-9]+)/delete', views.FormTaskView.delete, name='forms-task-delete'),
    url(r'^api/forms/note/$', views.FormNoteView.as_view(), name='forms-note'),
    url(r'^api/forms/note/(?P<id>[0-9]+)/associate_idea/(?P<idea_slug>[a-z0-9\-]+)', views.FormNoteView.add_idea, name='forms-note-associate-idea'),
    url(r'^api/forms/note/(?P<id>[0-9]+)/associate_thought/(?P<thought_slug>[a-z0-9\-]+)', views.FormNoteView.add_thought, name='forms-note-associate-thought'),
)

# setup serving of media asserts on development environment
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)