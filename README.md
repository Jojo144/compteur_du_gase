# Le Compteur du Gase (CdG)
Logiciel de gestion de comptes et de stock pour un GASE (Groupement d'Achat en Service Épicerie, une épicerie autogérée).

## Présentation

Le logiciel est pensé pour les groupements d’achats / épiceries fonctionnant de la façon suivante :
    • Chaque adhérent a un compte qu’il crédite.
    • Quand on fait des courses, on entre dans le logiciel ce que l’on achète (à la manière d’un logiciel de caisse) et cela débite notre compte en conséquence.
    • Le logicel met aussi à jour les stocks et propose un suivi de ceux-ci.

## Historique

Il y a trois GASEs (des épiceries autogérées) à Nantes. Depuis quelques années, on
y utilise un logiciel ([MoneyCoop](https://github.com/barchstien/gase-web)) pour gérer les stocks / les comptes des adhérents
/ la liste des adhérents. Ce logiciel est très pratique mais un peu vieillot et
difficile à faire évoluer.

Le projet est d'en refaire une version plus moderne, plus pratique, avec de
superbes statistiques et avec un meilleur nom : Le Compteur du GASE ! Il reste
encore beaucoup à améliorer mais une première version est néanmoins déjà
utilisable.

Version de démo ici : https://test-compteur.girole.fr

## Configuration

Ce logiciel peut être utilié tel quel.

Néanmoins, pour personnaliser l'interface graphique, il faut créer un fichier local.css dans le répertoire contenant le fichier base.css.

Différentes options sont également disponibles dans l'interface graphique dans Gestion>Interface d'administration>Réglages divers.  

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

### Après l'installation

À la première utilisation il faut aller dans l'interface administration pour créer des unités
(en général : kg, L, bouteille, sachet, pot) et des catégories (par ex :
Légumineuses, Conserves, Non alimentaire, ...).

Puis c'est parti !

Pensez ensuite à mettre en place une sauvegarde.

### Installation en ligne

Paquet Yunohost.
```
sudo yunohost app install https://github.com/Jojo144/compteur_du_gase
```
Pour le moment seuls les scripts `install` et `remove` fonctionne.

Pour mettre à jour sauvegarder la base, désinstallez et réinstallez.

## Sauvegarde de la base de donnée

Il faut sauvegarder le fichier `db.sqlite3` qui se trouve là où est installée votre application
(dans `/opt/compteur_gase` par exemple).

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
