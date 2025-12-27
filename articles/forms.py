from django import forms
from .models import Article, Comment
from ckeditor.widgets import CKEditorWidget
from taggit.forms import TagWidget

# from django_summernote.widgets import SummernoteWidget
WIDGET_CLASS = "w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-800 dark:text-white focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())  # Stored in MongoDB
    # featured_image = forms.ImageField(
    #     required=False,
    #     widget=forms.ClearableFileInput(attrs={'class': WIDGET_CLASS.replace('p-3', 'p-2')}) # Adjust padding for file input
    # )
    
    featured_image = forms.ImageField(
    required=False,
    widget=forms.ClearableFileInput(attrs={
        'class': 'hidden',  # hide the default input
        'id': 'featured-image-input'
    })
)

    published = forms.BooleanField(required=False, label="Publish immediately")  # New field

    class Meta:
        model = Article
        fields = ["title", "category", "tags", "featured_image", "published"]
        widgets = {
            'title': forms.TextInput(attrs={'class': WIDGET_CLASS}),
            # Select is for Category field (if it's a ForeignKey/ChoiceField)
            'category': forms.Select(attrs={'class': WIDGET_CLASS}),
            # TextInput is good for Tags (if you're using a single CharField for comma-separated tags)
            'tags': TagWidget(attrs={'class': WIDGET_CLASS}),
            
            # 'published': forms.IntegerField(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    'class': WIDGET_CLASS.replace('p-3', 'p-2'),
                    "rows": 4,
                    "placeholder": "Write your comment here...",
                }
            ),
        }
