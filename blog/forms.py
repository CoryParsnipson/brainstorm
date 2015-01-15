from django import forms

from blog.models import Idea, Thought


class LoginForm(forms.Form):
    """ Create a login form with username and password fields.
    """
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class IdeaForm(forms.ModelForm):
    """ Django form class for managing user interaction with Idea objects
    """
    def __init__(self, *args, **kwargs):
        super(IdeaForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Idea
        fields = ['name', 'slug', 'description', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 1,
                'cols': 40,
            }),
            'icon': forms.FileInput(),
        }


class ThoughtForm(forms.ModelForm):
    """ Django form class for managing thoughts
    """
    class Meta:
        model = Thought
        fields = ['title', 'slug', 'content', 'idea', 'author', 'is_draft', 'is_trash', 'preview']
        widgets = {
            # tinymce textarea (when js is enabled)
            'content': forms.Textarea(attrs={
                'id': 'thought-editor',
                'class': 'editor',
            }),
        }