import base64

from django.urls import path

from . import views

urlpatterns = [
    path('login_router', views.login_router, name='login_router'),
    path('portal_logout', views.portal_logout, name='portal_logout'),
]
