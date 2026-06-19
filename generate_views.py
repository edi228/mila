import os

base_path = '/Users/edouard/Documents/Antigravity/immo/maono_real_estate'

# --- 1. MENUS.XML ---
menus_xml = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Root Menu -->
    <menuitem id="menu_re_root" name="Immobilier" web_icon="maono_real_estate,static/description/icon.png" sequence="10"/>

    <!-- Level 1 -->
    <menuitem id="menu_re_dashboard" name="Tableau de bord" parent="menu_re_root" sequence="10" action="action_re_dashboard_dummy"/>
    <menuitem id="menu_re_patrimoine" name="Patrimoine" parent="menu_re_root" sequence="20"/>
    <menuitem id="menu_re_locations" name="Locations" parent="menu_re_root" sequence="30"/>
    <menuitem id="menu_re_facturation" name="Facturation" parent="menu_re_root" sequence="40"/>
    <menuitem id="menu_re_interventions" name="Interventions" parent="menu_re_root" sequence="50"/>
    <menuitem id="menu_re_reporting" name="Reporting" parent="menu_re_root" sequence="80"/>
    <menuitem id="menu_re_config" name="Configuration" parent="menu_re_root" sequence="100"/>

    <!-- Level 2: Patrimoine -->
    <menuitem id="menu_re_building" name="Immeubles" parent="menu_re_patrimoine" sequence="10" action="action_re_building"/>
    <menuitem id="menu_re_property" name="Biens" parent="menu_re_patrimoine" sequence="20" action="action_re_property"/>

    <!-- Level 2: Locations -->
    <menuitem id="menu_re_lease_active" name="Baux actifs" parent="menu_re_locations" sequence="10" action="action_re_lease_active"/>
    <menuitem id="menu_re_lease_all" name="Tous les baux" parent="menu_re_locations" sequence="20" action="action_re_lease_all"/>

    <!-- Level 2: Interventions -->
    <menuitem id="menu_re_service" name="Services &amp; Travaux" parent="menu_re_interventions" sequence="10" action="action_re_property_service"/>

    <!-- Level 2: Configuration -->
    <menuitem id="menu_re_config_plan" name="Plans de périodicité" parent="menu_re_config" sequence="10" action="action_re_lease_plan"/>
    <menuitem id="menu_re_config_tax" name="Taxes immobilières" parent="menu_re_config" sequence="20" action="action_re_tax_real_estate"/>
</odoo>
"""

# --- 2. RE_PROPERTY_VIEWS.XML ---
re_property_views = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_re_property_form" model="ir.ui.view">
        <field name="name">re.property.form</field>
        <field name="model">re.property</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <field name="state" widget="statusbar" statusbar_visible="available,occupied"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="%(action_re_lease_all)d" type="action" class="oe_stat_button" icon="fa-file-text-o">
                            <field name="active_lease_id" widget="statinfo" string="Bail actif"/>
                        </button>
                    </div>
                    <widget name="web_ribbon" title="Archivé" bg_color="bg-danger" invisible="active"/>
                    <field name="active" invisible="1"/>
                    <field name="image_ids" widget="many2many_image_gallery" class="oe_avatar"/>
                    <div class="oe_title">
                        <h1><field name="ref" readonly="1"/> - <field name="name" placeholder="Nom du bien"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="type"/>
                            <field name="building_id"/>
                            <field name="owner_id"/>
                        </group>
                        <group>
                            <field name="rent_amount"/>
                            <field name="currency_id" invisible="1"/>
                            <field name="surface"/>
                            <field name="rooms"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Description">
                            <field name="description"/>
                        </page>
                        <page string="Équipements">
                            <field name="amenities"/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <record id="view_re_property_tree" model="ir.ui.view">
        <field name="name">re.property.tree</field>
        <field name="model">re.property</field>
        <field name="arch" type="xml">
            <tree decoration-success="state=='available'" decoration-info="state=='occupied'" decoration-warning="state=='works'">
                <field name="ref"/>
                <field name="name"/>
                <field name="type"/>
                <field name="owner_id"/>
                <field name="rent_amount"/>
                <field name="state" widget="badge" decoration-success="state=='available'" decoration-info="state=='occupied'" decoration-warning="state=='works'" decoration-danger="state=='suspended'"/>
            </tree>
        </field>
    </record>

    <record id="action_re_property" model="ir.actions.act_window">
        <field name="name">Biens immobiliers</field>
        <field name="res_model">re.property</field>
        <field name="view_mode">tree,form,kanban</field>
    </record>
    
    <record id="action_re_dashboard_dummy" model="ir.actions.act_window">
        <field name="name">Dashboard</field>
        <field name="res_model">re.property</field>
        <field name="view_mode">kanban,tree</field>
    </record>
</odoo>
"""

