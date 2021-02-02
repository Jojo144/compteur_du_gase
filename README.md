# Le Compteur du Gase (CdG)
*Logiciel pour gérer une épicerie autogéreé !*

## Présentation

Le Compteur du Gase Gestion permet de gérer les comptes et stocks d'un GASE (Groupement d'Achat en Service Épicerie, une épicerie autogérée).
Le logiciel est pensé pour les groupements d’achats / épiceries fonctionnant de la façon suivante :
    • Chaque adhérent a un compte qu’il crédite.
    • Quand on fait des courses, on entre dans le logiciel ce que l’on achète (à la manière d’un logiciel de caisse) et cela débite notre compte en conséquence.
    • Le logiciel met aussi à jour les stocks et propose un suivi de ceux-ci.
Il permet de gérer les stocks, les comptes des adhérents et la liste des adhérents.


## Capture d'écran

![Capture d'écran](/screenshot/Screenshot_2021-12-26_Le-compteur-du-GASE.png)


## Historique

Depuis quelques années, les trois GASE (des épiceries autogérées) de Nantes utilisent le logiciel ([MoneyCoop](https://github.com/barchstien/gase-web)).
Le Compteur du GASE est une réécriture du logiciel MoneyCoop pour en refaire une version plus moderne, plus pratique, avec de
superbes statistiques et avec un meilleur nom !

MoneyCoop a été écrit en ~ 2012 par Pascal L. pour l'épicerie l'indépendante à Paris 18ème.
Cette épicerie consistait deux gros placards au fond d'une salle de réunion et une permanence par semaine.
Au début, les comptes étaient faits avec une feuille Excel mais ça s'est rapidement révélé ingérable.
Comme ils avaient peu de temps le logiciel était en ligne et chacun enregistrait ses achats chez soi, de sorte de consacrer tout le temps des permanences à l'échange, et à l'organisation (commandes).
L'indépendante a été influencée par le GASE de Rochefort en Terre. Puis d'autres groupements ont demandé les sources de MoneyCoop pour l'utiliser, notamment à Nantes via une personne qui était à l'indépendante avant, à Champigny...
Deux principes ont guidé l'écriture du logiciel : "tout le monde doit pouvoir tout faire" (même mot de passe pour tous), "simple et robuste" (par exemple pas possible de supprimer des choses pour éviter les erreurs).

Il n'y avait pas de statistiques dans la version de base, cela a probablement été rajouté par les Nantais.

Version de démo ici : https://demo-compteur.gase.eu.org


## Épiceries utilisant le logiciel
| Épicerie                  | Description                                                                                                                                                               | Utilise le compteur depuis | Contact                                                                        |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|--------------------------------------------------------------------------------|
| Le GASE de l'Esclain      | Épicerie associative autogérée, quartier Beauséjour à Nantes                                                                                                              | février 2021               | bonjour (arrrobase) gasedelesclain.fr                                          |
| Le GASE à Roulettes       | GASE 100% bénévole et autogéré à Nantes centre                                                                                                                            | mai 2020                   | commission informatique : informatique (puis un arobase puis) roulettes.eu.org |
| Petite Epicerie Pell'Mêle | La Petite Epicerie Pell’Mêle est une épicerie associative de produits bio (et locaux si possible) en vrac, créée en octobre 2019. https://pellmele.fr/la-petite-epicerie/ | septembre 2019             | pellmele-epicerie (arrobase) retzien.fr                                        |
| Le Gasouillis             | Une épicerie associative à Guénouvry (44 Guémené-Penfao)                                                                                                                  | septembre 2021             | gasouillis (arrobase) tutanota.com                                             |

Si vous utilisez le Compteur du Gase et que vous acceptez d'apparaître sur cette liste, merci d'envoyer un mail à jojo144@girole.fr .


## Contributions

Toutes les remarques et contributions sont les bienvenues. N'hésitez pas à entrer en contact avec moi si vous souhaitez l'installer dans votre épicerie.

Pour le développement, des détails techniques sont disponibles dans le fichier [HACKING.md](./HACKING.md)

Contact : jojo144@girole.fr


## Installation

Deux façons d'installer le logiciel : soit en local sur Debian/Ubuntu, soit en ligne avec [Yunohost](https://yunohost.org).

Le compteur du GASE est une application écrite en [Django](https://www.djangoproject.com/), un framework Python pour écrire des applications web.
Dans les deux cas, il sagit donc d'installer un serveur web (Nginx) et de faire tourner Gunicorn.

### Installation en local

Testé sur Ubuntu 19.04. Il suffit d'exécuter le script `local_install.sh` qui fait tout ce qu'il faut.
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

Après une migration Stretch -> Buster on a eu besoin de reconstruire les venv :

```
cp db.sqlite3 ~/db-back.sqlite3
rm -rf venv/
sudo -u compteur_gase__X bash
python3 -m venv venv
source venv/bin/activate
pip install gunicorn
pip install -r requirements.txt
systemctl restart compteur_gase__X
```


### Après l'installation (quel que soit le mode d'installation)

Vous pouvez paramétrer le compteur dans l'interface d'administration.

- Des catégories (Légumineuses, Conserves, ...) par défaut sont données mais vous pouvez les changer ou en ajouter.

- De même pour les unités (kg, L, buteille, ...).

- Dans "Réglages divers" vous pouvez désactiver les fonctionalités non utilisées, paramétrer l'envoi d'email... etc

Puis c'est parti !

**Pensez ensuite à mettre en place une sauvegarde (voir ci-dessous)**.

# Notes sur l'intégration YunoHost

L'intégration YunoHost est optionelle, elle est désactivée si l'application
n'est pas installée via le package YunoHost.

L'intégration YunoHost consiste en un mécanisme d'installation et une
intégration de l'authentification permetant au compteur d'exploiter les comptes
utilisateur YunoHost. Quelques notes concernant l'intégration de
l'authentification :

- le contrôle d'accès (quel utilisateur YunoHost peut accéder au compteur) se
  fait depuis l'admin YunoHost
- Tous les utilisateurs autorisés sont administrateurs du compteur

## Sauvegarde de la base de donnée

Il faut sauvegarder le fichier `db.sqlite3` qui se trouve là où est installée votre application
(dans `/opt/compteur_gase` par exemple). Par exemple en faisant une copie sur un serveur distant
(scp ou cp dans un dossier Nextcloup) ou en le copiant sur une clé USB (cp).

Pour faire une sauvegarde automatique (exemple tous les jours ou toutes les heures) vous pouvez
utiliser cron.


## Mise à jour

Au début je sais plus et après :

`sudo -u compteur_gase venv/bin/python3 manage.py migrate`


## Configuration

Ce logiciel peut être utilisé tel quel.

Néanmoins, pour personnaliser l'interface graphique, il faut créer un fichier local.css dans le répertoire contenant le fichier base.css.

Différentes options sont également disponibles dans l'interface graphique dans Gestion>Interface d'administration>Réglages divers.


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

## Credits

- Favicon made by Freepik from www.flaticon.com
- Bootstrap4 Select2 theme CSS is from [BootStrap4 Select2 theme 1.3.2](https://github.com/ttskch/select2-bootstrap4-theme)
