#!/usr/bin/env python3
"""
Script de création de données de test pour le module immobilier MILA.
Utilise JSON-RPC via le cookie de session Odoo.
"""

import json
import requests
import sys

BASE_URL = "https://mila.afroit.net"
SESSION_COOKIE = "dfbK5_eUkFJr67xb79-ONv9gGywfEm5I_zF9F-ttx4ZiAtxgdYpoYoSNepSC_AQRo1XIBPXLtOw9mWB60xVc"

session = requests.Session()
session.cookies.set("session_id", SESSION_COOKIE)
session.headers.update({"Content-Type": "application/json"})

call_id = [0]

def rpc(model, method, args=None, kwargs=None):
    call_id[0] += 1
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": call_id[0],
        "params": {
            "model": model,
            "method": method,
            "args": args or [],
            "kwargs": kwargs or {}
        }
    }
    resp = session.post(f"{BASE_URL}/web/dataset/call_kw", json=payload)
    data = resp.json()
    if "error" in data:
        print(f"  ❌ ERREUR RPC [{model}.{method}]: {data['error']['data'].get('message', data['error'])}", file=sys.stderr)
        return None
    return data["result"]

def create(model, vals):
    result = rpc(model, "create", [[vals]])
    if result:
        print(f"  ✅ Créé {model} id={result}")
    return result

def write(model, ids, vals):
    result = rpc(model, "write", [[ids] if isinstance(ids, int) else ids, vals])
    if result:
        print(f"  ✅ Mis à jour {model} ids={ids}")
    return result

def search_read(model, domain, fields, limit=10):
    return rpc(model, "search_read", [domain], {"fields": fields, "limit": limit})

print("=" * 60)
print("CRÉATION DES DONNÉES DE TEST - MILA IMMOBILIER")
print("=" * 60)

results = {}

# =============================================================
# 1. NOUVEAUX LOCATAIRES (res.partner)
# =============================================================
print("\n### 1. Création des locataires ###")

partner_marcel = create("res.partner", {
    "name": "Marcel Togbe",
    "phone": "+228 91 23 45 67",
    "email": "m.togbe@email.com",
    "company_id": 1,
    "is_company": False,
    "customer_rank": 1,
})
results["partner_marcel_id"] = partner_marcel

partner_fatima = create("res.partner", {
    "name": "Fatima Ouedraogo",
    "phone": "+228 77 88 99 00",
    "email": "fatima.o@email.com",
    "company_id": 1,
    "is_company": False,
    "customer_rank": 1,
})
results["partner_fatima_id"] = partner_fatima

partner_techtogo = create("res.partner", {
    "name": "Société TechTogo SARL",
    "email": "contact@techtogo.tg",
    "company_id": 1,
    "is_company": True,
    "customer_rank": 1,
})
results["partner_techtogo_id"] = partner_techtogo

print(f"  Marcel Togbe id={partner_marcel}, Fatima Ouedraogo id={partner_fatima}, TechTogo id={partner_techtogo}")

# =============================================================
# 2. NOUVEAUX BIENS (re.property)
# =============================================================
print("\n### 2. Création des biens immobiliers ###")

prop_2b = create("re.property", {
    "name": "Appartement 2B",
    "property_type": "residential",
    "building_id": 1,
    "lmr": 120000,
    "surface": 65.0,
    "rooms": 2,
    "company_id": 1,
})
results["prop_2b_id"] = prop_2b

prop_studio = create("re.property", {
    "name": "Studio 1A",
    "property_type": "residential",
    "building_id": 1,
    "lmr": 75000,
    "surface": 35.0,
    "rooms": 1,
    "company_id": 1,
})
results["prop_studio_id"] = prop_studio

prop_magasin = create("re.property", {
    "name": "Magasin RDC",
    "property_type": "commercial",
    "building_id": 1,
    "lmr": 200000,
    "surface": 120.0,
    "rooms": 1,
    "company_id": 1,
})
results["prop_magasin_id"] = prop_magasin

print(f"  Appartement 2B id={prop_2b}, Studio 1A id={prop_studio}, Magasin RDC id={prop_magasin}")

# =============================================================
# 3. NOUVEAUX BAUX (re.lease)
# =============================================================
print("\n### 3. Création des baux ###")

lease_2b = create("re.lease", {
    "property_id": prop_2b,
    "tenant_id": partner_marcel,
    "lmr": 120000,
    "deposit": 240000,
    "date_start": "2026-03-01",
    "date_end": "2027-02-28",
    "lease_state": "3_progress",
    "lease_type": "monthly",
    "recurrence_id": 1,
    "company_id": 1,
})
results["lease_2b_id"] = lease_2b

lease_studio = create("re.lease", {
    "property_id": prop_studio,
    "tenant_id": partner_fatima,
    "lmr": 75000,
    "deposit": 150000,
    "date_start": "2026-05-01",
    "date_end": "2027-04-30",
    "lease_state": "3_progress",
    "lease_type": "monthly",
    "company_id": 1,
})
results["lease_studio_id"] = lease_studio

print(f"  Bail Appart 2B id={lease_2b}, Bail Studio 1A id={lease_studio}")