# --- 3. RE_LEASE_VIEWS.XML ---
re_lease_views = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_re_lease_form" model="ir.ui.view">
        <field name="name">re.lease.form</field>
        <field name="model">re.lease</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirmer" type="object" class="oe_highlight" invisible="lease_state != '1_draft'"/>
                    <button name="action_renew_lease" string="Renouveler" type="object" invisible="lease_state not in ('3_progress', '4_paused')"/>
                    <button name="action_pause" string="Suspendre" type="object" invisible="lease_state != '3_progress'"/>
                    <button name="action_resume" string="Reprendre" type="object" invisible="lease_state != '4_paused'"/>
                    <field name="lease_state" widget="statusbar" statusbar_visible="1_draft,3_progress,6_churn"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>
                    <group>
                        <group string="Contrat">
                            <field name="property_id"/>
                            <field name="tenant_id"/>
                            <field name="tenant_ref_snapshot"/>
                            <field name="guarantor_id"/>
                            <field name="lease_type"/>
                            <field name="plan_id"/>
                            <field name="start_date"/>
                            <field name="end_date"/>
                        </group>
                        <group string="Financier">
                            <field name="rent_amount"/>
                            <field name="currency_id" invisible="1"/>
                            <field name="advance_months"/>
                            <field name="advance_amount"/>
                            <field name="deposit_amount"/>
                            <field name="signature_total"/>
                            <field name="next_invoice_date"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lignes de facturation">
                            <field name="line_ids">
                                <tree editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="recurring_invoice"/>
                                    <field name="price_subtotal"/>
                                </tree>
                            </field>
                        </page>
                        <page string="Taxes &amp; Épargne">
                            <group>
                                <field name="tax_line_ids" nolabel="1">
                                    <tree editable="bottom">
                                        <field name="tax_id"/>
                                        <field name="tax_bearer"/>
                                        <field name="tenant_share_percent"/>
                                        <field name="tax_amount_tenant"/>
                                        <field name="tax_amount_owner"/>
                                    </tree>
                                </field>
                            </group>
                        </page>
                        <page string="Docs &amp; Signatures">
                            <group>
                                <field name="signature_tenant" widget="signature"/>
                                <field name="signature_owner" widget="signature"/>
                                <field name="is_fully_signed"/>
                                <field name="contract_pdf_id"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <record id="view_re_lease_tree" model="ir.ui.view">
        <field name="name">re.lease.tree</field>
        <field name="model">re.lease</field>
        <field name="arch" type="xml">
            <tree decoration-info="lease_state=='1_draft'" decoration-success="lease_state=='3_progress'">
                <field name="name"/>
                <field name="property_id"/>
                <field name="tenant_id"/>
                <field name="start_date"/>
                <field name="rent_amount"/>
                <field name="lease_state" widget="badge" decoration-success="lease_state=='3_progress'"/>
            </tree>
        </field>
    </record>

    <record id="action_re_lease_all" model="ir.actions.act_window">
        <field name="name">Tous les baux</field>
        <field name="res_model">re.lease</field>
        <field name="view_mode">tree,form</field>
    </record>

    <record id="action_re_lease_active" model="ir.actions.act_window">
        <field name="name">Baux Actifs</field>
        <field name="res_model">re.lease</field>
        <field name="view_mode">tree,form</field>
        <field name="domain">[('lease_state', '=', '3_progress')]</field>
    </record>
    
    <record id="action_re_building" model="ir.actions.act_window">
        <field name="name">Immeubles</field>
        <field name="res_model">re.building</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
"""

# --- 4. DATA SEQUENCES & BASIC CONFIG ---
data_sequence = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="seq_re_tenant_ref" model="ir.sequence">
            <field name="name">Référence locataire</field>
            <field name="code">re.tenant.ref</field>
            <field name="prefix">LOC/%(year)s/</field>
            <field name="padding">5</field>
        </record>
        
        <record id="seq_re_lease" model="ir.sequence">
            <field name="name">Contrat Bail</field>
            <field name="code">re.lease.seq</field>
            <field name="prefix">BAIL/%(year)s/</field>
            <field name="padding">4</field>
        </record>
        
        <record id="seq_re_property" model="ir.sequence">
            <field name="name">Bien</field>
            <field name="code">re.property.seq</field>
            <field name="prefix">BIEN/%(year)s/</field>
            <field name="padding">4</field>
        </record>
    </data>
</odoo>
"""

# Override views files
import sys

def write_f(rel_path, data):
    with open(os.path.join(base_path, rel_path), 'w') as f:
        f.write(data)

write_f('views/menus.xml', menus_xml)
write_f('views/re_property_views.xml', re_property_views)
write_f('views/re_lease_views.xml', re_lease_views)
write_f('data/ir_sequence_tenant_ref.xml', data_sequence)

print("Views and base Data generated.")
