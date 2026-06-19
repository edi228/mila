#!/usr/bin/env python3
"""
Script de création de données de test pour le module immobilier MILA.
Version corrigée avec les vrais noms de champs.
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
        msg = data['error']['data'].get('message', str(data['error']))
        print(f"  ❌ ERREUR [{model}.{method}]: {msg}", file=sys.stderr)
        return None
    return data["result"]

def create(model, vals):
    result = rpc(model, "create", [[vals]])
    if result:
        rid = result if isinstance(result, int) else result[0] if isinstance(result, list) else result
        print(f"  ✅ Créé {model} id={rid}")
        return rid
    return None

def write(model, ids, vals):
    ids_list = [ids] if isinstance(ids, int) else ids
    result = rpc(model, "write", [ids_list, vals])
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
# Vérifier si les partenaires existent déjà (créés au run précédent)
# =============================================================
print("\n### Vérification des partenaires existants ###")
existing_partners = search_read(
    "res.partner",
    [["id", "in", [12, 13, 14]]],
    ["id", "name", "email"]
)
print(f"  Partenaires existants: {existing_partners}")

if existing_partners and len(existing_partners) == 3:
    partner_ids = {p["name"]: p["id"] for p in existing_partners}
    partner_marcel = partner_ids.get("Marcel Togbe", 12)
    partner_fatima = partner_ids.get("Fatima Ouedraogo", 13)
    partner_techtogo = partner_ids.get("Société TechTogo SARL", 14)
    print(f"  Réutilisation: Marcel={partner_marcel}, Fatima={partner_fatima}, TechTogo={partner_techtogo}")
else:
    # Recréer si besoin
    print("\n### 1. Création des locataires ###")
    partner_marcel = create("res.partner", {
        "name": "Marcel Togbe",
        "phone": "+228 91 23 45 67",
        "email": "m.togbe@email.com",
        "company_id": 1,
        "is_company": False,
        "customer_rank": 1,
    })
    partner_fatima = create("res.partner", {
        "name": "Fatima Ouedraogo",
        "phone": "+228 77 88 99 00",
        "email": "fatima.o@email.com",
        "company_id": 1,
        "is_company": False,
        "customer_rank": 1,
    })
    partner_techtogo = create("res.partner", {
        "name": "Société TechTogo SARL",
        "email": "contact@techtogo.tg",
        "company_id": 1,
        "is_company": True,
        "customer_rank": 1,
    })

results["partner_marcel_id"] = partner_marcel
results["partner_fatima_id"] = partner_fatima
results["partner_techtogo_id"] = partner_techtogo

# =============================================================
# 2. NOUVEAUX BIENS (re.property) - champ "type" et "rent_amount"
# =============================================================
print("\n### 2. Création des biens immobiliers ###")

prop_2b = create("re.property", {
    "name": "Appartement 2B",
    "type": "residential",
    "building_id": 1,
    "rent_amount": 120000,
    "surface": 65.0,
    "rooms": 2,
})
results["prop_2b_id"] = prop_2b

prop_studio = create("re.property", {
    "name": "Studio 1A",
    "type": "residential",
    "building_id": 1,
    "rent_amount": 75000,
    "surface": 35.0,
    "rooms": 1,
})
results["prop_studio_id"] = prop_studio

prop_magasin = create("re.property", {
    "name": "Magasin RDC",
    "type": "commercial",
    "building_id": 1,
    "rent_amount": 200000,
    "surface": 120.0,
    "rooms": 1,
})
results["prop_magasin_id"] = prop_magasin

print(f"  Appartement 2B id={prop_2b}, Studio 1A id={prop_studio}, Magasin RDC id={prop_magasin}")

# =============================================================
# 3. NOUVEAUX BAUX (re.lease)
# Champs corrects: rent_amount, deposit_amount, start_date, end_date, plan_id
# =============================================================
print("\n### 3. Création des baux ###")

lease_2b = None
lease_studio = None

if prop_2b and partner_marcel:
    lease_2b = create("re.lease", {
        "property_id": prop_2b,
        "tenant_id": partner_marcel,
        "rent_amount": 120000,
        "deposit_amount": 240000,
        "start_date": "2026-03-01",
        "end_date": "2027-02-28",
        "lease_state": "3_progress",
        "lease_type": "monthly",
        "plan_id": 1,
    })

if prop_studio and partner_fatima:
    lease_studio = create("re.lease", {
        "property_id": prop_studio,
        "tenant_id": partner_fatima,
        "rent_amount": 75000,
        "deposit_amount": 150000,
        "start_date": "2026-05-01",
        "end_date": "2027-04-30",
        "lease_state": "3_progress",
        "lease_type": "monthly",
    })

results["lease_2b_id"] = lease_2b
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
print("\n### 4. Création et paiement des factures ###")

# Trouver le journal de trésorerie
cash_journals = search_read(
    "account.journal",
    [["type", "in", ["cash", "bank"]], ["company_id", "=", 1]],
    ["id", "name", "type"]
)
print(f"  Journaux trésorerie: {cash_journals}")
payment_journal_id = cash_journals[0]["id"] if cash_journals else 18
results["payment_journal_id"] = payment_journal_id

# Facture 1: Loyer Mars 2026 - Marcel Togbe
inv_marcel = None
if partner_marcel:
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

if inv_marcel:
    post_result = rpc("account.move", "action_post", [[inv_marcel]])
    print(f"  ✅ Facture Marcel postée: id={inv_marcel}")

# Facture 2: Loyer Mai 2026 - Fatima Ouedraogo
inv_fatima = None
if partner_fatima:
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

if inv_fatima:
    post_result = rpc("account.move", "action_post", [[inv_fatima]])
    print(f"  ✅ Facture Fatima postée: id={inv_fatima}")

results["inv_marcel_id"] = inv_marcel
results["inv_fatima_id"] = inv_fatima

# Paiement des factures via account.payment.register
print("\n### 4b. Paiement des factures ###")

def pay_invoice(invoice_id, amount, pay_date, partner_id):
    """Payer une facture via account.payment.register"""
    # Créer le wizard de paiement avec contexte
    call_id[0] += 1
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": call_id[0],
        "params": {
            "model": "account.payment.register",
            "method": "with_context",
            "args": [],
            "kwargs": {
                "context": {
                    "active_model": "account.move",
                    "active_ids": [invoice_id],
                    "active_id": invoice_id,
                }
            }
        }
    }
    # En Odoo 19, on peut utiliser action_register_payment sur l'invoice
    # Puis appeler create+action_create_payments sur le wizard
    
    # Méthode directe: créer account.payment
    payment_id = create("account.payment", {
        "payment_type": "inbound",
        "partner_type": "customer",
        "partner_id": partner_id,
        "amount": amount,
        "date": pay_date,
        "journal_id": payment_journal_id,
        "company_id": 1,
    })
    if payment_id:
        # Poster le paiement
        post_res = rpc("account.payment", "action_post", [[payment_id]])
        if post_res is not None:
            print(f"  ✅ Paiement posté id={payment_id}")
            # Réconcilier avec la facture
            # Trouver les lignes receivable du paiement et de la facture
            pay_lines = search_read(
                "account.move.line",
                [["payment_id", "=", payment_id], ["account_type", "=", "asset_receivable"]],
                ["id", "balance"]
            )
            inv_lines = search_read(
                "account.move.line",
                [["move_id", "=", invoice_id], ["account_type", "=", "asset_receivable"]],
                ["id", "balance"]
            )
            print(f"  Lignes paiement receivable: {pay_lines}")
            print(f"  Lignes facture receivable: {inv_lines}")
            
            if pay_lines and inv_lines:
                all_line_ids = [l["id"] for l in pay_lines + inv_lines]
                reconcile_res = rpc("account.move.line", "reconcile", [all_line_ids])
                if reconcile_res is not None:
                    print(f"  ✅ Réconciliation effectuée")
                else:
                    print(f"  ⚠️  Réconciliation échouée")
        return payment_id
    return None

if inv_marcel and partner_marcel:
    pay_id_1 = pay_invoice(inv_marcel, 120000, "2026-03-01", partner_marcel)
    results["pay_marcel_id"] = pay_id_1

if inv_fatima and partner_fatima:
    pay_id_2 = pay_invoice(inv_fatima, 75000, "2026-05-01", partner_fatima)
    results["pay_fatima_id"] = pay_id_2

# =============================================================
# 5. INTERVENTION URGENTE (re.property.service)
# =============================================================
print("\n### 5. Création de l'intervention ###")

intervention = None
if prop_magasin:
    intervention = create("re.property.service", {
        "name": "Réparation porte d'entrée cassée",
        "property_id": prop_magasin,
        "service_type": "repair",
        "priority": "2",
        "state": "approved",
        "estimated_cost": 50000,
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

print("\n--- Détail des biens créés ---")
prop_ids = [p for p in [prop_2b, prop_studio, prop_magasin] if p]
if prop_ids:
    props = search_read("re.property", [["id", "in", prop_ids]],
                         ["id", "name", "type", "state", "rent_amount"])
    for p in (props or []):
        print(f"  {p}")

print("\n--- Détail des baux créés ---")
lease_ids = [l for l in [lease_2b, lease_studio] if l]
if lease_ids:
    leases = search_read("re.lease", [["id", "in", lease_ids]],
                          ["id", "name", "property_id", "tenant_id", "lmr", "lease_state", "start_date", "end_date"])
    for l in (leases or []):
        print(f"  {l}")

print("\n--- Détail des factures ---")
inv_ids = [i for i in [inv_marcel, inv_fatima] if i]
if inv_ids:
    invs = search_read("account.move", [["id", "in", inv_ids]],
                        ["id", "name", "partner_id", "amount_total", "payment_state", "state"])
    for i in (invs or []):
        print(f"  {i}")

print("\n--- Détail de l'intervention ---")
if intervention:
    servs = search_read("re.property.service", [["id", "=", intervention]],
                         ["id", "name", "property_id", "service_type", "priority", "state", "estimated_cost"])
    for s in (servs or []):
        print(f"  {s}")

print("\n✅ Script terminé!")
