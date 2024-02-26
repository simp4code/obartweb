from django import forms
from .models import VideoContent

class VideoContentForm(forms.ModelForm):
    class Meta:
        model = VideoContent
        fields = ['title', 'chapter', 'video', 'short_details']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chapter'].widget = forms.Select(choices=VideoContent.CHAPTER_CHOICES)
