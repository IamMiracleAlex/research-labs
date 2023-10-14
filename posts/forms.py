from datetime import datetime

from django import forms
from django.utils.functional import lazy
from django.db.models.query import QuerySet

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from posts.models import Post, PostBody, SubCategory, Theme, Sector, Product, Region, Company


class ContentEditorForm(forms.ModelForm):
    subcategories = forms.ModelMultipleChoiceField(
        queryset=SubCategory.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple, required=False
    )
    themes = forms.ModelMultipleChoiceField(
        queryset=Theme.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple, required=False
    )
    sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple, required=False
    )
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple, required=False
    )
    regions = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple, required=False
    )
    companies = forms.ModelMultipleChoiceField(
        queryset=Company.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple, required=False
    )
  
    published_at = forms.DateTimeField(initial=datetime.today(), widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Post
        exclude = ['author', 'slug', 'views', 'body', 'excerpt']

class PostBodyForm(forms.ModelForm):
    text = forms.CharField(label='Section Body', widget=CKEditorUploadingWidget()) # can add seprate config

    class Meta:
        model = PostBody
        fields = ['title', 'text', ]

PostBodyFormset = forms.modelformset_factory(PostBody, PostBodyForm)

class WhatsInsidePostBodyForm(forms.ModelForm):
    title0 = forms.CharField(label="What's Inside", required=False, widget=forms.TextInput(attrs={"value": "What's Inside"}),)
    text0 = forms.CharField(label='Section Body', widget=CKEditorUploadingWidget())

    class Meta:
        model = PostBody
        fields = ['title0', 'text0', ]
    
    def save(self, commit=True):
        obj = self.Meta.model(
            title=self.cleaned_data.get('title0'),
            text=self.cleaned_data.get('text0')
        )
        if commit:
            obj.save()
        
        return obj

class KeyPointPostBodyForm(forms.ModelForm):
    title1 = forms.CharField(label="Key Points", required=False, widget=forms.TextInput(attrs={"value": "Key Points"}),)
    text1 = forms.CharField(label='Section Body', widget=CKEditorUploadingWidget())

    class Meta:
        model = PostBody
        fields = ['title1', 'text1', ]

    def save(self, commit=True):
        obj = self.Meta.model(
            title=self.cleaned_data.get('title1'),
            text=self.cleaned_data.get('text1')
        )
        if commit:
            obj.save()
        
        return obj
class IntroductionPostBodyForm(forms.ModelForm):
    title2 = forms.CharField(label="Introduction", required=False, widget=forms.TextInput(attrs={"value": "Introduction"}),)
    text2 = forms.CharField(label='Section Body', widget=CKEditorUploadingWidget())

    class Meta:
        model = PostBody
        fields = ['title2', 'text2', ]

    def save(self, commit=True):
        obj = self.Meta.model(
            title=self.cleaned_data.get('title2'),
            text=self.cleaned_data.get('text2')
        )
        if commit:
            obj.save()
        
        return obj

class ResearchAnalysisPostBodyForm(forms.ModelForm):
    title3 = forms.CharField(label="Research Analysis", required=False, widget=forms.TextInput(attrs={"value": "Research Analysis"}),)
    text3 = forms.CharField(label='Section Body', widget=CKEditorUploadingWidget())
    class Meta:
        model = PostBody
        fields = ['title3', 'text3', ]

    def save(self, commit=True):
        obj = self.Meta.model(
            title=self.cleaned_data.get('title3'),
            text=self.cleaned_data.get('text3')
        )
        if commit:
            obj.save()
        
        return obj
class WhatWeThinkPostBodyForm(forms.ModelForm):
    title4 = forms.CharField(label="What We Think", required=False, widget=forms.TextInput(attrs={"value": "What We Think"}),)
    text4 = forms.CharField(label='Section Body', widget=CKEditorUploadingWidget())

    class Meta:
        model = PostBody
        fields = ['title4', 'text4', ]

    def save(self, commit=True):
        obj = self.Meta.model(
            title=self.cleaned_data.get('title4'),
            text=self.cleaned_data.get('text4')
        )
        if commit:
            obj.save()
        
        return obj

def published_dates():
    return [("", "All Dates")] + [(p, p.strftime("%B %Y")) for p in Post.objects.dates('published_at', 'month')]

class FilterForm(forms.Form):
    DRAFT, PUBLISHED = 'Draft', 'Published'
    STATUS_CHOICES = (
        ("", "All Posts"),
        (DRAFT, DRAFT),
        (PUBLISHED, PUBLISHED),
    )

    DATE_CHOICES = [
        ("", "All Dates")
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False
    )
    subcategory = forms.ModelChoiceField(
        queryset=lazy(SubCategory.objects.all, QuerySet)(), required=False)
    search = forms.CharField(required=False)
