# Plan d'Implémentation — Phase 2 · Suite Immobilière AFRO IT
**Date :** 22 mai 2026 | **Module :** `maono_real_estate` | **Odoo :** 19 Enterprise

---

## Vue d'ensemble — 7 Chantiers

| # | Chantier | Complexité | Impact |
|---|---|---|---|
| 1 | Bug vue Bien — champ ir.attachment | Faible | UX |
| 2 | Dashboard OWL custom | Haute | Fonctionnel |
| 3 | Communications (WhatsApp, Email, Notifs) | Moyenne | Fonctionnel |
| 4 | UI Pénalités | Faible | Accessibilité |
| 5 | Onglet Épargne — fix | Faible | Fonctionnel |
| 6 | Logique Baux — ligne loyer auto + produits | Moyenne | Fonctionnel |
| 7 | Upsell / Downsell avec traçabilité | Moyenne | Fonctionnel |

---

## Chantier 1 — Bug vue Bien (ir.attachment brut)

### Problème
Le champ `Many2many` vers `ir.attachment` s'affiche en liste brute (colonnes Name, Resource Model, Resource Field…) au lieu d'un widget galerie.

### Correction
- **Supprimer** le champ `many2many` vers `ir.attachment` de la vue formulaire
- **Ajouter** un champ `image_1920` (photo principale) avec widget `image` en haut du formulaire
- Les pièces jointes restent accessibles via le **chatter natif** (standard Odoo)

### Fichiers modifiés
- `models/re_property.py` — ajout champ `image_1920`
- `views/re_property_views.xml` — remplacement du widget cassé

---

## Chantier 2 — Dashboard OWL Custom

### Architecture
Un composant OWL monté sur une route dédiée `/odoo/immobilier/dashboard`, chargé via une `ir.actions.client`.

### Zones du dashboard

**Zone A — Bandeau KPI (5 cartes animées)**
- Total biens (avec répartition disponible / occupé / travaux)
- Taux d'occupation (%)
- LMR Global (somme des loyers actifs)
- Factures impayées (montant + nombre)
- Pénalités actives (montant + nombre)

**Zone B — Baux actifs (tableau interactif)**
Colonnes : Bien, Locataire, Loyer/mois, Statut badge, Prochaine échéance, Jours restants (coloré : vert/orange/rouge), Actions rapides (→ voir bail)

**Zone C — Interventions en cours (kanban miniature)**
Cartes groupées par statut (En cours / À valider / Urgent), avec : bien, type, priorité, prestataire

**Zone D — Alertes & Rappels (colonne droite)**
- Baux expirant dans < 60 jours
- Factures en retard > 15 jours
- Pénalités non encore facturées

### Implémentation technique
```
static/
  src/
    dashboard/
      ImmoDashboard.js      # Composant OWL root
      ImmoKpiCard.js        # Carte KPI réutilisable
      ImmoBauxList.js       # Tableau baux
      ImmoInterventions.js  # Kanban interventions
      ImmoAlerts.js         # Panneau alertes
      dashboard.xml         # Templates OWL
      dashboard.scss        # Styles
```

Les données sont récupérées via des méthodes `@api.model` sur `re.lease` et `re.property.service` exposées en RPC.

---

## Chantier 3 — Communications

### 3.1 WhatsApp
- **Activation** du module natif Odoo `whatsapp` (déjà disponible en Odoo 17+)
- **Configuration** : compte WhatsApp Business API requis (Meta) — les templates de messages seront pré-créés dans Odoo
- **Déclencheurs sur le bail** :
  - Confirmation du bail → message de bienvenue au locataire
  - Génération quittance → notification avec montant et date d'échéance
  - Retard de paiement → rappel automatique à J+7, J+15, J+30
  - Expiration bail dans 60 jours → alerte au gestionnaire + locataire

### 3.2 Email (mail.template)
Templates à créer dans `data/mail_template_data.xml` :
- `re_lease_welcome_email` — confirmation de bail
- `re_lease_quittance_email` — quittance mensuelle avec PDF en pièce jointe
- `re_lease_payment_reminder_email` — rappel de paiement
- `re_lease_expiry_email` — alerte expiration
- `re_penalty_notification_email` — notification de pénalité

### 3.3 Notifications internes Odoo
- Via `message_notify()` sur les modèles `re.lease` et `re.penalty`
- Les crons existants enverront des notifications au gestionnaire assigné
- Bouclier de non-duplication (pas de double notification)

---

## Chantier 4 — UI Pénalités

