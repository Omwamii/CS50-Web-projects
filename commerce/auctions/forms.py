from django import forms
from django.forms import ModelForm
from .models import Comment, Listing, Bid, Category

class ListingForm(ModelForm):
    """ form to create listing
    """
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'image',
                  'category')
        widgets = {
                'title': forms.TextInput(attrs={
                    'class': "form-control",
                    'style': 'max-width: 750px; margin-left: 100px; margin-top: 15px;',
                    'placeholder': 'Title'
                    }),
                'description': forms.Textarea(attrs={
                    'class': "form-control",
                    'style': 'max-width: 750px; margin-left: 100px; margin-top: 15px;',
                    'placeholder': 'Description'
                    }),
                'starting_bid': forms.NumberInput(attrs={
                    'class': "form-control",
                    'style': 'max-width: 750px; margin-left: 100px; margin-top: 15px;',
                    'placeholder': 'Starting bid'
                    }),
                'image': forms.FileInput(attrs={
                    'style': 'margin-left: 100px; margin-top: 7px;',
                    'input_text': 'Listing image (optional)'
                    }),
                'category': forms.Select(attrs={
                    'class': 'form-control',
                    'style': 'max-width: 750px; margin-left: 100px; margin-top: 7px;',
                    'empty_label': "Select category (optional)"
                    })
                }
        labels = {
            'title': False,
            'description': False,
            'starting_bid': False,
            'image': False,
            'listing_date': False,
            'listed_by': False,
            'category': False,
        }
        # category = forms.ChoiceField(choices=choices)


class CommentForm(ModelForm):
    """ form for comment submission
    """
    class Meta:
        model = Comment
        fields = ('text',)

class BidForm(ModelForm):
    """ submit bid on item
    """
    model = Bid
    fields = ('bid',)
