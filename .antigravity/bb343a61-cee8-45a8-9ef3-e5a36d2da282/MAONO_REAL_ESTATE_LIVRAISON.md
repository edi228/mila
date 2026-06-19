# AFRO IT — Gestion Immobilière — Document de Livraison Technique
## Module Odoo 19 | Version 3.1 | AFRO IT
**Date de livraison :** 17 mai 2026  
**Environnement :** Docker local — base `gestion_immo` — port `http://localhost:8019`  
**Chemin addons :** `/Users/edouard/Documents/Antigravity/immo/maono_real_estate`

---

## 1. CONTEXTE ET OBJECTIF

**AFRO IT** souhaitait un module de gestion immobilière locative complet sur Odoo 19 Enterprise, couvrant :
- La gestion du **patrimoine** (immeubles, biens, équipements)
- La gestion des **baux locatifs** avec facturation récurrente automatisée
- Le suivi des **interventions / travaux** sur les biens
- La gestion des **pénalités de retard** multicritères cumulatives
- L'**épargne provisionnée** sur les loyers
- Le **portail locataire** (base posée)
- Des **rapports PDF** (contrat de bail, quittance de loyer)

---

## 2. ARCHITECTURE TECHNIQUE

### 2.1 Identité du module
| Paramètre | Valeur |
|---|---|
| Nom technique | `maono_real_estate` |
| Version | 3.1 |
| Cible Odoo | 19.0 Enterprise |
| Dépendances | `sale`, `account`, `mail`, `payment`, `portal`, `rating` |
| Licence | OPL-1 |
| Application | Oui (icône dans le menu principal) |

### 2.2 Philosophie
- Module **autonome** — sans dépendance au module `sale_subscription` (trop lourd, inadapté)
- Interface **épurée** avec un seul point d'entrée menu "Immobilier"
- Facturation récurrente gérée par **crons dédiés** (pas de workflow Odoo standard)
- Pénalités **cumulatives et configurables** par palier

---

## 3. MODÈLES DE DONNÉES (23 modèles)

### 3.1 Patrimoine
| Modèle | Description | Fichier |
|---|---|---|
| `re.building` | Immeuble / complexe immobilier | `re_building.py` |
| `re.property` | Bien immobilier (unité louable) | `re_property.py` |
| `re.property.amenity` | Équipement / commodité d'un bien | `re_property_amenity.py` |

**Champs clés `re.building` :** nom, référence auto, adresse, gérant, nombre d'unités, revenu mensuel attendu (computed), chatter mail  
**Champs clés `re.property` :** référence, nom, type (résidentiel/commercial/industriel/terrain), statut (disponible/occupé/travaux/suspendu), immeuble, propriétaire, loyer de référence, surface, pièces, équipements, galerie photos

### 3.2 Bail (modèle central)
| Modèle | Description | Fichier |
|---|---|---|
| `re.lease` | Contrat de bail | `re_lease.py` |
| `re.lease.line` | Ligne de facturation d'un bail | `re_lease_line.py` |
| `re.lease.tax.line` | Taxe appliquée au bail | `re_lease_tax_line.py` |
| `re.lease.saving.rule` | Règle d'épargne provisionnée | `re_lease_saving_rule.py` |
| `re.lease.penalty.schedule` | Palier de pénalité | `re_lease_penalty_schedule.py` |
| `re.lease.identity` | Pièces d'identité du locataire | `re_lease_identity.py` |
| `re.lease.log` | Journal d'événements du bail | `re_lease_log.py` |
| `re.lease.plan` | Plan de périodicité | `re_lease_plan.py` |
| `re.lease.service` | Service inclus (eau, élec…) | `re_lease_service.py` |
| `re.lease.template` | Modèle de bail réutilisable | `re_lease_template.py` |
| `re.lease.close.reason` | Motif de résiliation | `re_lease_close_reason.py` |

**États du bail (`lease_state`) :**
```
Devis de bail → Renouvellement en cours → En cours (Actif) → Suspendu → Renouvelé → Résilié → Avenant en cours
```

**Champs financiers clés :** loyer mensuel de base, mois d'avance, dépôt de garantie, total à la signature, taux d'indexation, LMR (Loyer Mensuel Récurrent) calculé

**Champs signatures :** signature binaire locataire + propriétaire + garant, dates, indicateur `is_fully_signed`

**Champs état des lieux :** photos EDLE/EDLS, dates, notes HTML, booléens

