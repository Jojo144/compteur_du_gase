from base64 import b64encode
import json

from django.shortcuts import redirect
from django.http import HttpResponse


from django.conf import settings

from .middleware import CustomHeaderMiddleware


def get_portal_domain(request):
    """ Domain of the YunoHost portal for the current domain

    The portal (and its session cookie) lives on the topmost parent domain,
    e.g. example.org for gase.example.org.
    """
    host = request.get_host()
    try:
        with open('/etc/ssowat/conf.json') as f:
            # e.g. "example.org/yunohost/sso"
            portal = json.load(f)['domain_portal_urls'][host]
    except (OSError, ValueError, KeyError):
        return host
    return portal.split('/')[0]


# Utilisé par les liens « Connecte-toi » de la page d'accueil et par la page de
# login de l'admin. Pour le reste, c'est Ynh qui gère avec ses permissions qui
# protègent des url.
def login_router(request):
    """ Used as a drop in replacement for a Django login view

    - catch the GET param (?next=) indicating where to go after login
    - transcode it in ynh format
    - pass it to the ynh login page through redirection
    """

    redirect_url = request.build_absolute_uri(request.GET.get('next', settings.LOGIN_REDIRECT_URL))
    redirect_url = b64encode(redirect_url.encode()).decode()  # base64 requires a bytes object

    if CustomHeaderMiddleware.header not in request.META:
        # Pas connecté au SSO : on passe par le portail.
        return redirect(f'https://{get_portal_domain(request)}/yunohost/sso/?r={redirect_url}')
    else:
        # Connecté au SSO mais pas autorisé dans l'app : renvoyer vers le
        # portail ferait une boucle de redirection.
        return HttpResponse(
            "Tu n'as pas les droits, "
            "contacte ton administrateur·ice si tu penses que tu devrais."
        )


def portal_logout(request):
    """ Log out of the YunoHost portal, after the Django logout

    Without it, SSOwat keeps sending the Ynh-User header and the user is logged
    back in on the next request.
    The portal API then redirects back to the Referer.
    """
    response = redirect(f'https://{get_portal_domain(request)}/yunohost/portalapi/logout?referer_redirect')
    # Django's default policy (same-origin) would strip the Referer sent to the
    # portal, which is on another domain.
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
