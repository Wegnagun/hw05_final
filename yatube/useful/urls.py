from django.urls import path

from . import views

app_name = 'useful'

urlpatterns = [
    path('percent/', views.percent, name='percent'),
]
