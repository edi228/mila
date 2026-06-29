# -*- coding: utf-8 -*-
"""
Migration 19.0.4.0 — Script pre-migrate
Crée les colonnes manquantes sur res_partner avant le chargement des modèles.
Cela évite le KeyError/UndefinedColumn lors de l'upgrade.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Ajoute les colonnes v4.0 sur res_partner si elles n'existent pas."""
    if not version:
        return

    columns_to_add = [
        # (table, colonne, type_sql, default)
        ('res_partner', 're_contact_type',           'VARCHAR',  None),
        ('res_partner', 'identity_doc_type',          'VARCHAR',  None),
        ('res_partner', 'identity_doc_number',        'VARCHAR',  None),
        ('res_partner', 'identity_doc_expiry',        'DATE',     None),
        ('res_partner', 'identity_doc_expired',       'BOOLEAN',  'FALSE'),
        ('res_partner', 'identity_doc_scan_name',     'VARCHAR',  None),
        ('res_partner', 'identity_doc_scan_back_name','VARCHAR',  None),
        # re.building
        ('re_building', 'geo_partner_id',             'INTEGER',  None),
        ('re_building', 'latitude',                   'NUMERIC(10,7)', '0'),
        ('re_building', 'longitude',                  'NUMERIC(10,7)', '0'),
        # re.property
        ('re_property', 'latitude',                   'NUMERIC(10,7)', '0'),
        ('re_property', 'longitude',                  'NUMERIC(10,7)', '0'),
    ]

    for table, col, col_type, default in columns_to_add:
        cr.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name=%s AND column_name=%s",
            (table, col)
        )
        if not cr.fetchone():
            default_clause = f" DEFAULT {default}" if default is not None else ""
            cr.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{col}" {col_type}{default_clause}'
            )
            _logger.info("Migration 4.0: colonne %s.%s créée", table, col)
        else:
            _logger.info("Migration 4.0: colonne %s.%s déjà présente", table, col)
