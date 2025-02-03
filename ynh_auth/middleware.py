from django.contrib.auth.middleware import RemoteUserMiddleware

class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = 'HTTP_YNH_USER'  # nom du header dans les requêtes qui contient le nom d'utilisateur courant

    def process_request(self, request):
        print (str(request))
        super().process_request(request)
