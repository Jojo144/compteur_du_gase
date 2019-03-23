# Le Compteur du Gase (CdG)
Logiciel de gestion de comptes et de stock pour un GASE (Groupement d'Achat en Service Épicerie)

# TODO
[ ] DOCUMENTER au fil des pages
[ ] documenter l'install, l'histoire du logiciel
[ ] doc backups
[ ] doc màj
[x] liste + création/modif des fournisseurs (dans Gestion)
[x] voir adresse du foyer qqpart (soit liste membres soit détail membre)
[x] historique des appro compte
[-] mettre un seuil en dessous duquel on ne peut plus faire d'achats (ne reste qu'à valider)
[ ] mettre timeout / try-catch sur l'envoi de mail
[x] EXPLICITER LEs INVARIANTS DE LA BASE
[ ] vérifier l'intégrité de la base (stock pdt = somme des ope, solde membre = somme de ope) et sinon reporter une erreur par mail à l'admin
[x] afficher valeur du stock (total/par référence/par rayon) (documenter)
[x] documenter inventaire
[x] bilan inventaire
[ ] des belles stats !
[x] lien vers l'admin + expliquer comment elle fonctionne
[ ] désactiver mpd admin ?
[ ] références non visible (doc) -> filtre dans liste des pdts + non listés dans achat
[ ] gérer plusieurs unités (L / kg / sachet / bouteille) mais pas les grammmes sinon on va s'y perdre !
[ ] création / modif foyer + membres (pour l'instant faisable via l'admin)
[-] ne pas définir price comme une property dans model des ope
[ ] bouton "abandonner" sur page achats
[x] doc création des catégories dans l'admin
[ ] achat : "valider formulaire" (erreur quand ce n'est pas un nombre)
[ ] pouvoir avoir plusieurs référents pour un pdt
[x] page appro stock : montrer le prix des références (+ pourquoi pas stock actuel)
[x] que se passe-t-il si on supprime un foyer ?
[ ] pouvoir filtrer dans l'inventaire / plus compact
[ ] afficher bilan au fur à mesure (ou pour chaque produit) pour inventaire
[ ] gérer non vrac dans achats
[ ] envoyer un mail quand appro ?
[ ] mettre des symboles € dans les formulaires avec des thunes

[ ] Rendre tout joli !

## Pour la v2!
[ ] dans la liste des références, on devrait pouvoir cliquer sur un fournisseur pour en voir les détails
[ ] historique des achats (nécessite une page "foyer")
[ ] alertes stock au référent (doc)
[ ] pouvoir annuler un achat d'une façon ou d'une autre (via admin ?) (doc (dans Gestion ?))
[ ] masquer les astérisques des champs obligatoires partout
[ ] faire que les messages "Votre compte a bien été appro/débité" s'effacent au bout de qqs secondes
[ ] partout autoriser le . et la , comme séparateur décimal
[ ] montrer de façon un peu plus clair qu'on peut trier par colonne ?
[ ] aligner le ♥ avec le milieu de la ligne
[ ] achat + appro sélection de son compte au clavier
[ ] gestion du prix libre


C'est quoi la diff entre verbose_name et 1er arg ?
filter(provider= vs filter(provider_=
null=False, default="" partout ?
