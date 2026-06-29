# Contexte Projet — MILA Gestion Immobilière
**Document de référence pour IA de suivi de projet**
_Généré le 29 juin 2026 — À jour jusqu'au sprint v3.3_

---

## 1. VUE D'ENSEMBLE

### Objectif
Développer un module Odoo de **gestion immobilière locative complète** pour la société **MILA**, deployé sur une instance Odoo Enterprise gérée via **Odoo.sh** (plateforme de déploiement PaaS, parfois désignée "cloudpepper" dans les échanges).

### Instance de production
- **URL** : https://mila.afroit.net
- **Credentials admin** : admin / admin
- **Credentials client test** : client / client123
- **Plateforme** : Odoo.sh (branche `prod`, branche de staging `main`, branche de test `test`)
- **Version Odoo** : Enterprise (branche prod identifiée 17.0 sur Odoo.sh, mais comportement et API compatibles avec les patterns Odoo 19 utilisés dans le développement)
- **Repo GitHub** : https://github.com/edi228/mila
- **Token GitHub** : [TOKEN_EDI228_GITHUB]
- **Nom du module** : `maono_real_estate`

### Deux sociétés configurées
| Société | Usage | Plan comptable |
|---------|-------|---------------|
| MILA Immobilier | Gestion locative | Plan comptable Togo |
| MILA Boutique | Gestion commerciale boutique | Plan comptable Togo |

### Langue et localisation
- Interface : Français
- Devise : CFA (XOF)
- Plan comptable : Togo (activé)

---

## 2. STRUCTURE DU MODULE `maono_real_estate`

### Localisation
```
/Users/edouard/Documents/Antigravity/immo/maono_real_estate/
```

### Version actuelle : 3.3
### Dépendances déclarées
```python
'depends': ['sale', 'account', 'mail', 'payment', 'portal', 'rating']
```

### Architecture des fichiers (25 modèles, 5 wizards, 15 vues XML, 3 assets OWL)

```
models/
  re_building.py              # re.building — Immeubles/complexes
  re_property.py              # re.property — Biens immobiliers
  re_lease.py                 # re.lease — Contrats de bail (champs)
  re_lease_logic.py           # re.lease (_inherit) — Méthodes métier
  re_lease_line.py            # re.lease.line — Lignes de facturation
  re_lease_tax_line.py        # re.lease.tax.line — Taxes par bail
  re_lease_saving_rule.py     # re.lease.saving.rule — Règles d'épargne
  re_lease_penalty_schedule.py # re.lease.penalty.schedule + re.penalty
  re_lease_identity.py        # re.lease.identity — Pièces d'identité (au niveau bail)
  re_lease_log.py             # re.lease.log — Journal d'événements
  re_lease_plan.py            # re.lease.plan — Plans de récurrence
  re_lease_template.py        # re.lease.template — Modèles de bail
  re_lease_service.py         # re.lease.service — Services inclus
  re_lease_close_reason.py    # re.lease.close.reason — Motifs résiliation
  re_property_service.py      # re.property.service — Interventions/travaux
  re_property_amenity.py      # re.property.amenity — Équipements
  re_account_move.py          # account.move + account.move.saving.line (_inherit)
  re_account_tax.py           # account.tax (_inherit)
  re_dashboard.py             # re.dashboard — Point RPC dashboard OWL
  res_partner.py              # res.partner (_inherit)
  re_product.py               # product.template (_inherit)
  re_tenant_ref_log.py        # re.tenant.ref.log — Historique refs locataire

wizard/
  re_lease_renew_wizard.py         # Renouvellement de bail
  re_lease_close_wizard.py         # Résiliation de bail
  re_penalty_compute_wizard.py     # Calcul des pénalités (avec preview)
  re_saving_transfer_wizard.py     # Transfert épargne → écriture comptable
  re_lease_amendment_wizard.py     # Avenant de bail

static/src/dashboard/
  immo_dashboard.js           # Composant OWL principal + ImmoKpiCard
  immo_dashboard.xml          # Templates OWL
  immo_dashboard.scss         # Styles dashboard

report/
  re_lease_contract_report.xml   # Contrat de bail (QWeb PDF)
  re_lease_quittance_report.xml  # Quittance de loyer (QWeb PDF)
```

---

## 3. MODÈLES CLÉS — CHAMPS ET RELATIONS

### `re.building` — Immeuble
Champs : `name`, `ref`, `street`, `city`, `zip`, `country_id`, `owner_id` (→ res.partner), `property_ids`, `property_count`, `occupied_count`, `available_count`, `occupation_rate`, `expected_monthly_revenue`

### `re.property` — Bien immobilier
Champs : `name`, `ref`, `building_id` (→ re.building), `type` (residential/commercial/terrain/parking/mixte), `owner_id` (→ res.partner, domain: is_property_owner=True), `rent_amount`, `state` (available/occupied/suspended/works/reserved — compute), `active_lease_id` (compute), `current_tenant_id` (compute), `surface`, `floor`, `rooms`, `amenities`, `image_1920`

