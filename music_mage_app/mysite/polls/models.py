from django.db import models
import datetime
from django.utils import timezone
import csv
import pandas as pd

# Create your models here.

# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')

#     def __str__(self):
#         return self.question_text
    
#     def was_published_recently(self):
#         return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
    
#     def __str__(self):
#         return self.choice_text

class SongTracks(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    genre = models.CharField(max_length=100)
    track_name = models.CharField(max_length=100)
    artist_name = models.CharField(max_length=100)
    popularity = models.IntegerField()
    valence = models.FloatField()
    energy  = models.FloatField()
    danceability  = models.FloatField()
    acousticness  = models.FloatField()
    tempo  = models.FloatField()
    speechiness  = models.FloatField()
    mode  = models.IntegerField()
    instrumentalness = models.FloatField()

    # def __str__(self):
    #     return self.objects.all()

    # def__str__(self):
    #     return self.objects.all()

# class df(models.Model):
#     with open('music_characteristics_dataset.csv') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             _, created = song_track.objects.get_or_create(
#                 id=row[0],
#                 genre=row[1],
#                 track_name=row[2],
#                 artist_name=row[3],
#                 popularity=row[4],
#                 valence=row[5],
#                 energy=row[6],
#                 danceability=row[7],
#                 acousticness=row[8],
#                 tempo=row[9],
#                 speechiness=row[10],
#                 mode=row[11],
#                 instrumentalness=row[12],
#                 )

    



   