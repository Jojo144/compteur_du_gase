# Coder sur le compteur du GASE

## Environnement de développement

Il est recommandé d'utiliser des paramètres personalisés pour le dév :

    cp compteur/settings_local.py.dev.example compteur/settings_local.py


## Pour mettre à jour en testant une branche

Pour mettre à jour :
```
sudo yunohost app upgrade compteur_gase -u https://github.com/Jojo144/compteur_du_gase_ynh/tree/MA-BRANCHE
```


## Intégration YunoHost

Pour les urls protégées par les permissions Ynh, le SSO gère tout seul le fait
qu'on doit être authentifié : il redirige vers la page de loggin avec la bonne url
de retour.

On utilise `login_router` pour rediriger vers l'authentification Ynh dans les cas
non protégés par le SSO :
- quand on clique sur "Connecte-toi" sur la page d'accueil pour afficher les
  numéros de tel et cie
- et c'est tout je crois ! À un moment on l'utilisait pour les pages d'admin mais maintenant
  elles sont protégées par le SSO. Du coup on aurait pu coder l'url en dur sur la page
  d'accueil mais ça permet 1. de ne pas faire le calcul si pas de clique sur le bouton et
  2. peut-être on s'en servira plus tard.


### `ynh_auth/apps.py`

On n'a pas fait tout ce qu'il faut pour que `ynh_auth` soit une vraie application
mais ça n'a pas l'air de poser problème.

### `ynh_auth/auth.py`

C'est là où on fait les requêtes LDAP pour savoir quelles permission a
l'utilisateur courant. Visiblement on peut faire ces requête en tant que Anonyme
(pas besoin d'identifiants).

On récupère les permissions `main` et `admin`. Celle de la page d'accueil on n'en
n'a pas besoin ici.

La méthode `authenticate` met à jour tous les attributs à chaque connexion (une
liste des utilisateurs est maintenue dans la base de donnée, en parallèle du LDAP).

### `ynh_auth/middleware.py`

Là on dit juste le nom du header de la requête HTML dans lequel Ynh met le nom
d'utilisateur courant loggué.

### `ynh_auth/urls.py` et `ynh_auth/views.py`

La définition du `login_router` (voir plus haut).

### `scripts/_common.sh`

On y définit les trois permissions.

Remarque : la permission admin est "protected", c'est-à-dire qu'on ne peut pas la donner aux visiteurs, car sinon le visiteur essaie d'accéder à l'interface d'amdin en tant que anonyme et ça c'est pas possible.
