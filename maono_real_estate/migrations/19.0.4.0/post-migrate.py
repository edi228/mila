# -*- coding: utf-8 -*-
"""
Migration 19.0.4.0 — Post-migrate
Initialise les données après le chargement complet des modèles v4.0.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    - Initialise re_contact_type depuis les booléens existants (is_tenant > is_property_owner > is_guarantor)
    - Initialise identity_doc_expired = FALSE pour tous les partenaires existants
    - Initialise lat/lng = 0 pour les biens/immeubles existants
    """
    if not version:
        return

    # Initialiser re_contact_type depuis les booléens (pour les contacts existants)
    cr.execute("""
        UPDATE res_partner
        SET re_contact_type = CASE
            WHEN is_tenant = TRUE       THEN 'tenant'
            WHEN is_property_owner = TRUE THEN 'owner'
            WHEN is_guarantor = TRUE    THEN 'guarantor'
            ELSE NULL
        END
        WHERE re_contact_type IS NULL
          AND (is_tenant = TRUE OR is_property_owner = TRUE OR is_guarantor = TRUE)
    """)
    _logger.info("Migration 4.0: re_contact_type initialisé pour %d contacts", cr.rowcount)

    # S'assurer que identity_doc_expired n'est pas NULL
    cr.execute("""
        UPDATE res_partner
        SET identity_doc_expired = FALSE
        WHERE identity_doc_expired IS NULL
    """)
    _logger.info("Migration 4.0: identity_doc_expired initialisé")

    # Initialiser lat/lng à 0 si NULL
    cr.execute("""
        UPDATE re_building
        SET latitude = 0, longitude = 0
        WHERE latitude IS NULL OR longitude IS NULL
    """)
    cr.execute("""
        UPDATE re_property
        SET latitude = 0, longitude = 0
        WHERE latitude IS NULL OR longitude IS NULL
    """)
    _logger.info("Migration 4.0: coordonnées GPS initialisées à 0")
