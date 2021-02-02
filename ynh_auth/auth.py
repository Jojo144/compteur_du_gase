from django.contrib.auth.backends import RemoteUserBackend

class AllAdminRemoteUserBackend(RemoteUserBackend):
    def authenticate(self, request, remote_user):
        user = super().authenticate(request, remote_user)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
