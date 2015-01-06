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
        fields = ['name', 'slug', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 1,
                'cols': 40,
            }),
        }


class ThoughtForm(forms.ModelForm):
    """ Django form class for managing thoughts
    """
    class Meta:
        model = Thought
        fields = ['title', 'slug', 'content', 'idea', 'author']
        widgets = {
            # tinymce textarea (when js is enabled)
            'content': forms.Textarea(attrs={
                'id': 'thought-editor',
                'class': 'editor',
            })
        }

    #def clean_content(self):
    #    data = self.cleaned_data['content']
    #    return data