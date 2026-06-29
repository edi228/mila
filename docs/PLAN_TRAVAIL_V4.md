# Plan de Travail — MILA Immobilier v4.0
_Mis à jour : 29 juin 2026_

---

## Principes directeurs

1. **Pas de navigation hors module** : tous les champs pertinents des modèles liés sont éditables directement depuis les vues Immobilier
2. **Simplicité** : chaque action courante accessible en ≤ 2 clics
3. **Cohérence** : les données créées depuis une vue Immobilier sont valides dans les vues natives Odoo (pas de doublons)
4. **Push → Build Odoo.sh** : chaque chantier fini = push GitHub = rebuild automatique sur `prod`

---

## CHANTIER 1 — Renommage "Garantie" → "Caution"
**Effort** : 🟢 2h | **Sprint** : 1

### Fichiers à modifier
- [ ] `models/re_lease.py` — labels : deposit_amount → "Caution", deposit_paid → "Caution encaissée", deposit_returned → "Caution restituée", deposit_deductions → "Déductions sur caution"
- [ ] `views/re_lease_views.xml` — tous les string= "Dépôt de garantie"
- [ ] `report/re_lease_contract_report.xml` — label dans le rapport imprimable
- [ ] `report/re_lease_quittance_report.xml` — idem si applicable

### Validation
- Ouvrir fiche bail → onglet financier → libellé "Caution"
- Imprimer un contrat → label correct

---

## CHANTIER 2 — Contacts & Locataires améliorés
**Effort** : 🟡 1 jour | **Sprint** : 1

### 2.1 Champ type sur res.partner

**`models/res_partner.py`**
```python
re_contact_type = fields.Selection([
    ('tenant', 'Locataire'),
    ('owner', 'Propriétaire'),
    ('guarantor', 'Garant'),
    ('provider', 'Prestataire'),
    ('other', 'Autre')
], string="Rôle principal immobilier", tracking=True)
# onchange bi-directionnel avec is_tenant, is_property_owner, is_guarantor
```

**Pièce d'identité (déplacée de re.lease.identity vers res.partner) :**
```python
identity_doc_type = fields.Selection([
    ('cni', "Carte Nationale d'Identité"),
    ('passport', 'Passeport'),
    ('driver', 'Permis de conduire'),
    ('residence', 'Titre de séjour'),
    ('other', 'Autre')
], string="Type de pièce d'identité")
identity_doc_number      = fields.Char(string="Numéro de pièce")
identity_doc_scan        = fields.Binary(string="Scan recto (PDF/image)", attachment=True)
identity_doc_scan_name   = fields.Char()
identity_doc_scan_back   = fields.Binary(string="Scan verso", attachment=True)
identity_doc_scan_back_name = fields.Char()
identity_doc_expiry      = fields.Date(string="Date d'expiration")
```

### 2.2 Vue contact étendue
**`views/res_partner_views.xml`** — onglet "Immobilier" ajouté :
- Rôle principal (re_contact_type) + cases is_tenant, is_property_owner, is_guarantor
- Section "Pièce d'identité" : type, numéro, expiration, scan recto/verso
- Smart buttons : Baux actifs | Biens en propriété | Garanties

### 2.3 Champs inline sur la fiche bail
**`views/re_lease_views.xml`** — onglet "Locataire" (nouveau) :
```
[Nom du locataire]    [Téléphone]    [Email]
[Adresse]
── Pièce d'identité ──────────────────────────────
[Type]    [Numéro]    [Expiration]
[Scan recto ↑]    [Scan verso ↑]
── Référence ──────────────────────────────────────
[Référence locataire (readonly)]
```
Même logique allégée pour le Garant (nom, téléphone, pièce d'identité).

### 2.4 Conserver re.lease.identity
Garder le modèle existant comme table de stockage (les champs partner sont `related`), le rendre invisible dans l'UI (remplacé par l'onglet).

### Validation
- Créer un contact depuis la vue Locataires (menu Locations → Locataires) → champ type visible → pièce d'identité remplissable
- Depuis bail : onglet Locataire → éditer téléphone du locataire → visible sur sa fiche contact

