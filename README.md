# Le Compteur du Gase (CdG)
*Logiciel pour gérer une épicerie autogéreé !*

## Présentation

*Le Compteur du Gase* permet de gérer les comptes et stocks d'un GASE (Groupement d'Achat en Service Épicerie, une épicerie autogérée).
Le logiciel est pensé pour les groupements d’achats / épiceries fonctionnant de la façon suivante :
* Chaque adhérent a un compte qu’il crédite.
* Quand on fait des courses, on entre dans le logiciel ce que l’on achète (à la manière d’un logiciel de caisse) et cela débite notre compte en conséquence.
* Le logiciel met aussi à jour les stocks et propose un suivi de ceux-ci.
  Il permet de gérer les stocks, les comptes des adhérents et la liste des adhérents.

Le CdG intègre aussi un tableau des permanences qui permet de s'inscrire pour tenir les permanences de l'épiceries.

[![Integration level](https://dash.yunohost.org/integration/compteur_du_gase.svg)](https://dash.yunohost.org/appci/app/compteur_du_gase) ![](https://ci-apps.yunohost.org/ci/badges/compteur_du_gase.status.svg)  ![](https://ci-apps.yunohost.org/ci/badges/compteur_du_gase.maintain.svg)
[![Install compteur_du_gase with YunoHost](https://install-app.yunohost.org/install-with-yunohost.svg)](https://install-app.yunohost.org/?app=compteur_du_gase)

## Capture d'écran

![Capture d'écran](/screenshot/Screenshot_2021-12-26_Le-compteur-du-GASE.png)


## Historique

Depuis quelques années, les trois GASE (des épiceries autogérées) de Nantes utilisent le logiciel ([MoneyCoop](https://github.com/barchstien/gase-web)).
Le Compteur du GASE est une réécriture du logiciel MoneyCoop pour en refaire une version plus moderne, plus pratique, avec de
superbes statistiques et avec un meilleur nom !

MoneyCoop a été écrit en ~ 2012 par Pascal L. pour l'épicerie l'Indépendante à Paris 18ème.
Cette épicerie consistait en deux gros placards au fond d'une salle de réunion et une permanence par semaine.
Au début, les comptes étaient faits avec une feuille Excel mais ça s'est rapidement révélé ingérable.
Comme ils avaient peu de temps le logiciel était en ligne et chacun enregistrait ses achats chez soi, de façon à consacrer tout le temps des permanences à l'échange, et à l'organisation (commandes).
L'Indépendante a été influencée par le GASE de Rochefort en Terre. Puis d'autres groupements ont demandé les sources de MoneyCoop pour l'utiliser, notamment à Nantes via une personne qui était à l'Indépendante avant, à Champigny...
Deux principes ont guidé l'écriture du logiciel : "tout le monde doit pouvoir tout faire" (même mot de passe pour tous), "simple et robuste" (par exemple pas possible de supprimer des choses pour éviter les erreurs).

Il n'y avait pas de statistiques dans la version de base, cela a probablement été rajouté par les Nantais.


## Épiceries utilisant le logiciel
| Épicerie                  | Description                                                                                                                                                               | Utilise le compteur depuis | Contact                                                                        |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|--------------------------------------------------------------------------------|
| Le GASE de l'Esclain      | Épicerie associative autogérée, quartier Beauséjour à Nantes                                                                                                              | février 2021               | bonjour (arrrobase) gasedelesclain.fr                                          |
| Le GASE à Roulettes       | GASE 100% bénévole et autogéré à Nantes centre                                                                                                                            | mai 2020                   | commission informatique : informatique (puis un arobase puis) roulettes.eu.org |
| Petite Epicerie Pell'Mêle | La Petite Epicerie Pell’Mêle est une épicerie associative de produits bio (et locaux si possible) en vrac, créée en octobre 2019. https://pellmele.fr/la-petite-epicerie/ | septembre 2019             | pellmele-epicerie (arrobase) retzien.fr                                        |
| Le Gasouillis             | Une épicerie associative à Guénouvry (44 Guémené-Penfao)                                                                                                                  | septembre 2021             | gasouillis (arrobase) tutanota.com                                             |

Si vous utilisez le Compteur du Gase et que vous acceptez d'apparaître sur cette liste, merci d'envoyer un mail à jojo144@girole.fr .


## Démonstration

Version de démo ici : https://demo-compteur.gase.eu.org

L'interface d'administration n'est pour l'instant pas accessible sans compte sur le serveur gase.eu.org.


## Installation

Nous proposons deux façons d'installer le logiciel :
- soit en local → le logciel est installé sur un ordinateur et est accessible sur celui-ci (sans avoir besoin d'accès internet)
- soit en ligne → le logiciel est installé sur un serveur et est accessible sur n'importe quel appareil disposant d'un accès à internet.

Le compteur du GASE est une application écrite en [Django](https://www.djangoproject.com/), un framework Python pour écrire des applications web.
Dans les deux cas, il sagit donc d'installer un serveur web (Nginx) et de faire tourner Gunicorn.


### Installation en local sur Debian ou Ubuntu

Testé sur Ubuntu 19.04. Il suffit d'exécuter le script `local_install.sh` qui fait tout ce qu'il faut.
```
sudo apt-get install python3-venv nginx
sudo mkdir /opt/compteur_gase
cd /opt/compteur_gase
sudo git clone https://github.com/Jojo144/compteur_du_gase_ynh
# personaliser les variables dans local_install.sh
sudo compteur_du_gase_ynh/local_install.sh
```
Ensuite le logiciel est accessible sur http://localhost .
Tester aussi de redémarrer pour voir si les services se lancent bien tous seuls.

Vous pouvez choisir un autre répertoire que `/opt/compteur_gase` ça devrait marcher.
Il y a des *warnings* à propos du cache pip, je les ai ignoré pour le moment.

Attention, si vous tombez sur une page Apache "It works" c'est que vous avez Apache d'installé au lieu de Nginx (ou les deux).


### Installation en ligne avec YunoHost

[YunoHost](https://yunohost.org) est une distribution dérivée de Debian facilitant l'autohébergement.
Nous proposons un paquet YunoHost.

Pour installer :
```
sudo yunohost app install https://github.com/Jojo144/compteur_du_gase_ynh
```
Normalement les scripts `install`, `upgrade`, `remove`, `backup` et `restore` fonctionnent.

Pour mettre à jour :

**⚠ Faire une sauvegarde de la base de donnée (fichier db.sqlite3) avant toute mse à jour.**
```
sudo yunohost app upgrade compteur_gase -u https://github.com/Jojo144/compteur_du_gase_ynh
```
YunoHost 4.2 est requis.


### Après l'installation (quel que soit le mode d'installation)

Vous pouvez paramétrer le compteur dans l'interface d'administration :

- des catégories (Légumineuses, Conserves, ...) par défaut sont données mais vous pouvez les changer ou en ajouter,

- de même pour les unités (kg, L, buteille, ...),

- dans "Réglages divers" vous pouvez désactiver les fonctionalités non utilisées, paramétrer l'envoi d'email... etc.

**Pensez ensuite à mettre en place des sauvegardes.** (voir paragraphe ci-dessous)


### Personalisation graphique

Pour utiliser un logo, activez l'option dans les réglages divers puis :
```
cd /opt/compteur_gase
cp /bla/bla/bla/logo.png base/static/base/
sudo -u compteur_gase venv/bin/python3 manage.py collectstatic
```

Pour personnaliser l'interface graphique, il est aussi possible de créer un fichier
`local.css` dans le répertoire contenant le fichier `base.css`.


### Gestion des comptes utilisateurices admin

Accessible depuis l'admin elle-même, on peut créer/changer les comptes admin.

NB : si on utilise YunoHost, la gestion des utilisateurices se fait via YunoHost,
et les comptes ne sont pas accessibles dans l'admin du compteur.


### Notes sur l'intégration YunoHost

L'intégration YunoHost est optionelle, elle est désactivée si l'application
n'est pas installée via le package YunoHost.

L'intégration YunoHost consiste en un mécanisme d'installation et une
intégration de l'authentification permetant au compteur d'exploiter les comptes
utilisateur YunoHost.

Il y a deux permissions pour chaque instance du compteur :
  - une pour la page d'accueil (et le tableau des permanences)
  - une pour le reste du logiciel

Pour chacune de ces permissions on peut définir qui peut y accéder (n'importe
qui/n'importe quel utilisateur loggué/des utilisateurs d'un certain groupe) via
l'interface d'administration de YunoHost.

La confguration par défaut est que n'importe qui peut accéder à l'accueil mais
seuls les membres authentifiés (de n'importe quel groupe) peuvent avoir accès au
reste du compteur.

Remarque : pour avoir accès au logiciel entier il est nécessaire d'avoir *les deux*
permissions. Si on ne donne que la seconde ça ne va pas marcher...

Les utilisateurs qui n'ont accès qu'à la page d'accueil peuvent consulter et
modifier le tableau des permanences. Par contre, les mails et numéros de téléphone
ne s'afficherons pas pour les visiteurs (utilisateurs non authentifiés sur
l'instance).


Tous les utilisateurs autorisés à accéder à une instance du compteur sont
administrateurs de cette instance, i.e. peuvent accéder à l'interface
d'administration de Django (via "Gestion > Interface d'administration").


## Sauvegardes

Il faut sauvegarder le fichier `db.sqlite3` qui se trouve là où est installée votre
application (dans `/opt/compteur_gase` par exemple). C'est lui qui contient la base
de donnée, c'est à dire toutes les données enregistrées dans le logiciel (membres,
achats, ...).

Vous pouvez utiliser le mécanisme de sauvegarde qui vous plait mais nous vous
recommandons chaudement de mettre en place des sauvegardes automatiques et
fréquentes.

Par exemple en faisant une copie sur un serveur distant (scp ou cp dans un dossier
Nextcloup) ou en le copiant sur une clé USB (cp).

Pour faire une sauvegarde automatique (exemple tous les jours ou toutes les heures)
vous pouvez utiliser [cron](https://fr.wikipedia.org/wiki/Cron).

Si vous utilisez YunoHost vous pouvez utiliser le script `backup` fourni mais un
petit `cp` de la base de donnée supplémentaire ne peut pas faire de mal.


## Mise à jour

Au début je sais plus et après :

`sudo -u compteur_gase venv/bin/python3 manage.py migrate`


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


## Export de certaines tables

Il est possible d'exporter certaines tables :
```
manage.py export_products /path/to/filename.xlsx
manage.py export_providers /path/to/filename.xlsx
manage.py export_households /path/to/filename.xlsx
```


## Contributions

Toutes les remarques et contributions sont les bienvenues. N'hésitez pas à entrer en contact avec nous si vous souhaitez l'installer dans votre épicerie.

Pour le développement, des détails techniques sont disponibles dans le fichier [HACKING.md](./HACKING.md)

Contact : jojo144@girole.fr


## Crédits

- Favicon made by Freepik from www.flaticon.com
- Bootstrap4 Select2 theme CSS is from [BootStrap4 Select2 theme 1.3.2](https://github.com/ttskch/select2-bootstrap4-theme)
