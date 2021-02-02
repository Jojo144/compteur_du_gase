import base64

from django.urls import path

from . import views

urlpatterns = [
    path('login_router', views.login_router, name='login_router'),
]
