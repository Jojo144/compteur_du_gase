# Coder sur le compteur du GASE

## Environnement de développement

Il est recommandé d'utiliser des paramètres personalisés pour le dév :

    cp compteur/settings_local.py.dev.example compteur/settings_local.py

## Pour mettre à jour en testant une branche

Pour mettre à jour :
```
sudo yunohost app upgrade compteur_gase -u https://github.com/Jojo144/compteur_du_gase/tree/MA-BRANCHE
```
