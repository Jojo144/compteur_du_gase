"""compteur URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

from compteur.settings import PATH

def redirect_to_detail(request):
    from base.models import LocalSettings
    return redirect(
        'admin:base_localsettings_change',
        object_id=LocalSettings.objects.first().pk
    )

urlpatterns = [
    path(PATH, include('base.urls')),
    path(PATH + 'admin/base/localsettings/', redirect_to_detail),
    path(PATH + 'admin/', admin.site.urls),
    path(PATH + 'accounts/', include('django.contrib.auth.urls')),
]

if settings.YNH_INTEGRATION_ENABLED:
    urlpatterns = [
        path(PATH + 'ynh_auth/', include('ynh_auth.urls')),
    ] + urlpatterns