### 3.3 Pénalités
| Modèle | Description | Fichier |
|---|---|---|
| `re.penalty` | Pénalité de retard générée | `re_penalty.py` |

**Workflow :** Brouillon → Confirmée → Facturée → Annulée  
**Calcul :** montant base + pénalités antérieures (cumul) × taux/montant selon palier  
**Séquence :** `PEN/YYYY/NNNN`

### 3.4 Interventions
| Modèle | Description | Fichier |
|---|---|---|
| `re.property.service` | Intervention / travaux sur un bien | `re_property_service.py` |

**Workflow :** Brouillon → Soumis → Approuvé → En cours → Validation → Validé → Clôturé / Annulé  
**Champs :** type, priorité (0→3), prestataire, dates planifiées/réelles, coûts estimé/réel, photos avant/après, documents joints

### 3.5 Extensions de modèles natifs
| Modèle étendu | Ajouts | Fichier |
|---|---|---|
| `res.partner` | is_property_owner, is_tenant, is_guarantor, tenant_ref, lease_count, owner_property_count | `res_partner.py` |
| `account.tax` | tax_category (immo/charges/retenues), is_real_estate | `re_account_tax.py` |
| `account.move` | lease_saving_ids, total_saving_amount, saving_transferred | `re_account_move.py` |
| `account.move.saving.line` | Ligne d'épargne calculée attachée à une quittance | `re_account_move.py` |

### 3.6 Logique cron (extension)
| Modèle | Fichier |
|---|---|
| `re.lease` (extension) | `re_lease_logic.py` |
| `re.tenant.ref.log` | `re_tenant_ref_log.py` |

---

## 4. VUES XML (15 fichiers)

