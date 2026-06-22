from django.urls import path
from . import views

app_name = 'capteurs_app'

urlpatterns = [
    path('', views.liste_capteurs, name='liste_capteurs'),
    path('capteur/<str:id_capteur>/', views.detail_capteur, name='detail_capteur'),
]