# Mettre à jour les biens comme occupés
if prop_2b:
    write("re.property", prop_2b, {"state": "occupied"})
if prop_studio:
    write("re.property", prop_studio, {"state": "occupied"})

# =============================================================
# 4. FACTURES PAYÉES
# =============================================================
print("\n### 4. Création des factures ###")

# Trouver un journal de trésorerie (cash/bank) pour la company 1
cash_journals = search_read(
    "account.journal",
    [["type", "in", ["cash", "bank"]], ["company_id", "=", 1]],
    ["id", "name", "type"]
)
print(f"  Journaux trésorerie disponibles: {cash_journals}")
payment_journal_id = cash_journals[0]["id"] if cash_journals else None
results["payment_journal_id"] = payment_journal_id

# Facture 1: Loyer Mars 2026 - Marcel Togbe
inv_marcel = create("account.move", {
    "move_type": "out_invoice",
    "partner_id": partner_marcel,
    "journal_id": 13,
    "invoice_date": "2026-03-01",
    "invoice_date_due": "2026-03-31",
    "company_id": 1,
    "invoice_line_ids": [(0, 0, {
        "name": "Loyer Mars 2026 - Appartement 2B",
        "quantity": 1,
        "price_unit": 120000,
        "account_id": 2141,
    })],
})
results["inv_marcel_id"] = inv_marcel

# Poster la facture Marcel
if inv_marcel:
    post_result = rpc("account.move", "action_post", [[inv_marcel]])
    print(f"  ✅ Facture Marcel postée (id={inv_marcel})")

# Facture 2: Loyer Mai 2026 - Fatima Ouedraogo
inv_fatima = create("account.move", {
    "move_type": "out_invoice",
    "partner_id": partner_fatima,
    "journal_id": 13,
    "invoice_date": "2026-05-01",
    "invoice_date_due": "2026-05-31",
    "company_id": 1,
    "invoice_line_ids": [(0, 0, {
        "name": "Loyer Mai 2026 - Studio 1A",
        "quantity": 1,
        "price_unit": 75000,
        "account_id": 2141,
    })],
})
results["inv_fatima_id"] = inv_fatima

if inv_fatima:
    post_result = rpc("account.move", "action_post", [[inv_fatima]])
    print(f"  ✅ Facture Fatima postée (id={inv_fatima})")

# Payer les factures via account.payment.register
print("\n### 4b. Paiement des factures ###")
if inv_marcel and payment_journal_id:
    try:
        pay_ctx = {
            "active_model": "account.move",
            "active_ids": [inv_marcel],
        }
        pay_register = rpc("account.payment.register", "with_context", [], {"context": pay_ctx})
        # En Odoo 19, on crée directement le wizard
        wizard_id = create("account.payment.register", {
            "journal_id": payment_journal_id,
            "payment_date": "2026-03-01",
            "amount": 120000,
        })
        if wizard_id:
            # action_create_payments via le wizard
            rpc("account.payment.register", "action_create_payments", [[wizard_id]])
            print(f"  ✅ Facture Marcel payée")
    except Exception as e:
        print(f"  ⚠️  Paiement Marcel échoué: {e}")

# Approche alternative pour paiement: créer directement account.payment
if inv_marcel and payment_journal_id:
    print("  Tentative paiement direct account.payment...")
    
    # Récupérer la ligne de débit de la facture (receivable)
    inv_lines = search_read(
        "account.move.line",
        [["move_id", "=", inv_marcel], ["account_type", "=", "asset_receivable"]],
        ["id", "account_id", "balance", "amount_residual"]
    )
    print(f"  Lignes receivable facture Marcel: {inv_lines}")

print(f"\n  Facture Marcel id={inv_marcel}, Facture Fatima id={inv_fatima}")

# =============================================================
# 5. INTERVENTION URGENTE
# =============================================================
print("\n### 5. Création de l'intervention ###")

intervention = create("re.property.service", {
    "name": "Réparation porte d'entrée cassée",
    "property_id": prop_magasin,
    "service_type": "repair",
    "priority": "2",
    "state": "approved",
    "estimated_cost": 50000,
    "company_id": 1,
})
results["intervention_id"] = intervention
print(f"  Intervention id={intervention}")

# =============================================================
# RAPPORT FINAL
# =============================================================
print("\n" + "=" * 60)
print("RAPPORT FINAL - IDs CRÉÉS")
print("=" * 60)
for key, val in results.items():
    print(f"  {key}: {val}")

print("\nDétail des baux créés:")
if lease_2b:
    bail_data = search_read("re.lease", [["id", "=", lease_2b]], 
                             ["name", "property_id", "tenant_id", "lmr", "lease_state"])
    print(f"  Bail 2B: {bail_data}")
if lease_studio:
    bail_data = search_read("re.lease", [["id", "=", lease_studio]], 
                             ["name", "property_id", "tenant_id", "lmr", "lease_state"])
    print(f"  Bail Studio: {bail_data}")

print("\nDétail des biens créés:")
props = search_read("re.property", [["id", "in", [prop_2b, prop_studio, prop_magasin]]],
                     ["name", "property_type", "state", "lmr"])
for p in (props or []):
    print(f"  {p}")

print("\nScript terminé!")
