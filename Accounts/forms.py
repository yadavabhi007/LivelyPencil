from  django import forms
from .models import ImageUpload, Support


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ('image','post')


class SupportForms(forms.ModelForm):
    images = forms.SelectMultiple()
    class Meta: 
        model = Support
        fields = []