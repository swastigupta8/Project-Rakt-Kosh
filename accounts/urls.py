from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/donor/', views.register_donor, name='register_donor'),
    path('register/bank/', views.register_bank, name='register_bank'),
    path('login/', views.RaktKoshLoginView.as_view(), name='login'),
    path('logout/', views.RaktKoshLogoutView.as_view(), name='logout'),
]
