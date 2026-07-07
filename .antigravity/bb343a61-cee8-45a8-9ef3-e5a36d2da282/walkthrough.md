# Walkthrough — Version 4.1 Changes

All bugs, improvements, and feature requests identified from user feedback, screenshots, and document assets have been resolved and committed.

## Changes Made

### 1. Bug Fixes & Visual Corrections
- **Taux d'occupation correction** : Removed the redundant `widget="percentage"` from `re_building` views (form, list, kanban). The values were already calculated on a 0-100 basis, which Odoo's percentage widget multiplied by 100 → showing `6666%` instead of `66%`. A proper `%` suffix was added to raw display values and Odoo's progressbar widget was used on the form view.
- **Dashboard tabs crash fixed** : Added safety guards `|| []` to `properties_data` and `buildings_data` in both Javascript and XML components of the OWL Dashboard (`immo_dashboard.js` and `immo_dashboard.xml`). This prevents client-side rendering crashes if data parameters are temporarily undefined during module upgrade.
- **Interventions layout & scroll fixed** : Tweaked dashboard SCSS (`immo_dashboard.scss`) to resolve UI clipping on the right-hand panel:
  - Added `min-height: 0` and `overflow: visible` to the right-hand container.
  - Set a `max-height` (280px for alerts, 320px for interventions) with `overflow-y: auto` to allow scroll without clipping out of view.
- **LMR Global Rename** : Renamed all references of **LMR** to **Loyer mensuel global** / **Loyer Mensuel de Référence** in dashboard UI components to avoid confusing acronyms.

### 2. Geolocation & Automatic Partner Sync
- **Automatic Contact Creation** : Modified `re.building` to automatically spawn a `res.partner` (type: Company) upon creation and link it to the building.
- **Dynamic Field Sync** : Implemented custom `create` and `write` methods on the building model. Modifications to the building's name or address are dynamically propagated to the linked contact.
- **GPS Coordinates** : Linked the building form GPS fields directly to the linked partner (`partner_latitude` / `partner_longitude`). Added a **"📍 Voir sur la carte"** link button that opens the GPS coordinates directly in Google Maps.
- **Heritage** : The properties of an building inherit these exact GPS coordinates automatically.
- **Dependencies** : Added `base_geolocalize` to the depends section in `__manifest__.py`.

### 3. Locataires & Propriétaires Menus Fix
- **Auto-Setting Booleans** : Added overrides in `re.lease` to set `is_tenant = True` and `is_property_owner = True` automatically on contact records when a lease is created or confirmed (transitioning to `3_progress`). Previously, these menus appeared empty because Odoo only filtered on these booleans, which were never set.

### 4. Subscription-Style Manual Billing Button
- Added a prominent **"💳 Facturer"** button in the header of active leases (`3_progress`).
- Generates a draft invoice (brouillon) for the current period containing lease, tenant, property, and period details.
- Automatically advances `next_invoice_date` to the next period (monthly, quarterly, biannual, annual) based on the lease recurrence plan.

### 5. Custom Branded PDF Reports
Added three custom PDF print templates styled with **MEA & FILS** branding (Navy Blue & Gold color scheme):
1. **Reçu de paiement de loyer** (`account.payment` model) — including amount in words/numbers, tenant/owner info, and delay penalties warning clause.
2. **Fiche descriptive du bien** (`re.property` model) — listing type, surface, current tenant, lease details, and history.
3. **Fiche d'immeuble** (`re.building` model) — statistics cards, visual occupancy progress bar, and comprehensive list of goods.

---

## Verification & Deployment Steps

> [!NOTE]
> Since the integrated browser execution encountered platform limitations under macOS (`local chrome mode is only supported on Linux`), local automated browser navigation was skipped.
> However, all Python files have been successfully compiled (`py_compile` check passed) and all XML views were verified as 100% well-formed using static syntax parsers.

### To Upgrade & Deploy:
1. Trigger a repository update/pull on your **CloudPepper** server instance to pull commit `016dc37`.
2. Go to Odoo Staging: `https://staging-mila.afroit.net` (admin / capelini).
3. Access **Apps**, click **Update Apps List** (Mettre à jour la liste des applications).
4. Search for `maono_real_estate` (Module de Gestion Immobilière) and click **Upgrade** (Mettre à jour).
5. Verify the dashboard and menus.
