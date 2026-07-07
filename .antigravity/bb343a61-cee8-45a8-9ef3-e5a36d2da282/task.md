# Tasks — MILA v4.1

## Sprint 3 Improvements & Fixes

### 1. Bug Fixes
- [x] Fix taux d'occupation (6666% -> 66% with progressbar/proper formatting)
- [x] Fix dashboard tabs crash (guards in JS/XML for properties_data and buildings_data)
- [x] Fix interventions layout & scroll clipping (CSS overflow-y settings)
- [x] Rename 'LMR' to 'Loyer Mensuel' (no abbreviations in dashboard metrics)

### 2. Geolocation & Partner Integration
- [x] Auto-create Company contact `res.partner` for each building
- [x] Bidirectional sync building fields <-> contact fields
- [x] GPS coordinates support on building linked contact
- [x] Google Maps location popup link button
- [x] Property model GPS heritage from building

### 3. Locataires / Propriétaires Menus
- [x] Auto-set `is_tenant` boolean on lease creation/confirmation
- [x] Auto-set `is_property_owner` boolean on lease creation/confirmation

### 4. Subscription-Style Manual Billing Button
- [x] Implement `action_create_invoice_manual` on `re.lease`
- [x] Next billing date auto-increment & draft invoice generation
- [x] Period details (Start Date -> End Date), lease name and tenant details on invoice lines
- [x] "💳 Facturer" header button on active leases

### 5. Custom branded reports (MEA & FILS style)
- [x] Payment receipt PDF report
- [x] Property sheet PDF report
- [x] Building sheet PDF report

### 6. Deployment & Support
- [x] Static syntax verification (Python compilation & XML verification)
- [x] Push commits to main branch
- [x] Update documentation guide (`DOCUMENTATION_UTILISATEUR.md`) to Version 4.1
