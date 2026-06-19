# 📋 Guide Utilisateur — Module Gestion Immobilière MILA

**Version :** 3.2 | **Plateforme :** mila.afroit.net | **Date :** Juin 2026

---

## 🔐 Accès à la plateforme

| Champ | Valeur |
|-------|--------|
| **Adresse** | https://mila.afroit.net |
| **Identifiant client** | `client` |
| **Mot de passe** | `client123` |

> **Conseil :** Utilisez Google Chrome ou Mozilla Firefox pour une meilleure expérience.

---

## 🏠 Présentation générale

Le module **Gestion Immobilière** est accessible depuis l'icône **Immobilier** sur l'écran d'accueil d'Odoo.

Il se compose de 5 grandes sections :

| Section | Description |
|---------|-------------|
| 📊 **Tableau de bord** | Vue d'ensemble globale et KPIs |
| 🏢 **Patrimoine** | Gestion des immeubles et biens |
| 📄 **Locations** | Gestion des baux et locataires |
| 🔧 **Interventions** | Suivi des services et travaux |
| ⚙️ **Configuration** | Paramètres et données de référence |

---

## 📊 1. Tableau de bord

Le tableau de bord est votre page d'accueil. Il affiche un résumé en temps réel de tout votre parc immobilier.

### Que voit-on sur le tableau de bord ?

- **KPIs (indicateurs clés)** : nombre total de biens, taux d'occupation, loyers attendus, factures impayées, pénalités en cours
- **Liste des baux actifs** : avec statut, locataire, bien, montant du loyer et délai avant expiration
- **Interventions en cours** : travaux et services planifiés
- **Alertes** : baux qui expirent bientôt, factures en retard, pénalités non facturées

### Comment rafraîchir le tableau de bord ?

Cliquez sur le bouton **« Actualiser »** en haut à droite. Le tableau se rafraîchit aussi automatiquement à une fréquence configurable dans les paramètres.

---

## 🏢 2. Patrimoine — Gestion des Immeubles et Biens

### 2.1 Les Immeubles

Un **immeuble** est le bâtiment physique qui regroupe plusieurs biens.

**Comment voir la liste des immeubles ?**
> Menu → **Patrimoine** → **Immeubles**

