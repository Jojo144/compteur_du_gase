from django.contrib.auth.middleware import RemoteUserMiddleware

class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = 'HTTP_REMOTE_USER'  # nom du header dans les requêtes qui contient le nom d'utilisateur courant
