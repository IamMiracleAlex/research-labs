from datetime import datetime
from django import forms
from .models import Event
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class EventForm(forms.ModelForm):
    article = forms.CharField(widget=CKEditorUploadingWidget())
    event_date = forms.DateTimeField(initial=datetime.today(), widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Event
        exclude = ["created_at", "updated_at", "author"]

def event_dates():
    return [("", "All Dates")] + [(e, e.strftime("%B %Y")) for e in Event.objects.dates('event_date', 'month')]


class EventFilterForm(forms.Form):
    DRAFT, PUBLISHED = 'Draft', 'Published'
    STATUS_CHOICES = (
        ("", "All Posts"),
        (DRAFT, DRAFT),
        (PUBLISHED, PUBLISHED),
    )

    DATE_CHOICES = [
        ("", "All Dates")
    ]

    event_date = forms.ChoiceField(
        choices=event_dates,
        required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    search = forms.CharField(required=False)
