from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('add/', views.add_unit, name='add_unit'),
    path('mine/', views.my_inventory, name='my_inventory'),
]
