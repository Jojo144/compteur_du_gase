from base64 import b64encode
from django.shortcuts import redirect
from django.http import HttpResponse


from django.conf import settings


# Cette fonction n'est utilisé que quand on clique sur le bouton "Interface d'admin".
# Pour le reste, c'est Ynh qui gère avec ses permissions qui protègent des url.
def login_router(request):
    """ Used as a drop in replacement for a Django login view

    - catch the GET param (?next=) indicating where to go after login
    - transcode it in ynh format
    - pass it to the ynh login page through redirection
    """

    with open('/etc/yunohost/current_host') as f:
        ynh_main_domain = f.readline()

    redirect_url = request.build_absolute_uri(request.GET.get('next', settings.LOGIN_REDIRECT_URL))
    redirect_url = b64encode(redirect_url.encode()).decode()  # base64 requires a bytes object

    if request.user.is_anonymous:
        return redirect(
            f'https://{ynh_main_domain}/yunohost/sso/?r={redirect_url}'
        )
    else:
        # On est connectés mais pas autorisés.
        return HttpResponse(
            "Tu n'as pas les droits, "
            "contacte ton administrateur·ice si tu penses que tu devrais."
        )
