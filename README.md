# Le Compteur du Gase (CdG)
Logiciel de gestion de comptes et de stock pour un GASE (Groupement d'Achat en Service Épicerie).

## Présentation

Il y a trois GASEs (Groupement d'Achats en Service Épicerie) à Nantes qui sont des épiceries autogérées.

Depuis quelques années, on y utilise un logiciel qui s'appelle Money Coop pour gérer les stocks / les comptes des adhérents / la liste des adhérents.
Ce logiciel est très pratique mais un peu vieillot et difficile à faire évoluer.

Le projet est d'en refaire une version plus moderne, plus pratique, avec des super statistiques et avec un meilleur nom : Le Compteur du GASE !

Version de démo ici : https://test-compteur.girole.fr/

## Contributions

Toutes les remarques et contributions sont les bienvenues. N'hésitez pas à entrer en contact avec moi si vous souhaitez l'installer dans votre épicerie.

Contact : jojo144@girole.fr

## Installation

Deux façons d'installer le logiciel : soit en local sur Debian/Ubuntu, soit en ligne avec [Yunohost](https://yunohost.org).

Le compteur du GASE est une application écrite en [Django](https://www.djangoproject.com/), un framework Python pour écrire des applications web.
Dans les deux cas il sagit donc d'installer un serveur web (Nginx) et de faire tourner Gunicorn.

### Installation en local

Testé sur Ubuntu 19.04. Il suffit d'éxecuter le script `local_install.sh` qui fait tout ce qu'il faut.
```
sudo apt-get install python3-venv nginx
sudo mkdir /opt/compteur_gase
cd /opt/compteur_gase
sudo git clone https://github.com/Jojo144/compteur_du_gase
# personaliser les variables dans local_install.sh
sudo compteur_du_gase/local_install.sh
```
Ensuite le logiciel est accessible sur http://localhost .
Tester aussi de redémarrer pour voir si les services se lancent bien tous seuls.

Vous pouvez choisir un autre répertoire que `/opt/compteur_gase` ça devrait marcher.
Il y a des *warnings* à propos du cache pip, je les ai ignoré pour le moment.

Ensuite, aller dans l'interface d'administration et créer des unités et des catégories.

Puis c'est parti !

### Installation en ligne

Paquet Yunohost. TODO

## Migration depuis gase-web et Mysql

J'ai écrit un script qui permet de migrer les données de MoneyCoop / gase-web (base de donnée Mysql) vers le CdG.

Nécessite le paquet `mysql-connector-python` et `ipython` pour le `%run`. Dans le venv :
```
pip install mysql-connector-python ipyhton
```
Puis `./manage.py shell` et dans ce shell Django :
```
%run migration.py
```
