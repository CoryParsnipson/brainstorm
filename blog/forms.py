from django.forms import ModelForm

from blog.models import Idea, Thought


class IdeaForm(ModelForm):
    """
    Django form class for managing user interaction with Idea objects
    """
    class Meta:
        model = Idea
        fields = '__all__'


class ThoughtForm(ModelForm):
    """
    Django form class for managing thoughts
    """
    class Meta:
        model = Thought
        fields = ['title', 'slug', 'content', 'idea', 'author']