---

## CHANTIER 3 — Dashboard : KPI + Tableau + Grid
**Effort** : 🟡 1,5 jours | **Sprint** : 1-2

### 3.1 Backend — re_dashboard.py
**Modifier `get_dashboard_data()` :**
- KPI "Biens" → `{ occupied: 4, total: 6 }` (plus juste le total)
- Ajouter `properties_data` : liste complète biens avec building, type, state, tenant_name, rent_amount, next_invoice_date, lat, lng
- Ajouter `buildings_data` : immeubles + biens imbriqués (pour la grid)

### 3.2 Frontend OWL

**KPI modifié :**
```
┌──────────────────────┐
│  🏠  4 / 6           │
│     Biens occupés    │
│  ████████░░  66.7%   │  ← barre de progression
└──────────────────────┘
```

**Nouveau composant ImmoPropertyTable :**
```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Bien     │ Immeuble │ Type     │ Statut   │ Locataire│ Loyer    │ Échéance │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Appt 3A  │ Palmeraie│ Résid.  │ 🟢 Occupé│ K. Mensah│ 150 000 │ 01/07   │
│ (cliquable)                                                                 │
```
- Filtre par statut (tous / occupé / dispo / travaux) et par immeuble
- Tri par colonne
- Chaque ligne → ouvre le bien

**Nouveau composant ImmoBuildingGrid :**
```
╔═══════════════════════════════╗
║  🏢 Immeuble Palmeraie  (6)  ║
╠═══════════════════════════════╣
║  [🟢 Appt 3A]  [🟢 Appt 2B]  ║
║  [🟢 Bureau B1] [🟠 Appt 5B] ║
║  [🟢 Studio 1A] [🔵 Mag. RDC]║
╚═══════════════════════════════╝
```
Tooltip au survol : locataire + loyer. Clic → ouvre le bien.

### Validation
- KPI affiche "4 / 6" avec barre progression
- Tableau liste les 6 biens, clic sur une ligne → fiche bien
- Grid groupe les biens par immeuble, badges colorés

---

## CHANTIER 4 — Navigation & Menus
**Effort** : 🟢 3h | **Sprint** : 1

### Structure cible (`views/menus.xml`)

```
📊  Tableau de bord
🏢  Patrimoine
    ├── Immeubles
    └── Biens immobiliers
📄  Locations
    ├── Baux actifs
    ├── Tous les baux
    ├── Locataires              ← NOUVEAU (res.partner, domain is_tenant=True)
    ├── ─────────────────
    ├── Pénalités               ← REMONTÉE (était dans Configuration)
    └── Épargnes en cours       ← NOUVEAU
💰  Finances                    ← NOUVEAU menu principal
    ├── Quittances de loyer     ← account.move filtré bail
    └── Reçus de paiement       ← account.payment filtré bail
🔧  Interventions
    └── Services
⚙️  Configuration
    ├── Plans de récurrence
    ├── Modèles de bail
    ├── Motifs de résiliation
    ├── Modèles de signature    ← NOUVEAU (sprint 4)
    ├── Taxes immobilières
    └── Paramètres dashboard
```

### Validation
- Toute les entrées de menu sont cliquables et affichent du contenu
- Menu Locataires → filtre is_tenant → liste contacts locataires
- Menu Pénalités → liste re.penalty avec boutons inline

---

## CHANTIER 5 — Finance : Factures & Reçus de Paiement
**Effort** : 🔴 2 jours | **Sprint** : 2

### 5.1 Boutons sur la fiche bail
**`views/re_lease_views.xml`** — header :
- Bouton **"📄 Générer quittance"** → appelle `_generate_invoice()` immédiatement + confirme
- Smart button **"X Quittances"** → liste account.move filtrée sur le bail
- Smart button **"X Paiements"** → liste account.payment filtrée sur le bail

**Bouton "Enregistrer paiement"** → ouvre le wizard natif `account.payment.register` pré-filtré sur les factures impayées du bail.

