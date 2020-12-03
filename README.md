# Le Compteur du Gase (CdG)
*Logiciel pour gérer une épicerie autogéreé !*

## Présentation

Le Compteur du Gase Gestion permet de gérer les comptes et stocks d'un GASE (Groupement d'Achat en Service Épicerie, une épicerie autogérée).
Le logiciel est pensé pour les groupements d’achats / épiceries fonctionnant de la façon suivante :
    • Chaque adhérent a un compte qu’il crédite.
    • Quand on fait des courses, on entre dans le logiciel ce que l’on achète (à la manière d’un logiciel de caisse) et cela débite notre compte en conséquence.
    • Le logicel met aussi à jour les stocks et propose un suivi de ceux-ci.
Il permet de gérer les stocks, les comptes des adhérents et la liste des adhérents.

## Historique

Depuis quelques années, les trois GASEs (des épiceries autogérées) de Nantes utilisent le logiciel ([MoneyCoop](https://github.com/barchstien/gase-web)).
Le Compteur du GASE est une réécriture du logiciel MoneyCoop pour en refaire une version plus moderne, plus pratique, avec de
superbes statistiques et avec un meilleur nom !

MoneyCoop a été écrit en ~ 2012 par Pascal L. pour l'épicerie l'indépendante à Paris 18ème.
Cette épicerie consistait deux gros placards au fond d'une salle de réunion et une permanence par semaine.
Au début, les comptes étaient fait avec une feuille Excel mais ça c'est rapidement révélé ingérable.
Comme ils avaient peu de temps le logiciel était en ligne et chacun enregistrait ses achats chez soi, de sorte de consacrer tout le temps des permanences à l'échange, et à l'organisation (commandes).
L'indépendante a été influencée par le GASE de Rochefort en Terre. Puis d'autres groupement on demandé les sources de MoneyCoop pour l'utiliser, notamment à Nantes via une personne qui était à l'indépendante avant, à Champigny...
Deux principes ont guidé l'écriture du logiciel : "tout le monde doit pouvoir tout faire" (même mot de passe pour tous), "simple et robuste" (par exemple pas possible de supprimer des choses pour éviter les erreurs).

Il n'y avait pas de statistiques dans la version de base, cela a probablement été rajouté par les Nantais.

Version de démo ici : https://test-compteur.girole.fr

## Configuration

Ce logiciel peut être utilié tel quel.

Néanmoins, pour personnaliser l'interface graphique, il faut créer un fichier local.css dans le répertoire contenant le fichier base.css.

Différentes options sont également disponibles dans l'interface graphique dans Gestion>Interface d'administration>Réglages divers.

## Contributions

Toutes les remarques et contributions sont les bienvenues. N'hésitez pas à entrer en contact avec moi si vous souhaitez l'installer dans votre épicerie.

Pour le développement, des détails techniques sont disponibles dans le fichier [HACKING.md](./HACKING.md)

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

Attention, si vous tombez sur une page Apache "It works" c'est que vous avez Apache d'installé au lieu de Nginx (ou les deux).

### Installation en ligne

Paquet Yunohost.
```
sudo yunohost app install https://github.com/Jojo144/compteur_du_gase
```
Pour le moment seuls les scripts `install`, `upgrade` `remove` fonctionne.

Pour mettre à jour :
```
sudo yunohost app upgrade compteur_gase -u https://github.com/Jojo144/compteur_du_gase
```

### Après l'installation (quel que soit le mode d'installation)

À la première utilisation il faut aller dans l'interface administration pour 

- créer des unités (en général : kg, L, bouteille, sachet, pot) et des catégories (par ex :
Légumineuses, Conserves, Non alimentaire, ...).
- réaliser divers paramétrages (désactiver les fonctionalités non utilisées, paramétrer l'envoi d'email… etc).

Puis c'est parti !

Pensez ensuite à mettre en place une sauvegarde.

Exemples d'unités :

        Vrac  Pluriel
unité	    0     0
kg	        1     0
L	        1     0
tablette    0     1
sachet	    0     1
bouteille   0     1
pot         0     1


## Sauvegarde de la base de donnée

Il faut sauvegarder le fichier `db.sqlite3` qui se trouve là où est installée votre application
(dans `/opt/compteur_gase` par exemple).


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

Il est possibles d'exporter certaines tables :
```
manage.py export_products /path/to/filename.xlsx
manage.py export_providers /path/to/filename.xlsx
manage.py export_households /path/to/filename.xlsx
```

## Credits

- Favicon made by Freepik from www.flaticon.com
- Bootstrap4 Select2 theme CSS is from [BootStrap4 Select2 theme 1.3.2](https://github.com/ttskch/select2-bootstrap4-theme)
