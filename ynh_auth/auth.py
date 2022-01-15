from django.contrib.auth.backends import RemoteUserBackend

class AllAdminRemoteUserBackend(RemoteUserBackend):
    def authenticate(self, request, remote_user):
        user = super().authenticate(request, remote_user)
        user.is_staff = True  # on pourrait faire une perm pour l'admin mais pour l'instant accès à tous
        user.is_superuser = True
        user.set_unusable_password()  # pour ne plus avoir le lien de changement de mot de passe
        user.save()
        return user
