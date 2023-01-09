from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='myapp/index'),
    path('verified', views.verified, name='myapp/verified'),
]