### `re.lease` — Bail
Champs principaux : `name` (séquence BAIL/YYYY/NNNN), `property_id`, `tenant_id`, `guarantor_id`, `co_tenant_ids`, `lease_type` (monthly/annual/commercial/seasonal — **REQUIS**), `plan_id`, `start_date`, `end_date`, `rent_amount`, `advance_months`, `deposit_amount` (libellé actuel : "Dépôt de garantie" → à renommer "Caution"), `lmr` (Loyer Mensuel Récurrent — compute), `lease_state` (1_draft → 3_progress → 4_paused → 5_renewed → 6_churn)

Relations : `line_ids`, `tax_line_ids`, `saving_rule_ids`, `schedule_ids`, `penalty_ids`, `identity_ids`, `lease_log_ids`

Boutons d'action : `action_confirm`, `action_pause`, `action_resume`, `action_renew_lease` (wizard), `action_close_lease` (wizard), `action_create_amendment` (wizard), `action_compute_penalties` (wizard), `action_view_penalties`

### `re.lease.penalty.schedule` — Calendrier pénalités
Champs : `lease_id`, `sequence`, `name`, `trigger_days` (jours après échéance), `mode` (percent/fixed), `value`, `base` (original/cumulative), `is_active`, `auto_generate`

### `re.penalty` — Instance de pénalité
Champs : `lease_id`, `schedule_id`, `invoice_id` (quittance impayée), `penalty_invoice_id` (facture pénalité générée), `invoice_original_amount`, `cumulative_base`, `penalty_amount` (compute), `days_late` (compute), `state` (draft/confirmed/invoiced/cancelled)
Workflow : draft → confirmed (`action_confirm`) → invoiced (`action_create_invoice`) | cancelled (`action_cancel`)

### `re.lease.saving.rule` — Règles d'épargne
Champs : `lease_id`, `name`, `mode` (percent/fixed), `value`, `base` (rent/total_invoice), `is_active`, `target_account_id` (compte comptable), `beneficiary`, `beneficiary_partner_id`

### `re.property.service` — Interventions
Champs : `property_id`, `service_type` (repair/maintenance/renovation/...), `priority` (0 Normal → 3 Bloquant), `state` (draft → submitted → approved → in_progress → done/cancelled), `estimated_cost`, `actual_cost`, `vendor_bill_ids`
Workflow : draft → submitted → approved → in_progress → done

### `res.partner` (extension) — Contacts
Champs ajoutés : `is_property_owner`, `is_tenant`, `is_guarantor` (booléens), `tenant_ref`, `owner_property_ids`, `tenant_lease_ids`, `guarantor_lease_ids`, `total_lmr`

### `re.lease.identity` — Pièces d'identité (niveau bail)
Champs : `lease_id`, `party` (tenant/owner/guarantor/co_tenant), `partner_id`, `doc_type` (national_id/passport/residence_permit/driver_license/other), `doc_number`, `issue_date`, `expiry_date`, `attachment_id`, `attachment_back_id`, `verified`

### Dashboard OWL — `re.dashboard.get_dashboard_data()`
Retourne : `kpis` (5 indicateurs), `leases` (baux actifs), `services` (interventions en cours), `alerts` (expirations + impayés + pénalités), `refresh_interval`

---

## 4. INFRASTRUCTURE FINANCIÈRE EXISTANTE

### Génération de factures (quittances)
- Méthode : `re.lease._generate_invoice()` dans `re_lease_logic.py`
- Crée `account.move` de type `out_invoice` pour le locataire
- Appelée par cron quotidien `_cron_lease_create_quittance()`
- Exécute `action_post()` → facture immédiatement validée

### Épargnes comptables
- `account.move.saving.line` : sous-modèle d'`account.move` qui lie les lignes épargne
- Wizard `re.saving.transfer.wizard` : crée une écriture comptable `account.move` de type `entry` (débit journal, crédit compte épargne) — actuellement déclenchement **manuel**

### Factures de pénalités
- `re.penalty.action_create_invoice()` : crée `account.move` pour le locataire

### Factures fournisseurs (travaux)
- `re.property.service.vendor_bill_ids` : lien Many2many vers `account.move`

---

## 5. DONNÉES EN BASE (instance prod au 19 juin 2026)

### Biens (6)
| Bien | Type | Statut | Loyer |
|------|------|--------|-------|
| Appartement 3A | Résidentiel | Occupé | 150 000 CFA |
| Bureau B1 | Commercial | Occupé | 80 000 CFA |
| Appartement 5B | Résidentiel | En travaux | 250 000 CFA |
| Appartement 2B | Résidentiel | Occupé | 120 000 CFA |
| Studio 1A | Résidentiel | Occupé | 75 000 CFA |
| Magasin RDC | Commercial | Disponible | 200 000 CFA |

### Baux actifs (4)
| Référence | Bien | Locataire | Loyer |
|-----------|------|-----------|-------|
| BAIL/2026/0001 | Appartement 3A | Kofi Mensah | 150 000 CFA |
| BAIL/2026/0002 | Bureau B1 | Ama Diallo | 80 000 CFA |
| BAIL/2026/0003 | Appartement 2B | Marcel Togbe | 120 000 CFA |
| BAIL/2026/0004 | Studio 1A | Fatima Ouedraogo | 75 000 CFA |

