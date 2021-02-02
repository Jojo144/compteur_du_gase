from base64 import b64encode
from django.shortcuts import redirect


from django.conf import settings



def login_router(request):
    """ Used as a drop in replacement for a Django login view

    - catch the GET param (?next=) indicating where to go after login
    - transcode it in ynh format
    - pass it to the ynh login page through redirection
    """
    redirect_url = request.get('next', settings.LOGIN_REDIRECT_URL)
    ynh_login_url = f'/yunohost/sso/?r={b64encode(redirect_url)}'
    return redirect(ynh_login_url)
