# TODO

- [ ] documenter l'install, l'histoire du logiciel
- [ ] doc backups
- [ ] doc màj
- [x] liste + création/modif des fournisseurs (dans Gestion)
- [x] voir adresse du foyer qqpart (soit liste membres soit détail membre)
- [x] historique des appro compte
- [x] mettre un seuil en dessous duquel on ne peut plus faire d'achats (ne reste qu'à valider)
- [x] mettre timeout / try-catch sur l'envoi de mail
- [x] EXPLICITER LEs INVARIANTS DE LA BASE
- [ ] vérifier l'intégrité de la base (stock pdt = somme des ope, solde membre = somme de ope) et sinon reporter une erreur par mail à l'admin
- [x] afficher valeur du stock (total/par référence/par rayon) (documenter)
- [x] documenter inventaire
- [x] bilan inventaire
- [x] des belles stats !
- [x] lien vers l'admin + expliquer comment elle fonctionne
- [x] désactiver mpd admin ? -> non ça al'air trop relou
- [x] références non visible (doc) -> filtre dans liste des pdts + non listés dans achat
- [x] gérer plusieurs unités (L / kg / sachet / bouteille) mais pas les grammmes sinon on va s'y perdre !
- [x] création / modif foyer + membres (pour l'instant faisable via l'admin)
- [x] ne pas définir price comme une property dans model des ope
- [x] bouton "abandonner" sur page achats
- [x] doc création des catégories dans l'admin
- [x] achat : "valider formulaire" (erreur quand ce n'est pas un nombre + entier quand non vrac)
- [x] pouvoir avoir plusieurs référents pour un pdt -> plutôt non (pas trop de fonctions)
- [x] page appro stock : montrer le prix des références (+ pourquoi pas stock actuel)
- [x] que se passe-t-il si on supprime un foyer ?
- [ ] pouvoir filtrer dans l'inventaire / plus compact
- [x] envoyer un mail quand appro
- [x] unifier inventoryOp et ApproOp
- [x] check vrac à "dans panier"
- [x] supprimer une référence du panier -> icone
- [x] confirm si payer avec panier vide
- [x] quand même des meilleurs résultats d'inventaire
- [ ] réglages emails dans settings.py + test emails
- [ ] Tester / Documenter admin mail
- [x] page achat : bouton de la catégorie activée différent
- [x] plural unit
- [ ] update / backup
- [ ] migration
- [x] javascript and decimals
- [x] historique des achats (nécessite une page "foyer")
- [x] alertes stock au référent (doc)
- [x] pouvoir annuler un achat d'une façon ou d'une autre (via admin ?) (doc (dans Gestion ?))
- [x] montrer de façon un peu plus clair qu'on peut trier par colonne ? -> plutôt non
- [x] ajouter help_text pour ticket de caisse et alertes dans page membre
- [x] une liste des alertes stock
- [x] un formulaire de suggestion ? -> pas tout de suite

- [ ] découpler use_subscription et use_member_number
- [x] trier les listes de fournisseurs et catégories dasn détail pdt

## Cosmétique
- [ ] Abandonner et revenir à l'accueil -> mettre un logo
- [ ] Page produits -> non visible interrupteur sur même ligne que filtre
- [ ] détail membre/produit -> commentaire bcp plus petit
- [x] messages
- [x] formulaires de sélection de compte -> moins large
- [ ] masquer les astérisques des champs obligatoires partout
- [x] faire que les messages "Votre compte a bien été appro/débité" s'effacent au bout de qqs secondes
- [x] aligner le ♥ avec le milieu de la ligne -> même taille de police
- [ ] rendre plus clair qu'on peut créer plusieurs membres
- [ ] mettre des symboles € dans les formulaires avec des thunes
- [ ] message d'erreur quand on cherche à enregistrer un foyer sans membre pas ouf
- [ ] les alerts ne sont pas jolis


Jo:
filter(provider= vs filter(provider_id=
todo : use aggregate ?
filtre qui print stock / prix au kg


## Bugs connus
- [x] stock à 0 dans détail produit


## Pour la v2!
- [ ] plusieurs pdt pour les stats
- [ ] connection avec accès restreint
- [ ] gestion du prix libre


- [ ] dans la liste des références, on devrait pouvoir cliquer sur un fournisseur pour en voir les détails
- [ ] partout autoriser le . et la , comme séparateur décimal
- [ ] achat + appro sélection de son compte au clavier
- [ ] valeur du stock d'une catégorie
- [ ] afficher bilan au fur à mesure (ou pour chaque produit) pour inventaire
- [ ] ne pas envoyer plusieurs fois la même alerte stock



import ipdb; ipdb.set_trace()
l  ---> élargir le contexte
n  ---> passer à la ligne suivante
q  ---> quitter sauvagement
c  ---> continuer l'exécution du programme jusqu'à sa fin
s  ---> rentre dans la fonction de la ligne en cours
r  ---> execute un return



Pour devs :
provider.html et product.html sont utilisés our la création ET pour le détail
