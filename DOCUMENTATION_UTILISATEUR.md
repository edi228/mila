# 📋 Guide Utilisateur — Gestion Immobilière MILA

**Version :** 3.2 | **Plateforme :** [mila.afroit.net](https://mila.afroit.net) | **Juin 2026**

---

## 🔐 Accès à la plateforme

| Champ | Valeur |
|-------|--------|
| **Adresse** | https://mila.afroit.net |
| **Identifiant** | `client` |
| **Mot de passe** | `client123` |

> Utilisez **Google Chrome** ou **Firefox** pour une expérience optimale.

Une fois connecté, cliquez sur l'icône **Immobilier** sur l'écran d'accueil.

---

## 🏠 Vue d'ensemble du module

Le module Gestion Immobilière se compose de 5 sections accessibles via la barre de navigation en haut :

| Section | Description |
|---------|-------------|
| 📊 **Tableau de bord** | Résumé en temps réel du parc immobilier |
| 🏢 **Patrimoine** | Immeubles et biens immobiliers |
| 📄 **Locations** | Baux, modèles de bail, pénalités |
| 🔧 **Interventions** | Travaux et services |
| ⚙️ **Configuration** | Plans, motifs de résiliation |

---

## 📊 1. Tableau de bord

![Tableau de bord avec données réelles](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/01_dashboard.png)

Le tableau de bord est la page d'accueil du module. Il affiche en un coup d'œil l'état complet de votre patrimoine.

### Les 5 indicateurs clés (tuiles)

Chaque tuile est **cliquable** et vous amène directement aux enregistrements concernés :

| Tuile | Ce qu'elle affiche | Cliquer pour voir |
|-------|--------------------|-------------------|
| **Biens totaux** | Nombre de biens (disponibles, en travaux) | Liste de tous les biens |
| **Taux d'occupation** | % de biens actuellement loués | Biens occupés uniquement |
| **LMR Global** | Somme des loyers des baux actifs | Liste des baux actifs |
| **Impayés** | Montant total des loyers en retard | Factures impayées |
| **Pénalités actives** | Pénalités en cours non facturées | Liste des pénalités |

> **Exemple réel :** La tuile "Impayés" affiche **150 000 CFA** (loyer Janvier 2025 de Kofi Mensah, non payé). La tuile "Pénalités actives" affiche **15 000 CFA** (pénalité de 10% calculée automatiquement).

### Tableau des baux actifs

Le tableau central liste tous vos baux en cours avec :
- Le **bien** loué (cliquable → fiche du bien)
- Le **locataire**
- Le **loyer mensuel**
- La **prochaine date de facturation**
- Le **délai avant expiration** du bail (rouge = urgent, vert = ok)

### Alertes & Rappels (panneau droit)

Affiche les situations qui nécessitent votre attention :
- Baux expirant dans moins de 30 jours
- Pénalités non traitées
- Factures en retard

### Interventions en cours

Liste les travaux planifiés avec le bien concerné, la priorité et le statut.

### Rafraîchissement

- Bouton **« Actualiser »** en haut à droite pour un rafraîchissement immédiat
- Rafraîchissement **automatique toutes les 60 secondes** (configurable)

---

## 🏢 2. Patrimoine

### 2.1 Immeubles

> **Patrimoine → Immeubles**

Un immeuble est le bâtiment qui regroupe les biens locatifs.

**Exemple de notre parc :**
- **Immeuble Palmeraie** — Avenue de la Paix, Lomé → contient 3 biens

### 2.2 Biens immobiliers

> **Patrimoine → Biens immobiliers**

![Liste des Biens Immobiliers](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/02_properties_list.png)

**Notre parc actuel :**

| Bien | Type | Loyer de référence | Statut |
|------|------|--------------------|--------|
| Appartement 3A | Résidentiel | 150 000 CFA/mois | Occupé |
| Bureau B1 | Commercial | 80 000 CFA/mois | Occupé |
| Appartement 5B | Résidentiel | 250 000 CFA/mois | En travaux |

Le statut change **automatiquement** lorsqu'un bail est confirmé ou résilié.

### Fiche d'un bien

![Fiche d'un Bien Immobilier](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/03_property_form.png)

La fiche contient :
- La **barre de statut** : Disponible / Occupé / En travaux
- Le bouton **« X Baux »** : accès direct aux baux de ce bien
- Les informations : type, immeuble, surface, loyer de référence, équipements
- Le **chatter** : historique complet des modifications

---

## 📄 3. Locations

### 3.1 Liste des baux

> **Locations → Baux Actifs**

![Liste des Baux Actifs](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/04_leases_list.png)

**Baux actifs dans notre exemple :**
- **BAIL/2026/0001** — Kofi Mensah — Appartement 3A — 150 000 CFA/mois
- **BAIL/2026/0002** — Ama Diallo — Bureau B1 — 80 000 CFA/mois

---

### 📘 CAS D'USAGE 1 : Créer un bail pour un nouveau locataire

**Contexte :** L'Appartement 5B est terminé après travaux. Un nouveau locataire, **Marcel Togbe**, souhaite louer à partir du 1er juillet 2026.

**Étapes :**

1. Aller dans **Locations → Baux Actifs** → cliquer **« Nouveau »**
2. Sélectionner le **Bien immobilier** : Appartement 5B
3. Sélectionner le **Locataire** : Marcel Togbe (ou créer le contact)
4. Choisir **Type de bail** : Mensuel
5. Choisir **Plan de récurrence** : Mensuel
6. Indiquer **Date de début** : 01/07/2026 et **Date de fin** : 30/06/2027
7. Saisir le **Loyer mensuel de base** : 250 000 CFA
8. Saisir le **Dépôt de garantie** : 500 000 CFA (2 mois)
9. Cliquer **« Enregistrer »**
10. Cliquer sur **« En cours (Actif) »** dans la barre de statut pour confirmer le bail

→ Le statut de l'Appartement 5B passe automatiquement à **Occupé**
→ Le taux d'occupation passe de 66.7% à **100%** sur le tableau de bord

---

### 3.2 Fiche détail d'un bail

![Fiche d'un Bail](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/05_lease_form.png)

La fiche bail contient les informations contractuelles complètes et les boutons d'action.

**Barre de statut :**
```
Devis de bail → En cours (Actif) → Suspendu → Résilié
```

**Boutons d'action disponibles :**

| Bouton | Utilité |
|--------|---------|
| **Calculer pénalités** | Lance le calcul des pénalités sur les factures en retard |
| **Résilier** | Met fin au bail (avec date et motif) |
| **Avenant** | Modifie les termes sans créer un nouveau bail |
| **Renouveler** | Prépare le renouvellement à l'échéance |
| **Suspendre** | Suspend temporairement le bail (ex: travaux d'urgence) |
| **X Pénalités** | Accès rapide aux pénalités du bail |

---

### 📘 CAS D'USAGE 2 : Augmenter le loyer via un Avenant

**Contexte :** Le loyer de Kofi Mensah (Appartement 3A) est de 150 000 CFA. Suite à la révision annuelle, il passe à 160 000 CFA au 1er juillet 2026.

![Dialog Avenant de bail](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/09_avenant_dialog.png)

**Étapes :**

1. Ouvrir la fiche du bail **BAIL/2026/0001**
2. Cliquer sur **« 📈 Avenant »**
3. Dans le dialog "Avenant de bail" :
   - **Type d'avenant** : Révision de loyer
   - **Date d'effet** : 01/07/2026
   - **Nouveau loyer mensuel** : 160 000 CFA
   - **Note** : Révision annuelle indexée sur l'inflation
4. Cliquer **« Appliquer l'avenant »**

→ Le bail est mis à jour avec le nouveau loyer
→ La modification est tracée dans le chatter avec la date et l'auteur
→ Les futures factures utiliseront le nouveau montant

---

### 📘 CAS D'USAGE 3 : Traiter un loyer impayé et calculer une pénalité

**Contexte :** Kofi Mensah n'a pas payé son loyer de Janvier 2025 (150 000 CFA, dû le 01/02/2025). Aujourd'hui, le retard est de 148 jours. On applique une pénalité de 10%.

**Étapes :**

1. Ouvrir la fiche du bail **BAIL/2026/0001**
2. Cliquer **« Calculer pénalités »**
3. Le wizard affiche les factures impayées et calcule automatiquement
4. Valider les pénalités proposées

→ La pénalité **PEN/2025/0001** est créée : **15 000 CFA** (10% × 150 000)

![Liste des Pénalités](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/08_penalties_list.png)

La pénalité apparaît dans la liste avec :
- Sa **référence** : PEN/2025/0001
- Le **bail** concerné : BAIL/2026/0001
- La **facture impayée** liée : INV/2025/00001
- La **date d'échéance** dépassée : 01/02/2025
- Le **montant** : 15 000 CFA
- Le **statut** : Confirmée

---

### 📘 CAS D'USAGE 4 : Renouveler un bail arrivant à expiration

**Contexte :** Le bail d'Ama Diallo (Bureau B1) expire dans 11 jours. L'alerte apparaît en rouge sur le tableau de bord.

![Dialog Renouveler le bail](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/11_renouveler_dialog.png)

**Étapes :**

1. Sur le tableau de bord, cliquer sur l'alerte rouge (BAIL/2026/0002 expire dans 11 jours)
2. Dans la fiche du bail, cliquer **« Renouveler »**
3. Dans le dialog "Renouveler le bail" :
   - **Nouvelle date de fin** : définir la nouvelle durée
   - **Nouveau loyer** (optionnel) : si révision
4. Confirmer le renouvellement

→ Le bail est mis à jour avec la nouvelle date d'expiration
→ L'alerte disparaît du tableau de bord

---

### 📘 CAS D'USAGE 5 : Résilier un bail

**Contexte :** Kofi Mensah souhaite quitter l'Appartement 3A au 31 juillet 2026.

![Dialog Résilier le bail](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/12_resilier_dialog.png)

**Étapes :**

1. Ouvrir la fiche du bail **BAIL/2026/0001**
2. Cliquer **« Résilier »**
3. Remplir le dialog :
   - **Date de résiliation** : 31/07/2026
   - **Motif** : sélectionner dans la liste (Fin de bail, Départ volontaire, etc.)
   - **Note** : informations complémentaires
4. Confirmer

→ Le bail passe en statut **Résilié**
→ L'Appartement 3A repasse automatiquement en **Disponible**
→ Le bien réapparaît comme disponible dans le tableau de bord

---

## 🔧 4. Interventions (Services et Travaux)

### 4.1 Liste des interventions

> **Interventions → Services**

![Liste des Interventions](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/06_interventions_list.png)

**Interventions en cours dans notre exemple :**

| Ref | Intitulé | Bien | Priorité | Statut |
|-----|----------|------|----------|--------|
| INT/2026/0001 | Réparation plomberie - Fuite robinet cuisine | Appartement 3A | ★★★ Urgent | En cours |
| INT/2026/0002 | Maintenance annuelle climatisation | Bureau B1 | ★☆☆ Normal | Soumise |

---

### 📘 CAS D'USAGE 6 : Déclarer et suivre une intervention urgente

**Contexte :** Le locataire de l'Appartement 3A signale une fuite d'eau dans la cuisine. Une intervention urgente est nécessaire.

![Fiche d'une Intervention](/Users/edouard/.gemini/antigravity/brain/bb343a61-cee8-45a8-9ef3-e5a36d2da282/screenshots/07_intervention_form.png)

**Étapes de création :**

1. Aller dans **Interventions → Services** → **« Nouveau »**
2. **Intitulé** : "Réparation plomberie - Fuite robinet cuisine"
3. **Bien** : Appartement 3A
4. **Type** : Réparation
5. **Priorité** : ★★★ (Urgent)
6. **Date demandée** : aujourd'hui
7. **Date planifiée** : demain matin
8. **Coût estimé** : 25 000 CFA
9. **Description** : "Fuite au niveau du robinet de l'évier de la cuisine. Le locataire a coupé l'arrivée d'eau."
10. Enregistrer → statut automatique : **Demande**

**Avancement de l'intervention :**

```
Demande → Soumise → Approuvée → En cours → En attente validation → Validée → Facturée → Clôturée
```

- Cliquer **« Soumettre »** pour envoyer à validation
- Cliquer **« Approuver »** pour autoriser les travaux
- Cliquer **« Démarrer »** quand le technicien intervient
- Cliquer **« Valider »** quand les travaux sont terminés

---

## 💬 5. Communications et suivi

### Le Chatter (historique et messages)

Chaque fiche (bien, bail, intervention) dispose d'un **chatter** à droite. Il conserve l'historique complet de toutes les modifications.

**Pour envoyer un message à un collaborateur :**
1. Cliquer **« Envoyer message »**
2. Taper le message
3. Mentionner avec **@nom** pour notifier une personne spécifique
4. Cliquer **« Envoyer »** → la personne reçoit une notification email

**Pour ajouter une note interne :**
1. Cliquer **« Note »**
2. Saisir la note (non envoyée aux partenaires externes)
3. **« Ajouter »**

**Pour planifier une activité :**
1. Cliquer **« Activité »**
2. Choisir le type : Appel, Email, Réunion, Relance...
3. Définir la date d'échéance et assigner à un utilisateur

---

## ⚙️ 6. Configuration

> **Configuration** (menu en haut à droite)

### Plans de récurrence

Définit les fréquences de facturation disponibles :
- Mensuel (1 mois)
- Trimestriel (3 mois)
- Semestriel (6 mois)
- Annuel (12 mois)

### Modèles de bail

Prédéfinissez des modèles pour accélérer la création de baux (type, durée, loyer par défaut, plan).

### Motifs de résiliation

Personnalisez les motifs disponibles lors d'une résiliation (Fin de bail, Impayés, Départ volontaire, etc.).

### Fréquence de rafraîchissement du tableau de bord

> **Configuration → Paramètres techniques → Paramètres système**
> Rechercher : `re.dashboard.refresh_interval`

La valeur est en **secondes** (60 par défaut).

---

## 🔍 7. Conseils pratiques

### Filtres rapides

Sur chaque liste, utilisez la barre de recherche et le bouton **▼** pour accéder aux filtres :
- **Baux** : Actifs, Suspendu, Résilié, Expire bientôt
- **Biens** : Disponible, Occupé, En travaux
- **Interventions** : En cours, Urgentes, Par bien

### Vues disponibles

Toutes les listes proposent deux modes d'affichage (icônes en haut à droite) :
- **Vue liste** : tableau avec colonnes triables
- **Vue kanban** : cartes visuelles par statut

### Navigation rapide

Depuis le tableau de bord, cliquez sur :
- Un **nom de bien** dans le tableau des baux → fiche du bien
- Une **ligne de bail** → fiche du bail
- Une **intervention** → fiche de l'intervention
- Une **alerte** → l'enregistrement concerné

---

## ❓ 8. Questions fréquentes

**Q : Le statut de mon bien est toujours "Disponible" après avoir créé un bail ?**
> Le bail doit être **confirmé** : cliquer sur **"En cours (Actif)"** dans la barre de statut. Le statut du bien se met à jour automatiquement.

**Q : La tuile "Impayés" affiche 0 mais j'ai des retards ?**
> Les impayés affichés sont les factures **validées et en retard**. Les baux non facturés ne sont pas comptés. Vérifiez que les factures de loyer ont bien été générées et validées.

**Q : Comment modifier un loyer sans rompre le bail ?**
> Utilisez le bouton **Avenant** sur la fiche du bail. Cela modifie les termes avec une traçabilité complète, sans interrompre le bail.

**Q : Comment voir l'historique de toutes les modifications d'un bail ?**
> Ouvrez la fiche du bail et regardez le **chatter** (panneau de droite). Toutes les modifications (changement de statut, avenant, note...) y sont enregistrées avec la date et l'auteur.

**Q : Comment calculer une pénalité de retard ?**
> Depuis la fiche du bail, cliquez **"Calculer pénalités"**. Le système analysera les factures en retard et proposera les pénalités à créer selon les règles configurées (montant fixe ou pourcentage).

---

## 📞 Support

**AFRO IT**
- Email : contact@afroit.net
- Site : afroit.net

---

*Guide rédigé par AFRO IT — Juin 2026 — MILA Immobilier v3.2*
