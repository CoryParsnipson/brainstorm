from django.forms import ModelForm

from blog.models import Idea


class IdeaForm(ModelForm):
    """
    Django form class for managing user interaction with Idea objects
    """
    class Meta:
        model = Idea
        #fields = ['name', 'description']
        fields = '__all__'