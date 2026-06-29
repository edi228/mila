# Tasks — MILA v4.0 Sprint 1

## Sprint 1 (Chantiers 1 + 2 + 4)

### Chantier 1 — Renommage Garantie → Caution
- [ ] models/re_lease.py — labels deposit_amount, deposit_paid, deposit_returned, deposit_deductions
- [ ] views/re_lease_views.xml — tous les string= "Dépôt de garantie"
- [ ] report/re_lease_contract_report.xml — label rapport
- [ ] report/re_lease_quittance_report.xml — label si applicable

### Chantier 2 — Contacts & Locataires
- [ ] models/res_partner.py — re_contact_type + identity fields (type, number, scan, expiry)
- [ ] views/res_partner_views.xml — onglet Immobilier
- [ ] views/re_lease_views.xml — onglet Locataire inline (téléphone, email, identité)
- [ ] security/ir.model.access.csv — droits si nouveau champ attachment

### Chantier 4 — Menus restructurés
- [ ] views/menus.xml — nouveau menu Locataires, remonter Pénalités, nouveau menu Finances
- [ ] views/re_lease_views.xml — actions filtrées pour Quittances et Paiements
- [ ] Nouvelle action ir.actions pour menu Locataires (res.partner filtré)

### Finalisation Sprint 1
- [ ] __manifest__.py — bump version 3.3 → 4.0
- [ ] Push GitHub + update CloudPepper
- [ ] Tests fonctionnels