### 5.2 Reçu de Paiement (QWeb PDF)
**Nouveau rapport `report/re_lease_receipt_report.xml`**

Structure du reçu (inspirée de la capture Odoo.sh fournie + standards OHADA) :

```
┌─────────────────────────────────────────────────────────────────┐
│  MILA GESTION IMMOBILIÈRE          [Logo]                        │
│  Immeuble Palmeraie, Lomé - Togo                                 │
│  Tél : +228 XX XX XX XX  |  contact@mila.tg                     │
├─────────────────────────────────────────────────────────────────┤
│                     REÇU DE PAIEMENT                            │
│              Réf : REC/2026/00042   Date : 29/06/2026           │
├──────────────────────────────┬──────────────────────────────────┤
│  LOCATAIRE                   │  BIEN LOUÉ                       │
│  Kofi Mensah                 │  Appartement 3A                  │
│  Réf : LOC-2026-0001         │  Immeuble Palmeraie, Lomé        │
│  Tél : +228 90 00 00 00      │  Bail : BAIL/2026/0001           │
├──────────────────────────────┴──────────────────────────────────┤
│  DÉTAIL DU PAIEMENT                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Désignation              Période       Montant             │ │
│  │ Loyer de base            Juin 2026     150 000 CFA         │ │
│  │ Charges incluses         Juin 2026          0 CFA         │ │
│  │ Taxe foncière (2%)       Juin 2026      3 000 CFA         │ │
│  │ ────────────────────────────────────────────────────────── │ │
│  │ TOTAL DÛ                               153 000 CFA         │ │
│  │ Pénalité de retard (si applicable)           0 CFA         │ │
│  │ ────────────────────────────────────────────────────────── │ │
│  │ MONTANT REÇU                           153 000 CFA         │ │
│  │ Mode de règlement         Espèces / Virement / Mobile Money│ │
│  │ Référence transaction     [si applicable]                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Solde avant paiement       153 000 CFA                         │
│  Montant encaissé           153 000 CFA                         │
│  Solde après paiement             0 CFA    ✅ SOLDÉ             │
├─────────────────────────────────────────────────────────────────┤
│  Observations : RAS                                              │
├──────────────────────────────┬──────────────────────────────────┤
│  Signature du gestionnaire   │  Signature du locataire          │
│                              │                                  │
│  ____________________        │  ____________________            │
│  [Nom + Cachet]              │  [Nom + Date]                    │
└──────────────────────────────┴──────────────────────────────────┘
  Document généré le 29/06/2026 | MILA Gestion Immobilière v4.0
```

### 5.3 Vue "Quittances de loyer" (menu Finances)
- action `account.move` avec domain `move_type=out_invoice` + filtre par bail
- Colonnes : Réf | Bail | Locataire | Période | Montant | Statut paiement | Actions
- Bouton **"Enregistrer paiement"** inline

### 5.4 Vue "Reçus de paiement" (menu Finances)
- action `account.payment` avec filtre bail
- Colonnes : Réf | Bail | Locataire | Montant | Mode | Date | Statut
- Bouton **"Imprimer reçu"**

### Validation
- Créer une quittance depuis le bail → facture account.move créée et postée
- Enregistrer le paiement → wizard natif → paiement créé
- Imprimer le reçu → PDF avec tous les champs du modèle ci-dessus

---

## CHANTIER 6 — Pénalités : intuitivité
**Effort** : 🟡 1 jour | **Sprint** : 2

### 6.1 Améliorations modèle
**`models/re_lease_penalty_schedule.py`** :
- Ajouter `is_terminal = fields.Boolean("Déclenche la résiliation automatique")`
- Ajouter `description = fields.Text("Description affichée au locataire")`
- Ajouter `notify_tenant = fields.Boolean("Notifier le locataire par email")`
- **CORRIGER le doublon** : consolider `re.penalty` en un seul fichier (`re_penalty.py`)

