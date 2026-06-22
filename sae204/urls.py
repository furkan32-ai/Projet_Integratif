from django.urls import path, include

urlpatterns = [
    path('', include('capteurs_app.urls')),
]
