# Create your views here.
from django.http import HttpResponse
# HttpResponseRedirect,
from django.shortcuts import render
# get_object_or_404,
# from django.urls import reverse
from django.views import generic
# from .models import Person
from .forms import TrackForm
from .models import SongTracks
from django.core.exceptions import *
import os

# Import modules
# import sys
# If your authentification script is not in the project directory
# append its folder to sys.path
# sys.path.append("../spotify_api_web_app")
import pandas as pd
# from tqdm import tqdm
# import time
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
import csv

def get_table():
    p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'music_characteristics_dataset.csv')
    with open(p, encoding='utf-8') as f:
        reader = csv.reader(f)
        # Skip the header row of the CSV file
        next(reader)

        for row in reader:
            _, created = SongTracks.objects.get_or_create(
            id=row[0],
            genre=row[1],
            track_name=row[2],
            artist_name=row[3],
            popularity=row[4],
            valence=row[5],
            energy=row[6],
            danceability=row[7],
            acousticness=row[8],
            tempo=row[9],
            speechiness=row[10],
            mode=row[11],
            instrumentalness=row[12],
            )
            try:
                created.save()
            except:
                # if the're a problem anywhere, you wanna know about it
                print("there was a problem with line")

def df():
    get_table()
    data = SongTracks.objects.all()
    return data
    

def index(request):
    # template_name = 'polls/index.html'
    return render(request, 'polls/index.html')

# CREATE CLIENT FUNCTION TO CONNECT US TO SPOTIFY
def client():
    client_id = config('SPOTIPY_CLIENT_ID')
    client_secret = config('SPOTIPY_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return spotify

def get_track_id(request):
    """Return the top 5 songs that match in mood."""

    # GET TRACK ID
    track_id = []

    # sample_track = request.POST.get('sample_track', None)
    # sample_artist = request.POST.get('sample_artist', None)
    
    form = TrackForm(request.POST)

    if form.is_valid():
        sample_track = TrackForm.cleaned_data['sample_track']
        sample_artist = TrackForm.cleaned_data['sample_artist']

    try:
    # 3. Search Spotify for correct track
        # sample_track = TrackForm.sample_track
        # sample_artist = TrackForm.sample_artist
        track_result = client().search(q=f'track:{sample_track} artist:{sample_artist}', limit=1, type='track')
    except:
        return HttpResponse("no such song track")
        
    # 4. Save details, especially track id
    for i, t in enumerate(track_result['tracks']['items']):
            # artist_name.append(t['artists'][0]['name'])
            # track_name.append(t['name'])
        track_id.append(t['id'])

    track_id = track_id[0]
    return track_id

# data = song_track.objects.all()
#     id = {
#         "id": data
#     }
# return render_to_response("login/profile.html", id)

        
           

# CREATE RECOMMENDATION FUNCTION
def recommend(track_id, ref_df, n_recs = 5):
    
    # Get audio features of given track from spotify api
    track_features = client().audio_features(track_id)[0]
    # Combine into mood vector
    track_moodvec = np.array([track_features['valence'], track_features['energy'], track_features['acousticness'], 
                              track_features['instrumentalness'], track_features['speechiness'], 
                              track_features['mode']])
    
    # Compute distances to all reference tracks
    ref_df["distances"] = ref_df["mood_vec"].apply(lambda x: np.linalg.norm(track_moodvec-np.array(x)))
    # Sort by popularity
    ref_df_sorted = ref_df.sort_values(by = "popularity", ascending = True)
    # Sort distances from lowest to highest
    ref_df_sorted = ref_df.sort_values(by = "distances", ascending = True) 
    
    # If the input track is in the reference set, it will have a distance of 0, but should not be recommended
    ref_df_sorted = ref_df_sorted[ref_df_sorted["id"] != track_id]
    
    # Return n recommendations
    return ref_df_sorted.iloc[:n_recs]

def mage(request):
    return render(request, 'polls/mage.html')


# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):

#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
        
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'

class ResultsView(generic.DetailView):
    model = TrackForm
    template_name = 'polls/results.html'

# def search(request):
#     if request.method == 'POST':
#         search_id = request.POST.get('textfield', None)
#         try:
#             user = TrackForm.objects.get(name = search_id)
#             #do something with user
#             html = ("<H1>%s</H1>", user)
#             return HttpResponse(html)
#         except TrackForm.DoesNotExist:
#             return HttpResponse("no such song track")  
#     else:
#         return render(request, 'results.html')

def find(request):
    # if the user clicks submit
    if request.method == 'POST':
        # form = TrackForm(request.POST)
        # if form.is_valid():
        
        # get the track_id
        track_id = get_track_id(request)
        ref_df = df()
    # If the track_id is not nothing/empty

        # if form.is_valid():
        if track_id is not None:   
    # song_track = get_object_or_404(TrackForm, pk=track_id)
            try:
                # Try to retrieve recommendations that sound similar.
                results = recommend(track_id=track_id, ref_df=ref_df)
            except:
            
                return render(request, 'polls/mage.html', {
                'error_message': "Input not recognized.",
                })
            
            # Redisplay the default song track search form with the results  
            else:
                # form.save()
                return render(request, 'mage.html', {"results":results})
            
    else:
        return render(request, 'polls/mage.html')

    # def dynamic_articles_view(request):
    # context['object_list'] = article.objects.filter(title__icontains=request.GET.get('search'))
    # return render(request, "encyclopedia/article_detail.html", context)
        

# try:
#     profile = request.user.userprofile
# except UserProfile.DoesNotExist:
#     profile = UserProfile(user=request.user)

# if request.method == 'POST':
#     form = TrackForm(request.POST)
#     if form.is_valid():
#         form.save()
#         # return redirect()
#         return HttpResponseRedirect(reverse('polls:results', args=(song_tracks.id,)))
# else:
#     form = TrackForm()
# return render((request, 'polls/mage.html'))

    # return render(request, 'product-search.html')
        # return HttpResponseRedirect(reverse('polls:results', args=(song_tracks.id,)))


# if request.method == "POST":
#         query_name = request.POST.get('name', None)
#         if query_name:
#             results = Product.objects.filter(name__contains=query_name)
#             return render(request, 'product-search.html', {"results":results})

#    