### KPIs actuels
- Taux d'occupation : 66,7% (4/6)
- LMR Global : 425 000 CFA/mois
- Impayés : 150 000 CFA (INV/2025/00001 — Kofi Mensah — 503 jours de retard)
- Pénalités actives : 15 000 CFA (PEN/2025/0001)

---

## 6. PROBLÈMES CONNUS ET BUGS IDENTIFIÉS

| # | Sévérité | Description | Statut |
|---|----------|-------------|--------|
| 1 | ⚠️ | `re.penalty` déclaré en double (re_penalty.py ET re_lease_penalty_schedule.py) | À corriger |
| 2 | ⚠️ | `action_suspend`, `action_reactivate` non exposés via RPC (utilisent write() direct) | À corriger |
| 3 | ℹ️ | `_compute_invoice_dates()` dans re_lease.py est vide (surchargée dans re_lease_logic.py) | OK mais fragile |
| 4 | ℹ️ | `payment_token_id` présent mais flux account.payment non implémenté | Backlog |

---

## 7. HISTORIQUE DES SPRINTS

### Sprint 1 — Setup initial
- Déploiement sur Odoo.sh (prod, main, test)
- Installation du module `maono_real_estate` avec toutes dépendances
- Configuration : langue française, plan comptable Togo, 2 sociétés
- Création d'un compte client (client/client123)

### Sprint 2 — Corrections et tests fonctionnels
- Correction : tuiles KPI non cliquables sur le dashboard (bug arrow function OWL)
- Correction : navigation KPIs → listes filtrées
- Tests RPC automatisés : 22 cas, score 86% (15 OK, 4 partiels, 1 erreur version)
- Fix : purge cache assets Odoo (`ir.attachment` bundles web)

### Sprint 3 — Documentation et stabilisation
- Génération documentation utilisateur HTML autonome avec 12 screenshots intégrés
  - Fichier : `docs/GUIDE_UTILISATEUR_MILA_IMMOBILIER.html` (4,9 MB)
  - 8 cas d'usage avec variantes
  - Accessible sur GitHub
- Bump version module 3.2 → 3.3

---

## 8. STACK TECHNIQUE

| Élément | Technologie |
|---------|------------|
| Backend | Python 3 (Odoo ORM) |
| Frontend | OWL (Odoo Web Library) — JS/XML/SCSS |
| Base de données | PostgreSQL |
| Déploiement | Odoo.sh (branches prod/main/test) |
| Versionning | Git + GitHub (edi228/mila) |
| Rapports | QWeb (PDF) |
| CI/CD | Odoo.sh auto-deploy sur push |

---

## 9. PROCHAINS CHANTIERS — v4.0 (planifiés)

| # | Chantier | Priorité |
|---|----------|----------|
| 1 | Renommage "Garantie" → "Caution" sur les baux | ⭐⭐⭐ |
| 2 | Contacts améliorés (type unique, pièce d'identité, champs inline) | ⭐⭐⭐ |
| 3 | Dashboard : KPI Occupés/Total + tableau interactif + grid immeubles | ⭐⭐⭐ |
| 4 | Navigation et menus restructurés | ⭐⭐⭐ |
| 5 | Finance native : génération factures bouton + reçu de paiement | ⭐⭐⭐ |
| 6 | Pénalités : wizard simplifié + menus intuitifs | ⭐⭐ |
| 7 | Géolocalisation immeubles → biens (via res.partner) | ⭐⭐ |
| 8 | Épargnes automatiques dans quittances (+ annulation manuelle possible) | ⭐⭐ |
| 9 | Signature électronique (module sign natif Odoo Enterprise) | ⭐⭐ |

### Décisions prises pour v4.0
- **Multi-rôles contacts** : un contact peut avoir plusieurs rôles simultanément (propriétaire + garant) → garder les booléens + ajouter champ `re_contact_type` (rôle principal pour filtre/affichage)
- **Épargnes** : automatiques dans les quittances (ligne comptable séparée) + possibilité d'annulation/surcharge manuelle au cas par cas
- **Pièces d'identité** : déplacées sur `res.partner` (champs directs) + accessibles depuis les vues bail via `related`
- **Éléments liés** : tous les champs essentiels des modèles liés (contacts, comptes, etc.) doivent être éditables depuis les vues du module Immobilier sans navigation vers les vues natives

---

## 10. CONVENTIONS ET RÈGLES DE DEV

- Nommage modèles : `re.*` pour les modèles propres, `_inherit` pour les extensions
- Séquences : re.lease.seq, re.tenant.ref, re.property.seq, re.building.seq, re.property.service.seq, re.penalty.seq
- Toute modification → push GitHub → Odoo.sh rebuild automatique sur branche correspondante
- Tests : via JSON-RPC sur https://mila.afroit.net + browser DevTools
- Pas de migration de données entre sprints (données de test en base)
- Documentation utilisateur : HTML autonome avec screenshots base64 (format exportable)
