from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    # works
    path('', views.index, name='index'),
    # works
    path('mage.html/', views.mage, name='mage'),
    #fails
    path('mage.html/find/', views.find, name='find'),
    # path('mage.html/<str:track_id>/find/', views.find, name='find'),
 
    path('mage.html/results/', views.ResultsView.as_view(), name='results'),
    
]

# path('mage.html/<int:track_id>/vote/', views.vote, name='vote'),
# path('mage.html/<int:pk>/', views.DetailView.as_view(), name='detail'),
# urlpatterns = [
#     path('', views.index, name='index'),
#     path('<int:question_id>/', views.detail, name='detail'),
#     path('<int:question_id>/results/', views.results, name='results'),
#     path('<int:question_id>/vote/', views.vote, name='vote'),
# ]

