
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from databanks.models import DataBank


class DataBankAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = DataBank
        fields = '__all__'
        exclude = ['views']
