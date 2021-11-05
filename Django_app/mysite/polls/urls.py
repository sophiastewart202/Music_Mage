from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('mage.html/', views.IndexView.as_view(), name='mage'),
    path('mage.html/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('mage.html/<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('mage.html/<int:question_id>/vote/', views.vote, name='vote'),
]



# urlpatterns = [
#     path('', views.index, name='index'),
#     path('<int:question_id>/', views.detail, name='detail'),
#     path('<int:question_id>/results/', views.results, name='results'),
#     path('<int:question_id>/vote/', views.vote, name='vote'),
# ]