### Ajouts
- **Menu** : `Locations → Pénalités` (liste + formulaire)
- **Smart button** sur formulaire bail : badge rouge avec compteur, visible si `penalty_count > 0`
- **Bouton header** : `Calculer les pénalités` visible quand `lease_state == '3_progress'`
- **Compute** `penalty_count` sur `re.lease`

---

## Chantier 5 — Onglet Épargne (fix)

### Problème
`saving_rule_ids` est absent ou non éditable dans la vue bail.

### Correction
Restructurer l'onglet "Taxes & Épargne" en deux pages séparées :

**Page 1 — Taxes applicables**
- Liste éditable `tax_line_ids` (taxe, base, taux, montant calculé)

**Page 2 — Règles d'épargne provisionnée**
- Liste éditable `saving_rule_ids` avec colonnes :
  - Libellé de la règle
  - Mode (Pourcentage / Montant fixe)
  - Valeur (taux ou montant)
  - Base de calcul (Loyer HT / Loyer TTC)
  - Compte comptable cible
  - Actif (checkbox)

---

## Chantier 6 — Logique Baux (ligne loyer auto + produits Odoo)

### 6.1 Catégorie et type produit "Immobilier"
Création d'une **catégorie produit dédiée** `Immobilier / Services locatifs` :
- `data/re_product_data.xml` : catégorie + produit "Loyer" par défaut
- Champ `is_rental_service = True` sur `product.template` (extension)
- Filtre dans les vues : seuls les produits `is_rental_service` sont sélectionnables dans les lignes de bail

### 6.2 Ligne loyer automatique
- Sur `action_confirm()` : création automatique d'une ligne `re.lease.line` avec :
  - `product_id` → produit "Loyer" par défaut
  - `name` → "Loyer — [nom du bien]"
  - `price_unit` → `rent_amount`
  - `is_rent_line = True` (flag pour identifier la ligne principale, non supprimable)
  - `recurring_invoice = True`
- Sur `onchange(rent_amount)` : mise à jour automatique de la ligne loyer si elle existe

### 6.3 Services complémentaires
L'onglet "Lignes de facturation" est restructuré :
```
┌─── LOYER DE BASE (verrouillé) ────────────────────┐
│ 🔒 Loyer — Studio A1    500 000 XOF    Mensuel    │
└───────────────────────────────────────────────────┘
┌─── SERVICES COMPLÉMENTAIRES ──────────────────────┐
│ + Ajouter un service (produits type "Immobilier") │
│   Gardiennage           15 000 XOF    Mensuel     │
│   Eau potable           5 000 XOF     Mensuel     │
└───────────────────────────────────────────────────┘
```

---

## Chantier 7 — Upsell / Downsell avec traçabilité

### Principe
**Pas de nouveau bail créé.** Le bail existant est modifié directement, avec un enregistrement dans `re.lease.log` à chaque changement.

### Nouveau wizard : `re.lease.amendment.wizard`
Champs :
- `lease_id` — bail concerné
- `amendment_type` — Upsell / Downsell / Modification services
- `new_rent_amount` — nouveau loyer (optionnel)
- `lines_to_add` — services à ajouter (One2many)
- `lines_to_remove` — services à retirer (Many2many)
- `effective_date` — date d'entrée en vigueur
- `reason` — motif (zone texte)

### Actions du wizard
1. Applique les modifications sur le bail (`rent_amount`, `line_ids`)
2. Crée une entrée dans `re.lease.log` :
   - Type : `upsell` ou `downsell`
   - Ancien loyer → nouveau loyer
   - Services ajoutés / retirés
   - Motif + date
3. Envoie une notification Odoo + email au locataire

### Bouton header sur le formulaire bail
`📈 Avenant` visible quand `lease_state == '3_progress'`

---

## Ordre d'exécution

1. Chantier 1 (bug) — immédiat, 15 min
2. Chantier 4 (pénalités UI) — 30 min
3. Chantier 5 (épargne fix) — 20 min
4. Chantier 6 (logique baux) — 1h30
5. Chantier 7 (avenant wizard) — 1h
6. Chantier 3 (communications) — 1h
7. Chantier 2 (dashboard OWL) — 2h à 3h

**Durée totale estimée : 7 à 8 heures de développement**

---

## Points de vérification post-implémentation
- Upgrade du module sans erreur
- Test complet de création bail → confirmation → quittance auto
- Test upsell avec vérification du journal d'événements
- Test dashboard avec données réelles
- Test notification WhatsApp (si compte Meta configuré)
