from django import forms
from django.forms import ModelForm
from .models import Page

class PageForm(ModelForm):
    """ form for the Page object """
    class Meta:
        model = Page
        fields = ('title', 'content') # define what fields to use from the obj on form