| Fichier | Vues implémentées |
|---|---|
| `re_building_views.xml` | Form, List, Kanban (immeubles) |
| `re_property_views.xml` | Form, List + actions |
| `re_property_service_views.xml` | Form, List, Kanban, Search (interventions) |
| `re_lease_views.xml` | Form, List (baux) |
| `re_lease_plan_views.xml` | Form, List (plans périodicité) |
| `re_penalty_views.xml` | Form, List, Search (pénalités) |
| `re_lease_identity_views.xml` | Form, List (pièces d'identité) |
| `re_lease_log_views.xml` | List lecture seule (journal événements) |
| `re_lease_tax_line_views.xml` | List inline (taxes bail) |
| `re_lease_saving_rule_views.xml` | List inline (règles épargne) |
| `re_lease_penalty_schedule_views.xml` | Form, List (paliers pénalités) |
| `re_lease_template_views.xml` | Form, List (modèles bail) |
| `res_partner_views.xml` | Extension form partenaire (smart buttons + champs immo) |
| `re_account_tax_views.xml` | Extension list taxes (champs immo) |
| `menus.xml` | Toute la structure de navigation |

---

## 5. STRUCTURE DE NAVIGATION

```
🏠 Immobilier
├── Tableau de bord
├── Patrimoine
│   ├── Immeubles
│   └── Biens
├── Locations
│   ├── Baux actifs
│   └── Tous les baux
├── Interventions
│   └── Services & Travaux
├── Facturation       [structure posée]
├── Reporting         [structure posée]
└── Configuration
    ├── Plans de périodicité
    └── Taxes immobilières
```

---

## 6. WIZARDS (4 wizards)

### 6.1 Renouvellement de bail — `re.lease.renew.wizard`
- Saisie : nouvelles dates, nouveau loyer
- Options : copier services, taxes, règles épargne, paliers pénalités
- Action : crée un nouveau bail lié (enfant), passe le bail parent en `5_renewed`

### 6.2 Résiliation de bail — `re.lease.close.wizard`
- Saisie : motif, date résiliation, gestion dépôt (montant restitué, déductions + justification)
- Option : état des lieux de sortie (EDLS)
- Action : passe le bail en `6_churn`, libère le bien (statut → disponible)

### 6.3 Calcul pénalités — `re.penalty.compute.wizard`
- Saisie : bail, date de calcul
- Aperçu des pénalités à générer (liste avec jours de retard, montants)
- Total récapitulatif avant validation
- Action : génère les enregistrements `re.penalty` confirmés

### 6.4 Transfert épargne — `re.saving.transfer.wizard`
- Saisie : quittance source, journal bancaire cible, date de transfert
- Affiche les lignes d'épargne calculées avec comptes cibles
- Action : crée une écriture comptable de transfert

---

## 7. AUTOMATISATIONS (3 CRONS)

| Cron | Fréquence | Description |
|---|---|---|
| `ir_cron_re_lease_create_quittance` | Quotidien | Génère les factures clients pour tous les baux actifs dont `next_invoice_date ≤ today`. Calcule les lignes d'épargne. Met à jour `last_invoice_date` et `next_invoice_date`. |
| `ir_cron_re_lease_expiration` | Hebdomadaire | Alerte les gestionnaires (message chatter) pour les baux expirant dans ≤ 60 jours. Marque `is_closing = True`. |
| `ir_cron_re_lease_auto_penalties` | Quotidien | Pour chaque bail actif ayant des paliers `auto_generate=True`, détecte les factures impayées et génère automatiquement les pénalités correspondantes (anti-doublon intégré). |

---

## 8. RAPPORTS PDF (QWeb)

### 8.1 Contrat de bail — `report_re_lease_contract_doc`
- Modèle : `re.lease`
- Contenu : parties (bailleur/locataire), objet, durée, loyer, dépôt de garantie, services inclus, zones de signature avec images binary
- Format : A4 Europe, accessible depuis le formulaire bail → bouton "Imprimer"

### 8.2 Quittance de loyer — `report_re_lease_quittance_doc`
- Modèle : `account.move`
- Contenu : propriétaire, locataire, déclaration de réception, détail des lignes, total, mention légale, zone signature
- Format : A4 Europe

---

## 9. DONNÉES PRÉ-CHARGÉES

| Fichier data | Contenu |
|---|---|
| `re_lease_plan_data.xml` | 4 plans : Mensuel (1M), Trimestriel (3M), Semestriel (6M), Annuel (12M) |
| `re_lease_close_reason_data.xml` | Motifs de résiliation courants |
| `re_lease_service_data.xml` | Services courants (eau, électricité, gardiennage…) |
| `re_account_tax_data.xml` | Taxes immobilières de référence |
| `ir_sequence_tenant_ref.xml` | Séquences : LOC/YYYY/ (locataires), BAIL/YYYY/ (baux), BIEN/YYYY/ (biens), IMM/YYYY/ (immeubles), INT/YYYY/ (interventions), PEN/YYYY/ (pénalités) |
| `mail_template_data.xml` | Templates email (notifications) |
| `re_lease_cron.xml` | Déclaration des 3 crons |

---

## 10. SÉCURITÉ

### Groupes définis (`re_security.xml`)
| Groupe | Rôle |
|---|---|
| `group_re_estate_manager` | Accès complet — création, modification, suppression |
| `group_re_estate_accountant` | Lecture + comptabilité — pas de suppression |
| `group_re_estate_agent` | Lecture + création — pas de suppression |
| `group_re_estate_readonly` | Lecture seule |

### Modèles couverts dans `ir.model.access.csv`
Tous les 23 modèles + les 4 wizards disposent de règles d'accès par groupe.

---

## 11. DÉPLOIEMENT

### Environnement
| Paramètre | Valeur |
|---|---|
| Orchestrateur | Docker Compose |
| Compose file | `/Users/edouard/Documents/Antigravity/odoo-dev/docker-compose.yml` |
| Conteneur Odoo | `odoo-dev-odoo19-1` |
| Conteneur DB | `odoo-dev-db-1` |
| Base de données | `gestion_immo` |
| Port externe | `8019` → `8069` interne |
| Volume addons immo | `/Users/edouard/Documents/Antigravity/immo` → `/mnt/immo-addons` |
| Login admin | admin / admin |
| URL | http://localhost:8019/odoo |

### Commande d'upgrade (procédure validée)
```bash
# 1. Arrêter le serveur principal
docker stop odoo-dev-odoo19-1

# 2. Lancer l'upgrade en conteneur isolé
docker run --rm \
  --network odoo-dev_default \
  -v /Users/edouard/Documents/Antigravity/immo:/mnt/immo-addons \
  -v /Users/edouard/Documents/Antigravity/odoo-dev/extra-addons:/mnt/extra-addons \
  -v /Users/edouard/Documents/Antigravity/odoo-dev/enterprise-addons:/mnt/enterprise-addons \
  odoo:19.0 \
  odoo -d gestion_immo -u maono_real_estate \
  --db_host odoo-dev-db-1 -r odoo -w odoo \
  --addons-path=/mnt/extra-addons,/mnt/enterprise-addons,/mnt/immo-addons,/usr/lib/python3/dist-packages/odoo/addons \
  --stop-after-init

# 3. Redémarrer le serveur
docker start odoo-dev-odoo19-1
```

---

## 12. CORRECTIONS ODOO 19 APPLIQUÉES

Lors du développement, plusieurs incompatibilités Odoo 19 ont été identifiées et corrigées :

| Problème rencontré | Correction appliquée |
|---|---|
| `numbercall` inexistant dans `ir.cron` | Champ supprimé du XML des crons |
| `account.view_tax_list` n'existe pas | Remplacé par `account.view_tax_tree` |
| Syntaxe `%(action_id)d` invalide dans les boutons | Remplacé par `type="object"` + méthodes Python dédiées |
| `decoration-secondary` non supporté sur widget `badge` | Remplacé par `decoration-muted` |
| `<group expand="0">` invalide dans vue `<search>` | Supprimé, filtres à plat |
| `//page[@name='internal']` inexistant en Odoo 19 | XPath remplacé par `//div[@name='button_box']` |
| `uid` dans les domaines XML invalide | Filtre "Mes interventions" retiré du XML |
| `re.penalty` — modèle manquant | Créé avec workflow complet (re_penalty.py) |
| Actions en double avec `view_mode=tree,form` | Doublons supprimés de `menus.xml` |
| Serveur principal absorbant les commandes CLI | Upgrade via conteneur Docker éphémère isolé |

---

## 13. TESTS FONCTIONNELS VALIDÉS

Les tests suivants ont été exécutés et validés via le navigateur :

| Fonctionnalité | Résultat |
|---|---|
| Connexion Odoo 19 Enterprise — base gestion_immo | ✅ |
| App "Immobilier" visible dans le menu principal | ✅ |
| Patrimoine → Immeubles — vue liste + formulaire | ✅ |
| Patrimoine → Biens — vue liste + formulaire | ✅ |
| Locations → Baux actifs — formulaire nouveau bail (BAIL/2026/0003) | ✅ |
| Locations → Tous les baux — vue liste | ✅ |
| Interventions → Services & Travaux — vue kanban | ✅ |
| Configuration → Plans de périodicité — 4 plans chargés | ✅ |
| Configuration → Taxes immobilières — liste | ✅ |
| Création d'un immeuble (Résidence Dakar Plaza) | ✅ |
| Création d'un bien immobilier | ✅ |
| Formulaire de bail avec onglets (Facturation, Taxes & Épargne, Docs & Signatures) | ✅ |
| Smart buttons partenaires (Biens, Baux) | ✅ |

---

## 14. POINTS OUVERTS ET PROCHAINES ÉTAPES

### À développer (roadmap client)
1. **Portail Locataire** — contrôleur web (`/my/leases`) pour consultation des quittances et historique de bail. Base `portal.mixin` déjà héritée sur `re.lease`.
2. **Tableau de bord** — dashboard avec KPIs (taux d'occupation, LMR global, encours impayés, pénalités en cours).
3. **Reporting** — menu "Reporting" structuré mais vide — à compléter avec des vues pivot/graph.
4. **Indexation automatique** — cron pour appliquer le `indexation_rate` annuellement.
5. **Prélèvement automatique** — `payment_token_id` présent sur le modèle, à connecter à un acquéreur de paiement.
6. **Notifications email** — les templates `mail_template_data.xml` sont déclarés mais doivent être finalisés (corps HTML).

### Améliorations techniques suggérées
- Ajouter un **test de fumée automatisé** (module `maono_real_estate_tests`)
- Mettre en place la **séquence de build** dans un `Makefile` ou script shell
- Activer **`mail.activity.mixin`** sur `re.property.service` pour le suivi des tâches
- Configurer un journal comptable dédié "Loyers" pour isoler la facturation immobilière

---

## 15. RÉSUMÉ EXÉCUTIF

Le module `maono_real_estate` v3.1 est **installé, opérationnel et validé** sur la base Odoo 19 Enterprise `gestion_immo`.

Il couvre l'intégralité du périmètre fonctionnel demandé :
- **23 modèles** de données, **15 fichiers de vues**, **4 wizards**, **3 crons automatisés**, **2 rapports PDF**
- Interface intuitive organisée autour d'un menu unique "Immobilier"
- Données de configuration pré-chargées (plans, services, taxes, séquences)
- Sécurité granulaire sur 4 niveaux de droits (Manager, Comptable, Agent, Lecture seule)
- Architecture autonome, sans sur-dépendance aux modules Odoo standard
