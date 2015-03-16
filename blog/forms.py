from django import forms
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.admin import User

from blog.models import Idea, Thought, Highlight, ReadingListItem


class LoginForm(forms.Form):
    """ Create a login form with username and password fields.
    """
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class IdeaForm(forms.ModelForm):
    """ Django form class for managing user interaction with Idea objects
    """
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
    is_draft = forms.CharField(widget=forms.HiddenInput,
                               initial=Thought._meta.get_field_by_name('is_draft')[0].get_default())
    is_trash = forms.CharField(widget=forms.HiddenInput,
                               initial=Thought._meta.get_field_by_name('is_trash')[0].get_default())

    # fields for tinymce parameters
    upload_url = forms.CharField(widget=forms.HiddenInput(attrs={
        'value': reverse_lazy('upload')
    }))
    filename_url = forms.CharField(widget=forms.HiddenInput(attrs={
        'value': reverse_lazy('generate-upload-filename', kwargs={
            'full_path': '/full',
            'filename': '',
        })
    }))

    class Meta:
        model = Thought
        fields = ['title', 'slug', 'author', 'content', 'idea', 'preview', 'is_draft', 'is_trash']
        widgets = {
            # tinymce textarea (when js is enabled)
            'content': forms.Textarea(attrs={
                'class': 'editor',
            }),
        }


class HighlightForm(forms.ModelForm):
    """ Django form class for managing Highlights
    """
    id = forms.IntegerField(widget=forms.HiddenInput)

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

    class Meta:
        model = ReadingListItem
        fields = '__all__'