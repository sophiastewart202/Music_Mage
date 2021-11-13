from django import forms
from django.forms import ModelForm
from django.db import models
from .models import SongTracks

class TrackForm(forms.Form):
    sample_track = forms.CharField(label='sample_track', max_length=100)
    sample_artist = forms.CharField(label='sample_artist', max_length=100)

# class TrackForm(forms.ModelForm):

#     class Meta:
#         model = SongTracks
#         fields = ('sample_track','sample_artist')