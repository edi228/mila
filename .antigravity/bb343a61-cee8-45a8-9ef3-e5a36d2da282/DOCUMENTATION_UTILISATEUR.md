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

Une fois connecté, cliquez sur l'icône **Immobilier** pour accéder au module.

---

## 🏠 Présentation générale

Le module **Gestion Immobilière** se compose de 5 grandes sections accessibles depuis la barre de navigation :

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

![Tableau de bord Immobilier](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/01_dashboard.png)

### Ce que vous voyez sur le tableau de bord

**Ligne des KPIs (indicateurs clés) :**
- **Biens totaux** : nombre total de biens dans votre parc, avec le détail (disponibles / en travaux)
- **Taux d'occupation** : pourcentage de biens actuellement loués
- **LMR Global** : total des loyers mensuels des baux actifs
- **Impayés** : montant total des factures en retard
- **Pénalités actives** : montant des pénalités en cours

**Tableau des baux actifs :** liste de tous vos baux en cours avec le bien, le locataire, le loyer mensuel, la prochaine échéance de facturation, et un indicateur visuel du temps restant (rouge si moins de 30 jours, orange si moins de 60 jours, vert sinon).

**Panneau de droite :**
- **Alertes & Rappels** : baux qui expirent bientôt, pénalités non traitées, factures en retard
- **Interventions en cours** : liste des travaux et services planifiés avec statut et priorité

### Comment rafraîchir le tableau de bord ?

Cliquez sur le bouton **« Actualiser »** en haut à droite. Le tableau se rafraîchit aussi **automatiquement toutes les 60 secondes** (durée configurable dans les paramètres).

---

## 🏢 2. Patrimoine — Gestion des Immeubles et Biens

### 2.1 Les Biens Immobiliers

Un **bien** est l'unité locative : appartement, bureau, terrain, parking, etc.

**Comment voir la liste des biens ?**
> Menu → **Patrimoine** → **Biens immobiliers**

![Liste des Biens Immobiliers](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/02_properties_list.png)

La liste affiche pour chaque bien :
- Sa **référence** automatique (ex : BIEN/2026/0001)
- Son **nom** et son **type** (Résidentiel, Commercial, Terrain, Parking, Mixte)
- L'**immeuble** auquel il appartient
- Le **loyer mensuel de référence** en CFA
- Son **statut** : Disponible | Occupé | En travaux

> **À savoir :** Le statut se met à jour **automatiquement** quand un bail est confirmé (passe à "Occupé") ou résilié (revient à "Disponible"). Vous n'avez rien à faire manuellement.

### 2.2 Fiche détail d'un bien

