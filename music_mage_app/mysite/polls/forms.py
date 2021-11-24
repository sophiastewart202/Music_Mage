from django import forms
from django.forms import ModelForm
from django.db import models
from .models import SongTracks

class TrackForm(forms.Form):
    sample_track = forms.CharField(label='Song Track', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Track Name', 'style': 'width: 400px;', 'class': 'form-control', 'align':'center'}))
    sample_artist = forms.CharField(label='Artist Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Artist Name', 'style': 'width: 400px;', 'class': 'form-control', 'align':'center'}))

    # def send_email(self):
    #     # send email using the self.cleaned_data dictionary
    #     pass

# class TrackForm(forms.ModelForm):

#     class Meta:
#         model = SongTracks
#         fields = ('sample_track','sample_artist')