from django import forms
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.admin import User

from blog.models import Idea, Thought, Highlight, ReadingListItem, Task


class LoginForm(forms.Form):
    """ Create a login form with username and password fields.
    """
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class IdeaForm(forms.ModelForm):
    """ Django form class for managing user interaction with Idea objects
    """
    next = forms.CharField(widget=forms.HiddenInput, initial=reverse_lazy('dashboard-ideas'))

    def __init__(self, *args, **kwargs):
        super(IdeaForm, self).__init__(*args, **kwargs)

        if Idea.objects.filter(slug=self.instance.slug).exists():
            # add edit field if instance data is provided
            self.fields['edit'] = forms.CharField(widget=forms.HiddenInput, initial=self.instance.slug)

    class Meta:
        model = Idea
        fields = ['name', 'slug', 'description', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 1,
                'cols': 40,
            }),
        }


class ThoughtForm(forms.ModelForm):
    """ Django form class for managing thoughts
    """
    # predefined fields
    author = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)

    # fields for tinymce parameters
    upload_url = forms.CharField(widget=forms.HiddenInput(attrs={
        'value': reverse_lazy('upload')
    }))
    filename_url = forms.CharField(widget=forms.HiddenInput(attrs={
        'value': reverse_lazy('generate-upload-filename', kwargs={'full_path': '/full', 'filename': ''})
    }))

    def __init__(self, *args, **kwargs):
        super(ThoughtForm, self).__init__(*args, **kwargs)

        # calculate next url
        next_url = reverse_lazy('dashboard-thoughts') + "?id={idea}"
        self.fields['next'] = forms.CharField(widget=forms.HiddenInput, required=False, initial=next_url)

        if Thought.objects.filter(slug=self.instance.slug).exists():
            # add edit field if instance data is provided
            self.fields['edit'] = forms.CharField(widget=forms.HiddenInput, initial=self.instance.slug)

    class Meta:
        model = Thought
        fields = ['title', 'slug', 'author', 'content', 'idea', 'preview', 'is_draft']
        widgets = {
            # tinymce textarea (when js is enabled)
            'content': forms.Textarea(attrs={
                'class': 'editor',
            }),
            'slug': forms.TextInput(attrs={
               'class': 'no-text-overflow'
            }),
        }


class HighlightForm(forms.ModelForm):
    """ Django form class for managing Highlights
    """
    id = forms.IntegerField(widget=forms.HiddenInput)
    next = forms.CharField(widget=forms.HiddenInput, initial=reverse_lazy('dashboard-highlights'))

    class Meta:
        model = Highlight
        fields = ['id', 'title', 'description', 'url', 'icon']
        widgets = {
            # tinymce textarea (when js is enabled)
            'description': forms.Textarea(attrs={
                'class': 'editor',
            }),
        }


class ReadingListItemForm(forms.ModelForm):
    """ Django form class for managing ReadingListItems
    """
    id = forms.IntegerField(widget=forms.HiddenInput)
    next = forms.CharField(widget=forms.HiddenInput, initial=reverse_lazy('dashboard-books'))

    class Meta:
        model = ReadingListItem
        fields = '__all__'


class TaskForm(forms.ModelForm):
    """ task form class
    """
    id = forms.IntegerField(widget=forms.HiddenInput)
    next = forms.CharField(widget=forms.HiddenInput, initial=reverse_lazy('dashboard-todo'))

    # disable multi-level nesting of Tasks
    parent_task = forms.ModelChoiceField(
        queryset=Task.objects.filter(parent_task__isnull=True).order_by("-priority", "-date_added"),
        widget=forms.Select(),
        required=False,
    )

    class Meta:
        model = Task
        fields = ['id', 'parent_task', 'idea', 'content', 'priority']