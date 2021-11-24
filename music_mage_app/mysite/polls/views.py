# Import django modules
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
# , get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic.base import RedirectView 
from django.views.generic.edit import FormView
from django.core.exceptions import *
from django.core.cache import cache
from django.conf import settings

# Import models
from .forms import TrackForm
from .models import SongTracks

# Import modules
import pandas as pd
import numpy as np
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
import csv

# FUNCTION TO LOAD HOMEPAGE
def index(request):
    return render(request, 'polls/index.html')

# FUNCTION TO LOAD MUSIC MAGE SEARCH ENGINE PAGE
class TrackFormView(FormView):
    template_name = 'polls/mage.html'
    form_class = TrackForm
    # success_url = 'mage.html/find/'
    def form_valid(self, form):
    #     # This method is called when valid form data has been POSTed.
    #     # It should return an HttpResponse
        print(form.cleaned_data)

# def mage(request):
#     return render(request, 'polls/mage.html')

# OPTIONAL SONG DETAIL PAGE WITH ALBUM COVER ART, ETC.
# def detail(request, track_id):
#     track_id = cache.get('track_id')
#     return render(request, 'polls/detail.html', {'track_id':track_id})

# SEARCH RESULTS PAGE
# class ResultsView(generic.DetailView):
#     model = SongTracks
#     template_name = 'results.html'
#     track_id = cache.get('track_id')
#     recs = cache.get('recs')
#     sample_track = cache.get('sample_track')
#     sample_artist = cache.get('sample_artist')
    


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
        df["mood_vec"] = df[["valence", "energy", "acousticness", "instrumentalness", "speechiness", "mode"]].values.tolist()
        cache.set('df', df, 60)
        return df

# CREATE CLIENT FUNCTION TO CONNECT US TO SPOTIFY
def client():
    client_id = settings.SPOTIPY_CLIENT_ID
    client_secret = settings.SPOTIPY_CLIENT_SECRET
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    cache.get_or_set('spotify', spotify)
    return spotify

# CREATE FUNCTION TO MATCH INPUT TEXT WITH SPOTIFY SONG TRACK ID
def get_track_id(request):
    """Return the top 5 songs that match in mood."""

    # 1. Create empty list to hold track_id
    track_id = []
    
    # 2. Save the input text in variables
    form = TrackForm(request.POST)
    if form.is_valid():
        sample_track = form.cleaned_data['sample_track']
        sample_artist = form.cleaned_data['sample_artist']
        print(f'{sample_track} by {sample_artist}')
        cache.set('sample_track', sample_track, 60)
        cache.set('sample_artist', sample_artist, 60)

    try:
    # 3. Search Spotify for correct track
        track_result = client().search(q=f'track:{sample_track} artist:{sample_artist}', limit=1, type='track')
    except:
        return HttpResponse("no such song track")
        
    # 4. Save track id
    for i, t in enumerate(track_result['tracks']['items']):
        track_id.append(t['id'])

    track_id = track_id[0]
    cache.set('track_id', track_id, 60)
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
    ref_df_sorted = ref_df_sorted.set_index('track_name')
    cache.set('ref_df_sorted', ref_df_sorted[['artist_name', 'genre']].iloc[:n_recs], 60)

    return ref_df_sorted[['artist_name', 'genre']].iloc[:n_recs]

    # CREATE FUNCTION THAT SEARCHES FOR SONG RECOMMENDATIONS
def find(request):
    # if the user clicks search
    if request.method == 'POST':
        # get the track_id and dataframe
        track_id = get_track_id(request)
        ref_df = df()

        # if track_id is not None:   
        try:
            # Try to retrieve song recommendations
            recs = recommend(track_id=track_id, ref_df=ref_df)
            # return render(request,'mage.html', context=results)
        except:
            # if it doesn't work then reload the music mage search engine page
            return render(request, 'polls/mage.html', {
            'error_message': "You didn't enter a song track.",
            })
               
        # Display the page with the results  
        else:
            recs = recs.copy().to_html(classes='table table-striped text-center', justify='center')
            # classes='table table-striped text-center', justify='center'
            cache.set('recs', recs, 120)
            return HttpResponseRedirect(reverse('polls:results', args=(track_id,)))
            # return render(request,'polls/results.html', context=results)

    # if no one clicks the search button render the mage page       
    else:
        # return render(request,'polls/mage.html')
        return render(request,'polls/mage.html')

# FUNCTION TO LOAD RECOMMENDATION RESULTS
def results(request, track_id):
    form = TrackForm(request.POST)
    if form.is_valid():
        sample_track = form.cleaned_data['sample_track'].upper()
        sample_artist = form.cleaned_data['sample_artist'].upper()
    track_id = get_track_id(request)
    ref_df = df()
    recs = recommend(track_id=track_id, ref_df=ref_df).copy().to_html(classes='table table-striped text-center', justify='center')

    # sample_track = cache.get('sample_track') 
    # sample_artist = cache.get('sample_artist')
    # recs = cache.get('recs')
    # track_id = cache.get('track_id')
    context = {'recs': recs, 'sample_track':sample_track, 'sample_artist':sample_artist, 'track_id':track_id}
   
    return render(request, 'polls/results.html', context=context)