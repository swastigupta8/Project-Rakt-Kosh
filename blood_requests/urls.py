from django.urls import path

from . import views

app_name = 'blood_requests'

urlpatterns = [
    path('submit/', views.submit, name='submit'),
    path('pending/', views.pending, name='pending'),
    path('<int:pk>/fulfill/', views.mark_fulfilled, name='mark_fulfilled'),
]