### 6.2 Wizard amélioré
**`wizard/re_penalty_apply_wizard.py`** (nouveau wizard simplifié) :
- Sélectionner facture impayée → calcul automatique du palier applicable → aperçu du montant → Confirmer
- Accessible depuis : fiche bail + vue Quittances + menu Pénalités

### 6.3 Vue liste pénalités améliorée
**`views/re_penalty_views.xml`** :
- Colonnes : Réf | Bail | Locataire | Facture | Palier | Retard | Montant | Statut
- Boutons inline (pas d'ouverture de fiche) : **Confirmer** | **Facturer** | **Annuler**
- Filtre rapide : En attente | Confirmées | À facturer | Annulées
- Badge rouge si jours_retard > 30

### 6.4 Onglet Pénalités sur fiche bail
**`views/re_lease_views.xml`** — onglet "Pénalités" :
- Tableau 1 : Calendrier des paliers (éditable directement, colonnes : Séq | Libellé | Délai J+ | Mode | Valeur | Base | Cumulatif | Terminal)
- Tableau 2 : Pénalités générées (lecture, colonnes : Réf | Facture | Retard | Montant | Statut | Actions)
- Boutons : **"Calculer les pénalités"** + **"Toutes les pénalités →"**

### Validation
- Depuis bail actif avec facture impayée → onglet Pénalités → bouton "Calculer" → wizard affiche le calcul → confirmer → pénalité créée
- Liste Pénalités → bouton "Facturer" inline → facture créée sans ouvrir la fiche

---

## CHANTIER 7 — Géolocalisation Immeuble → Bien
**Effort** : 🟡 0,5 jour | **Sprint** : 2

### Backend
**`models/re_building.py`** :
```python
partner_id = fields.Many2one('res.partner', string="Contact / Localisation")
latitude   = fields.Float(related='partner_id.partner_latitude',  store=True, string="Latitude")
longitude  = fields.Float(related='partner_id.partner_longitude', store=True, string="Longitude")
maps_url   = fields.Char(compute='_compute_maps_url', string="Lien Google Maps")

@api.depends('latitude', 'longitude')
def _compute_maps_url(self):
    for b in self:
        if b.latitude and b.longitude:
            b.maps_url = f"https://maps.google.com/?q={b.latitude},{b.longitude}"
        else:
            b.maps_url = False
```

**`models/re_property.py`** :
```python
latitude  = fields.Float(compute='_compute_geo', store=True)
longitude = fields.Float(compute='_compute_geo', store=True)

@api.depends('building_id.latitude', 'building_id.longitude')
def _compute_geo(self):
    for p in self:
        p.latitude  = p.building_id.latitude  or 0.0
        p.longitude = p.building_id.longitude or 0.0
```

### Vues
**`views/re_building_views.xml`** : champ `partner_id` (pour renseigner l'adresse + coordonnées GPS depuis le contact) + bouton "📍 Voir sur la carte" (ouvre maps_url)
**`views/re_property_views.xml`** : latitude/longitude en readonly + mention "Héritées de l'immeuble" + bouton carte

### Validation
- Immeuble : sélectionner un contact avec adresse → latitude/longitude héritées automatiquement
- Bien : latitude héritée depuis l'immeuble

---

## CHANTIER 8 — Épargnes automatiques dans les quittances
**Effort** : 🟡 1 jour | **Sprint** : 3

### 8.1 Génération automatique
Modifier `_generate_invoice()` dans `re_lease_logic.py` :
```python
# Après création de l'account.move, pour chaque saving_rule active du bail :
# 1. Calculer le montant épargne (% ou fixe selon mode et base)
# 2. Créer une account.move.saving.line liée à la facture
# 3. Créer une ligne comptable dans la facture (ou écriture séparée selon Q2)
# 4. Libellé : f"Épargne {rule.name} — {lease.name} — {period}"
```

### 8.2 Annulation manuelle au cas par cas
- Sur la vue facture de loyer (côté Immobilier) : afficher les lignes d'épargne avec bouton "Annuler cette épargne" (revert la ligne comptable)
- Wizard léger `re.saving.cancel.wizard` : motif de l'annulation (obligatoire pour traçabilité)

### 8.3 Vue "Épargnes en cours" (menu Locations)
- Liste des `account.move.saving.line` filtrées sur les baux actifs
- Colonnes : Bail | Règle | Facture | Montant | Compte cible | Statut
- Export possible

### Validation
- Générer une quittance pour un bail avec règle épargne → vérifier la ligne comptable créée
- Annuler l'épargne d'une ligne → vérifier la contre-écriture
- Menu Épargnes en cours → liste cohérente

---

## CHANTIER 9 — Signature électronique
**Effort** : 🔴 2 jours | **Sprint** : 3-4

### Pré-requis
- Vérifier disponibilité module `sign` sur l'instance Odoo.sh
- Si disponible : ajouter `'sign'` dans `depends` du manifest

### 9.1 Nouveaux champs sur re.lease
**`models/re_lease_sign.py`** (nouveau fichier) :
```python
sign_template_id = fields.Many2one('sign.template', string="Modèle de contrat")
sign_request_id  = fields.Many2one('sign.request',  string="Demande de signature")
sign_state = fields.Selection([
    ('not_sent', 'Non envoyé'),
    ('sent', 'En attente signature locataire'),
    ('partially_signed', 'Partiellement signé'),
    ('signed', 'Signé électroniquement ✅'),
    ('manual', 'Signature manuelle attachée ✅'),
], default='not_sent', tracking=True)
sign_sent_date   = fields.Datetime(string="Envoyé le")
sign_done_date   = fields.Datetime(string="Signé le")
```

### 9.2 Méthodes
```python
def action_send_for_signature(self):
    """Crée sign.request depuis sign_template_id → send → email au locataire avec lien token"""

def action_view_sign_request(self):
    """Ouvre la sign.request en cours"""

def action_mark_manually_signed(self):
    """Ouvre wizard pour uploader le PDF signé scanné"""
```

### 9.3 Onglet "Signature" sur fiche bail
- Sélection du modèle de contrat (`sign_template_id`)
- Mode : `Électronique` | `Manuelle`
- Si électronique : bouton **"📧 Envoyer pour signature"** → badge statut
- Si manuelle : bouton **"📎 Attacher PDF signé"** → widget binary
- Historique : signataires + dates

### 9.4 Modèles de signature (Configuration)
**`views/re_sign_template_views.xml`** :
- Liste des `sign.template` utilisables pour les baux
- Colonne : Nom | Aperçu | Nbre baux l'utilisant

### Validation
- Envoyer pour signature → email reçu par locataire avec lien unique
- Signer depuis le lien → statut bail mis à jour
- Mode manuel → uploader PDF → statut = "Signature manuelle attachée"

---

## CALENDRIER RÉSUMÉ

| Sprint | Chantiers | Durée estimée |
|--------|-----------|---------------|
| **Sprint 1** | 1 (Caution) + 2 (Contacts) + 4 (Menus) | 2 jours |
| **Sprint 2** | 3 (Dashboard) + 5 (Finance+Reçu) + 6 (Pénalités) | 3 jours |
| **Sprint 3** | 7 (Géoloc) + 8 (Épargnes auto) | 2 jours |
| **Sprint 4** | 9 (Signature élec.) | 2 jours |

**Après chaque sprint :**
1. Push GitHub → Odoo.sh rebuild automatique
2. Tests fonctionnels (RPC + UI)
3. Mise à jour documentation HTML

---

## RÈGLE GÉNÉRALE POUR TOUS LES CHANTIERS

> **"Pas de navigation hors module"**
> Pour CHAQUE modèle lié (res.partner, account.account, account.journal, sign.template, etc.) :
> - Les champs **essentiels** sont affichés et **éditables** directement dans les vues Immobilier
> - Les wizards natifs Odoo sont toujours préférés aux vues personnalisées quand ils existent
> - Les smart buttons permettent d'accéder aux données complètes si besoin (mais ne sont pas le flux principal)
