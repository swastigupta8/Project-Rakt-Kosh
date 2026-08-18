from django.urls import path

from . import views

app_name = 'drives'

urlpatterns = [
    path('nearby/', views.nearby, name='nearby'),
    path('create/', views.create_drive, name='create'),
]