**Pour créer un nouvel immeuble :**
1. Cliquez sur **« Nouveau »**
2. Saisissez le **nom de l'immeuble**
3. Renseignez l'**adresse** (rue, ville, pays)
4. Désignez le **propriétaire** si applicable
5. Ajoutez une **note** si besoin
6. Cliquez **« Enregistrer »** (l'icône disquette)

### 2.2 Les Biens Immobiliers

Un **bien** est l'unité locative : appartement, bureau, terrain, parking, etc.

**Comment voir la liste des biens ?**
> Menu → **Patrimoine** → **Biens immobiliers**

Chaque bien affiche :
- Sa **référence** automatique (ex : BIEN/2026/0001)
- Son **nom** et son **type** (Résidentiel, Commercial, Terrain, Parking, Mixte)
- Le **loyer mensuel de référence**
- Son **statut** : Disponible | Occupé | En travaux

> **Important :** Le statut se met à jour **automatiquement** quand un bail est confirmé (passe à "Occupé") ou résilié (revient à "Disponible").

**Pour créer un nouveau bien :**
1. Cliquez sur **« Nouveau »**
2. Saisissez le **nom** du bien
3. Sélectionnez le **type** (résidentiel, commercial, etc.)
4. Choisissez l'**immeuble parent**
5. Renseignez la **surface (m²)**, le nombre de **pièces**, de **salles de bain**
6. Indiquez le **loyer mensuel de référence** en CFA
7. Ajoutez une **description** dans l'onglet Description
8. Enregistrez

**Fiche détail d'un bien :**
- Onglet **Description** : texte libre de présentation
- Onglet **Équipements** : liste des équipements inclus
- Bouton **« Baux »** : accès aux contrats liés à ce bien
- **Chatter** (à droite) : historique de toutes les actions

---

## 📄 3. Locations — Gestion des Baux

### 3.1 Créer un nouveau bail

> Menu → **Locations** → **Baux Actifs** → **« Nouveau »**

**Étapes de création d'un bail :**

1. **Sélectionner le bien immobilier** à louer
2. **Sélectionner le locataire** (contact Odoo existant ou à créer)
3. Renseigner le **type de bail** : Mensuel, Annuel, Commercial, Saisonnier
4. Choisir le **plan de récurrence** : Mensuel, Trimestriel, Semestriel, Annuel
5. Indiquer la **date de début** et la **date de fin** du contrat
6. Saisir le **loyer mensuel de base** en CFA
7. Indiquer le **dépôt de garantie**
8. Cliquer **« Enregistrer »**

### 3.2 Confirmer un bail (le rendre actif)

Après création, le bail est en statut **"Devis de bail"**. Pour l'activer :

> Dans la barre de statut : cliquer sur **« En cours (Actif) »**

Le bail passe à l'état actif, le bien associé devient automatiquement **"Occupé"**, et le système génère les lignes de facturation.

### 3.3 Comprendre la fiche bail

La fiche bail contient :

**Section CONTRAT :**
| Champ | Description |
|-------|-------------|
| Bien immobilier | Le logement ou bureau loué |
| Locataire principal | Le signataire du bail |
| Réf. Locataire | Référence unique du locataire |
| Garant | Personne se portant caution |
| Type de bail | Mensuel, Commercial, etc. |
| Plan de récurrence | Fréquence de facturation |
| Dates | Début et fin du contrat |

**Section FINANCIER :**
| Champ | Description |
|-------|-------------|
| Loyer mensuel de base | Montant du loyer en CFA |
| Dépôt de garantie | Caution versée à la signature |
| Total à la signature | Dépôt + avances |
| Prochaine échéance | Date de la prochaine facture |

**Onglets en bas de la fiche :**
- **Facturation** : lignes de loyer de base et services inclus
- **Taxes & Épargne** : gestion des taxes et règles d'épargne
- **Docs & Signatures** : documents contractuels et signatures électroniques

### 3.4 Actions disponibles sur un bail actif

| Bouton | Action |
|--------|--------|
| **Calculer pénalités** | Lance le calcul automatique des pénalités de retard |
| **Résilier** | Ferme le bail avec une date et un motif |
| **Pénalités** | Voir les pénalités associées à ce bail |
| **Avenant** | Modifier les termes du bail (loyer, durée) avec traçabilité |
| **Renouveler** | Créer un renouvellement du bail en cours |
| **Suspendre** | Mettre le bail en pause temporairement |

### 3.5 Pénalités de retard

Les pénalités peuvent être créées manuellement ou calculées automatiquement.

**Calcul automatique :**
> Dans la fiche bail → cliquer **« Calculer pénalités »**

Le système analysera les factures en retard et calculera les pénalités selon les règles configurées (montant fixe ou pourcentage).

**Statuts d'une pénalité :**
- Brouillon : pénalité calculée, non encore validée
- Confirmée : validée, en attente de facturation
- Facturée : intégrée à une facture
- Annulée : annulée sans suite

### 3.6 Avenant (modification du bail)

Un **avenant** permet de modifier les termes d'un bail en cours (ex : augmentation du loyer) **sans créer un nouveau bail** et avec traçabilité complète.

1. Cliquer sur **« Avenant »** dans la fiche bail
2. Indiquer la nature et la date de l'avenant
3. Modifier les paramètres (loyer, durée, etc.)
4. Valider

L'historique complet des modifications est conservé dans le chatter.

---

## 🔧 4. Interventions — Services et Travaux

### 4.1 Voir les interventions

> Menu → **Interventions** → **Services**

Chaque intervention affiche :
- Sa **référence** (ex : INT/2026/0001)
- Son **intitulé** et le **bien** concerné
- Le **type** : Réparation, Maintenance, Rénovation, Inspection, etc.
- Sa **priorité** : Normal | Urgent | Critique | Bloquant
- Les **dates** demandée et planifiée
- Le **coût estimé** en CFA
- Son **statut** : Demande → Soumise → Approuvée → En cours → Validée → Clôturée

### 4.2 Créer une intervention

1. Cliquer **« Nouveau »**
2. Saisir l'**intitulé** de l'intervention
3. Sélectionner le **bien** concerné
4. Choisir le **type** d'intervention
5. Définir la **priorité**
6. Indiquer les **dates** (demande et planification)
7. Renseigner le **coût estimé**
8. Décrire les travaux dans **Description**
9. Enregistrer

### 4.3 Cycle de vie d'une intervention

```
Demande → Soumise → Approuvée → En cours → En attente validation → Validée → Facturée → Clôturée
```

Chaque étape peut être franchie via les boutons d'action en haut de la fiche.

---

## ⚙️ 5. Configuration

> Menu → **Configuration**

### 5.1 Types de taxes

Configurez les taxes applicables aux loyers (TVA, etc.) pour qu'elles s'appliquent automatiquement lors de la facturation.

### 5.2 Plans de récurrence

Définissez les fréquences de facturation disponibles (ex : Mensuel, Trimestriel, Semestriel, Annuel).

### 5.3 Motifs de résiliation

Personnalisez les motifs de résiliation de bail pour les rapports et le suivi.

### 5.4 Paramètre de rafraîchissement du tableau de bord

Pour configurer la fréquence d'auto-refresh du tableau de bord :
> Menu → **Configuration** → **Paramètres techniques** → Rechercher `re.dashboard.refresh_interval`

La valeur est en **secondes** (défaut : 60 secondes).

---

## 💬 6. Communications

### 6.1 Le Chatter Odoo (messages internes)

Chaque fiche (bien, bail, intervention) dispose d'un **chatter** sur la droite. Il permet :
- D'envoyer un **message** aux membres de l'équipe
- D'ajouter une **note** interne
- De planifier une **activité** (appel, réunion, etc.)
- De voir l'**historique** complet des modifications

**Pour envoyer un message :**
1. Cliquer **« Envoyer message »** en haut du chatter
2. Tapez votre message
3. Ajoutez des **abonnés** si nécessaire (ils recevront une notification)
4. Cliquer **« Envoyer »**

### 6.2 Notifications email

Les parties prenantes reçoivent des notifications par email automatiquement pour :
- La confirmation d'un bail
- Les relances de paiement
- Les pénalités appliquées
- Les interventions assignées

---

## 📱 7. Conseils pratiques

### Rechercher rapidement

La barre de **recherche** en haut de chaque liste permet de filtrer par nom, référence, locataire, etc.

### Filtres et regroupements

Cliquez sur la flèche à côté de la barre de recherche pour accéder aux **filtres** prédéfinis et aux **regroupements** (par statut, par bien, par mois, etc.).

### Vues liste et kanban

En haut à droite de chaque liste, vous pouvez basculer entre :
- **Vue liste** : affichage en tableau
- **Vue kanban** : affichage en cartes (idéal pour les baux et interventions)

---

## ❓ 8. Questions fréquentes

**Q : Le statut de mon bien n'a pas changé après avoir créé un bail, que faire ?**
> Vérifiez que le bail a bien été **confirmé** (cliquer sur "En cours (Actif)" dans la barre de statut). Le statut du bien se met à jour automatiquement à la confirmation.

**Q : Je ne vois pas le tableau de bord, que faire ?**
> Cliquez sur le menu **Immobilier** dans la barre de navigation, puis sur **Tableau de bord**.

**Q : Comment savoir quelles factures sont en retard ?**
> Le tableau de bord affiche les alertes de factures en retard. Vous pouvez aussi aller dans **Locations** et filtrer par "En retard".

**Q : Peut-on modifier un bail actif sans le résilier ?**
> Oui, utilisez le bouton **Avenant** sur la fiche du bail. Cela crée une modification tracée sans interrompre le bail.

**Q : Comment générer un reçu ou une quittance de loyer ?**
> Depuis la fiche du bail, cliquez sur **Menu Actions** → **Imprimer** → **Quittance de loyer**.

---

## 📞 Support

Pour toute question ou assistance technique :

**AFRO IT**
- Email : contact@afroit.net
- Site : afroit.net

---

*Document rédigé par AFRO IT — Juin 2026 — MILA Immobilier v3.2*