![Fiche d'un Bien Immobilier](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/03_property_form.png)

La fiche d'un bien contient :

- **Référence et nom** du bien en en-tête
- **Type, immeuble parent, propriétaire** à gauche
- **Loyer de référence, surface, nombre de pièces** à droite
- **Barre de statut** (Disponible / Occupé) en haut
- **Bouton « Baux »** : accès direct aux contrats liés à ce bien
- Onglet **Description** : texte libre de présentation du bien
- Onglet **Équipements** : liste des équipements inclus
- **Chatter** (à droite) : historique complet de toutes les modifications (qui a fait quoi, quand)

**Pour créer un nouveau bien :**
1. Cliquez sur **« Nouveau »** en haut à gauche
2. Saisissez le **nom** du bien
3. Sélectionnez le **type** (résidentiel, commercial, etc.)
4. Choisissez l'**immeuble parent**
5. Renseignez la **surface (m²)** et le nombre de **pièces**
6. Indiquez le **loyer mensuel de référence** en CFA
7. Ajoutez une **description** dans l'onglet Description
8. Cliquez sur **« Enregistrer »**

---

## 📄 3. Locations — Gestion des Baux

### 3.1 Liste des baux

> Menu → **Locations** → **Baux Actifs**

![Liste des Baux Actifs](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/04_leases_list.png)

La liste affiche tous vos baux en cours : référence, bien, locataire, date de début, loyer et statut.

### 3.2 Fiche détail d'un bail

![Fiche d'un Bail](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/05_lease_form.png)

La fiche d'un bail contient deux grandes sections :

**Section CONTRAT :**
| Champ | Description |
|-------|-------------|
| Bien immobilier | Le logement ou bureau loué |
| Locataire principal | Le signataire du bail |
| Réf. Locataire | Référence unique du locataire dans le système |
| Garant | Personne se portant caution |
| Type de bail | Mensuel, Annuel, Commercial ou Saisonnier |
| Plan de récurrence | Fréquence de facturation (Mensuel, Trimestriel...) |
| Date de début / de fin | Durée du contrat |

**Section FINANCIER :**
| Champ | Description |
|-------|-------------|
| Loyer mensuel de base | Montant du loyer en CFA |
| Dépôt de garantie | Caution versée à la signature |
| Total à la signature | Dépôt + avances |
| Prochaine échéance | Date de la prochaine facture |

**Barre de statut :** Devis de bail → **En cours (Actif)** → Résilié

**Onglets en bas :**
- **Facturation** : lignes de loyer et services inclus
- **Taxes & Épargne** : taxes applicables et règles d'épargne
- **Docs & Signatures** : documents contractuels

### 3.3 Créer un nouveau bail

1. Cliquez sur **« Nouveau »**
2. Sélectionnez le **bien immobilier** à louer
3. Sélectionnez le **locataire** (ou créez-le)
4. Renseignez le **type de bail** et le **plan de récurrence**
5. Indiquez la **date de début** et la **date de fin**
6. Saisissez le **loyer mensuel de base** et le **dépôt de garantie**
7. Cliquez **« Enregistrer »**

### 3.4 Activer un bail

Après création, le bail est en statut **"Devis de bail"**. Pour le rendre actif :

> Cliquer sur **« En cours (Actif) »** dans la barre de statut

Le bail passe à l'état actif et le bien associé devient automatiquement **"Occupé"**.

### 3.5 Actions disponibles sur un bail actif

| Bouton | Action |
|--------|--------|
| **Calculer pénalités** | Calcul automatique des pénalités de retard |
| **Résilier** | Clôturer le bail avec date et motif |
| **Pénalités** | Voir toutes les pénalités de ce bail |
| **Avenant** | Modifier les termes sans créer un nouveau bail |
| **Renouveler** | Renouveler le bail à son expiration |
| **Suspendre** | Suspendre temporairement le bail |

### 3.6 Les Pénalités de retard

Les pénalités se créent depuis la fiche du bail :
> Cliquer **« Calculer pénalités »** → le système analyse les factures en retard et applique les règles configurées

**Cycle de vie d'une pénalité :**
```
Brouillon → Confirmée → Facturée
```

### 3.7 Les Avenants (modifications de bail)

Un avenant permet de modifier le loyer, la durée ou d'autres termes **sans interrompre le bail**. Toute modification est tracée dans le chatter avec la date et l'auteur.

---

## 🔧 4. Interventions — Services et Travaux

### 4.1 Liste des interventions

> Menu → **Interventions** → **Services**

![Liste des Interventions](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/06_interventions_list.png)

Chaque intervention affiche :
- Sa **référence** (INT/2026/0001...)
- Son **intitulé** et le **bien** concerné
- Le **type** : Réparation, Maintenance, Rénovation, Inspection...
- Sa **priorité** (étoiles) : Normal / Urgent / Critique / Bloquant
- Les **dates** demandée et planifiée
- Le **coût estimé** en CFA
- Son **statut** : Demande / Soumise / Approuvée / En cours / Validée / Clôturée

### 4.2 Fiche détail d'une intervention

![Fiche d'une Intervention](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/07_intervention_form.png)

### 4.3 Créer une intervention

1. Cliquer **« Nouveau »**
2. Saisir l'**intitulé** (ex : "Réparation fuite robinet cuisine")
3. Sélectionner le **bien** concerné
4. Choisir le **type** d'intervention
5. Définir la **priorité** (1 à 4 étoiles)
6. Indiquer les dates de **demande** et de **planification**
7. Renseigner le **coût estimé**
8. Décrire les travaux dans **Description**
9. Enregistrer

### 4.4 Cycle de vie d'une intervention

```
Demande → Soumise → Approuvée → En cours → En attente validation → Validée → Facturée → Clôturée
```

---

## ⚙️ 5. Configuration

> Menu → **Configuration**

Cette section permet de personnaliser le module selon vos besoins :

- **Types de taxes** : taxes applicables aux loyers (ex : TVA)
- **Plans de récurrence** : fréquences de facturation disponibles
- **Motifs de résiliation** : causes de fin de bail pour vos rapports

### Paramètre de rafraîchissement du tableau de bord

Pour changer la fréquence d'auto-refresh :
> **Configuration** → **Paramètres techniques** → rechercher `re.dashboard.refresh_interval`

La valeur est en **secondes**. Par défaut : **60 secondes**.

---

## 💬 6. Communications et suivi

### Le Chatter (messagerie interne)

Chaque fiche dispose d'un **chatter** sur la droite de l'écran. Il permet de :
- **Envoyer un message** à un collaborateur (qui reçoit une notification)
- **Ajouter une note** interne (non envoyée)
- **Planifier une activité** : appel téléphonique, réunion, relance...
- **Voir l'historique** complet : qui a modifié quoi et quand

**Pour envoyer un message :**
1. Cliquer **« Envoyer message »**
2. Saisir le message
3. Mentionner une personne avec **@nom** si besoin
4. Cliquer **« Envoyer »** — la personne reçoit une notification par email

### Notifications automatiques

Le système envoie des emails automatiquement lors de :
- La confirmation d'un bail
- L'approche de l'expiration d'un bail (alerte visible sur le dashboard)
- L'application de pénalités

---

## 📱 7. Conseils pratiques

### Recherche rapide

La barre de **recherche** (en haut de chaque liste) permet de filtrer par nom, référence, locataire, etc.

### Filtres et regroupements

Cliquer sur la flèche **▼** à côté de la barre de recherche pour accéder aux **filtres** prédéfinis (ex : "Baux actifs", "Biens occupés") et aux **regroupements** (par statut, par mois, par bien...).

### Vue liste et vue kanban

En haut à droite de chaque liste, basculez entre :
- **Vue liste** (≡) : tableau classique
- **Vue kanban** (⊞) : cartes visuelles, idéal pour les baux et interventions

---

## ❓ 8. Questions fréquentes

**Q : Le statut de mon bien n'a pas changé après avoir créé un bail ?**
> Vérifiez que le bail a bien été **confirmé** : cliquer sur "En cours (Actif)" dans la barre de statut. Le statut du bien se met à jour automatiquement à la confirmation.

**Q : Je ne vois pas le tableau de bord ?**
> Cliquez sur le menu **Immobilier** dans la barre de navigation du haut, puis **Tableau de bord**.

**Q : Peut-on modifier un bail actif sans le résilier ?**
> Oui : utilisez le bouton **Avenant** sur la fiche du bail. Cela crée une modification tracée sans interrompre le bail.

**Q : Comment voir les baux qui expirent bientôt ?**
> Le tableau de bord affiche les alertes dans le panneau **Alertes & Rappels** à droite. Les baux à moins de 30 jours apparaissent en rouge.

**Q : Comment calculer les pénalités de retard ?**
> Sur la fiche du bail concerné, cliquer **« Calculer pénalités »**. Le système calcule automatiquement les montants selon les règles configurées.

---

## 📞 Support

Pour toute question ou assistance technique :

**AFRO IT**
- Email : contact@afroit.net
- Site : afroit.net

---

*Document rédigé par AFRO IT — Juin 2026 — MILA Immobilier v3.2*
