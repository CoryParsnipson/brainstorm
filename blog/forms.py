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
    class Meta:
        model = Idea
        fields = '__all__'


class ThoughtForm(forms.ModelForm):
    """ Django form class for managing thoughts
    """
    class Meta:
        model = Thought
        fields = ['title', 'slug', 'content', 'idea', 'author']