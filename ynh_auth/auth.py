from django.contrib.auth.backends import RemoteUserBackend
from django.conf import settings
import ldap


YNH_MAIN_PERM = f'{settings.YUNOHOST_APP_ID}.main'
YNH_ADMIN_PERM = f'{settings.YUNOHOST_APP_ID}.admin'


ATTRS_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

PERMISSIONS_MAP = {
    'is_superuser': f'cn={YNH_ADMIN_PERM},ou=permission,dc=yunohost,dc=org',
    'is_staff': f'cn={YNH_ADMIN_PERM},ou=permission,dc=yunohost,dc=org',
    'is_active': f'cn={YNH_MAIN_PERM},ou=permission,dc=yunohost,dc=org',
}


class SSOWatRemoteUserBackend(RemoteUserBackend):
    def _get_ldap_informations(self, username):
        conn = ldap.initialize('ldap://')

        result = conn.search_s(
            'ou=users,dc=yunohost,dc=org',
            ldap.SCOPE_ONELEVEL,
            f'(&(objectClass=posixAccount)(uid={username}))',
            list(ATTRS_MAP.values()) + ['permission']
        )
        # Example output :
        # [('uid=user,ou=users,dc=yunohost,dc=org',
        #   {'givenName': ['user'],
        #    'sn': ['user'],
        #    'mail': ['user@ynh.dev',
        #             'root@ynh.dev',
        #             'admin@ynh.dev',
        #             'webmaster@ynh.dev',
        #             'postmaster@ynh.dev',
        #             'abuse@ynh.dev'],
        #    'permission': ['cn=mail.main,ou=permission,dc=yunohost,dc=org',
        #                   'cn=xmpp.main,ou=permission,dc=yunohost,dc=org',
        #                   'cn=compteur_gase.home_page,ou=permission,dc=yunohost,dc=org',
        #                   'cn=compteur_gase.ynh_auth,ou=permission,dc=yunohost,dc=org',
        #                   'cn=compteur_gase.main,ou=permission,dc=yunohost,dc=org']
        #    }
        #   )
        #  ]

        assert len(result) == 1, "expecting exactly 1 result as we juste authed user"
        ldap_attrs = result[0][1]

        attrs = {}
        for django_k, ldap_k in ATTRS_MAP.items():
            # attrs are multi-valued, get only the 1st
            attrs[django_k] = ldap_attrs.get(ldap_k, [''])[0].decode()


        user_permissions = ldap_attrs.get('permission', [])
        for django_k, ynh_ldap_perm in PERMISSIONS_MAP.items():
            attrs[django_k] = ynh_ldap_perm.encode() in user_permissions

        return attrs


    def authenticate(self, request, remote_user):
        attrs_from_ldap = self._get_ldap_informations(remote_user)

        if attrs_from_ldap['is_active']:
            user = super().authenticate(request, remote_user)
            for k, v in attrs_from_ldap.items():
                setattr(user, k, v)

            user.set_unusable_password()  # pour ne plus avoir le lien de changement de mot de passe
            user.save()

        else:
            return None  # AnonymousUser

        return user
