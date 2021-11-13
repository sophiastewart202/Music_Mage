# Import django modules
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
# , get_object_or_404
from django.urls import reverse
from django.views import generic
# from django.views.generic import TemplateView
from django.core.exceptions import *

# Import models
from .forms import TrackForm
from .models import SongTracks
import os

# Import modules
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
import csv



# FUNCTION TO LOAD HOMEPAGE
def index(request):
    return render(request, 'polls/index.html')

# FUNCTION TO LOAD MUSIC MAGE SEARCH ENGINE PAGE
def mage(request):
    return render(request, 'polls/mage.html')

# SEARCH RESULTS PAGE
class ResultsView(generic.DetailView):
    model = SongTracks
    template_name = 'results.html'

# CREATE FUNCTION TO LOAD DATA INTO SONGTRACKS MODEL
def get_table():
    p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'music_characteristics_dataset.csv')
    with open(p, encoding='utf-8') as f:
        reader = csv.reader(f)
        # Skip the header row of the CSV file
        next(reader)
        
        for row in reader:
            obj, created = SongTracks.objects.get_or_create(
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
                # if there is a problem anywhere, you wanna know about it
                print("There was a problem")

# CREATE FUNCTION TO ACTIVATE DATA LOADING OR ACCESS DATA AND RETURN A DATAFRAME
def df():
    if SongTracks.objects.count() == 0:
        get_table()
    else:
        data = SongTracks.objects.all().values()
        df = pd.DataFrame(data)

    return df

# CREATE CLIENT FUNCTION TO CONNECT US TO SPOTIFY
def client():
    client_id = config('SPOTIPY_CLIENT_ID')
    client_secret = config('SPOTIPY_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return spotify

# CREATE FUNCTION TO MATCH INPUT TEXT WITH SPOTIFY SONG TRACK ID
def get_track_id(request):
    """Return the top 5 songs that match in mood."""

    # 1. Create empty list to hold track_id
    track_id = []
    
    # 2. Save the input text in variables
    form = TrackForm(request.POST)
    if form.is_valid():
        sample_track = TrackForm.cleaned_data['sample_track']
        sample_artist = TrackForm.cleaned_data['sample_artist']

    try:
    # 3. Search Spotify for correct track
        track_result = client().search(q=f'track:{sample_track} artist:{sample_artist}', limit=1, type='track')
    except:
        return HttpResponse("no such song track")
        
    # 4. Save track id
    for i, t in enumerate(track_result['tracks']['items']):
        track_id.append(t['id'])

    track_id = track_id[0]
    return track_id


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

    mydict = {
        "results": ref_df_sorted.iloc[:n_recs].to_html()
    }
    
    return mydict

# def results(request, id=None):
#     searched_item = get_object_or_404(TrackForm(request.POST), id=id)
    
#     context= {'Song Track': searched_item,
#               }
#     return render(request, 'polls/results.html', context)

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

# CREATE FUNCTION THAT SEARCHES FOR SONG RECOMMENDATIONS
def find(request):
    # if the user clicks search
    if request.method == 'POST':
        # get the track_id and dataframe
        track_id = get_track_id(request)
        ref_df = df()

        if track_id is not None:   
            try:
                # Try to retrieve song recommendations
                results = recommend(track_id=track_id, ref_df=ref_df, n_recs = 5)
                # return render(request,'mage.html', context=results)
            except:
                # if it doesn't work then reload the music mage search engine page
                return render(request, 'polls/mage.html', {
                'error_message': "You didn't enter a song track.",
                })
               
            # Display the page with the results  
            else:
            #   form.save()
                return HttpResponseRedirect(reverse('polls:results'))
                # return render(request,'polls/results.html', context=results)

    # if no one clicks the search button render the mage page       
    else:
        return render(request,'polls/mage.html')