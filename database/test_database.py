# database/test_database.py

from database.connection import SessionLocal

from database.models import (
    DataLayer,
    Case,
    Entity,
    Evidence,
    Relationship,
    Event,
    EntityEvidence,
    CDRRecord,
    CCTVObservation,
    CourtRecord,
    FinancialRecord,
)


def test_database():

    db = SessionLocal()

    try:

        print("\n")
        print("=" * 60)
        print("CRIMINAL NETWORK ANALYZER")
        print("DATABASE VERIFICATION")
        print("=" * 60)

        # =====================================================
        # LAYERS
        # =====================================================

        print("\nDATA LAYERS")
        print("-" * 40)

        layers = (
            db.query(DataLayer)
            .order_by(DataLayer.id)
            .all()
        )

        for layer in layers:

            print(
                f"{layer.id}. "
                f"{layer.layer_code} - "
                f"{layer.layer_name}"
            )

        # =====================================================
        # COUNTS
        # =====================================================

        print("\nDATABASE COUNTS")
        print("-" * 40)

        print(
            "Cases:",
            db.query(Case).count()
        )

        print(
            "Entities:",
            db.query(Entity).count()
        )

        print(
            "Evidence:",
            db.query(Evidence).count()
        )

        print(
            "Relationships:",
            db.query(Relationship).count()
        )

        print(
            "Events:",
            db.query(Event).count()
        )

        print(
            "Entity-Evidence links:",
            db.query(EntityEvidence).count()
        )

        print(
            "CDR records:",
            db.query(CDRRecord).count()
        )

        print(
            "CCTV observations:",
            db.query(CCTVObservation).count()
        )

        print(
            "Court records:",
            db.query(CourtRecord).count()
        )

        print(
            "Financial records:",
            db.query(FinancialRecord).count()
        )

        # =====================================================
        # ENTITY TYPES
        # =====================================================

        print("\nENTITY TYPES")
        print("-" * 40)

        entity_types = (
            db.query(Entity.entity_type)
            .distinct()
            .all()
        )

        for entity_type in entity_types:

            count = (
                db.query(Entity)
                .filter(
                    Entity.entity_type ==
                    entity_type[0]
                )
                .count()
            )

            print(
                f"{entity_type[0]}: {count}"
            )

        # =====================================================
        # CASES
        # =====================================================

        print("\nCASES")
        print("-" * 40)

        cases = (
            db.query(Case)
            .filter(
                Case.case_type == "FIR"
            )
            .order_by(Case.fir_number)
            .all()
        )

        for case in cases:

            print(
                f"{case.id} | "
                f"FIR {case.fir_number} | "
                f"{case.police_station}"
            )

        # =====================================================
        # CROSS-LAYER RELATIONSHIPS
        # =====================================================

        print("\nCROSS-LAYER RELATIONSHIPS")
        print("-" * 40)

        relationships = (
            db.query(Relationship)
            .join(
                DataLayer,
                Relationship.layer_id ==
                DataLayer.id
            )
            .all()
        )

        for relation in relationships[:30]:

            print(
                f"{relation.source_entity_id} "
                f"--[{relation.relationship_type}]--> "
                f"{relation.target_entity_id} "
                f"| layer={relation.layer_id}"
            )

        # =====================================================
        # CDR
        # =====================================================

        print("\nCDR SAMPLE")
        print("-" * 40)

        cdr_records = (
            db.query(CDRRecord)
            .limit(10)
            .all()
        )

        for record in cdr_records:

            print(
                f"{record.caller_phone} "
                f"→ "
                f"{record.receiver_phone} "
                f"| {record.timestamp} "
                f"| {record.duration_seconds}s"
            )

        # =====================================================
        # CCTV
        # =====================================================

        print("\nCCTV SAMPLE")
        print("-" * 40)

        cctv_records = (
            db.query(CCTVObservation)
            .limit(10)
            .all()
        )

        for record in cctv_records:

            print(
                f"{record.camera_id} | "
                f"{record.entity_id} | "
                f"{record.vehicle_id} | "
                f"{record.location_id} | "
                f"{record.confidence}"
            )

        # =====================================================
        # COURT
        # =====================================================

        print("\nCOURT SAMPLE")
        print("-" * 40)

        court_records = (
            db.query(CourtRecord)
            .limit(10)
            .all()
        )

        for record in court_records:

            print(
                f"{record.court_case_number} | "
                f"{record.court_name} | "
                f"{record.entity_id} | "
                f"{record.status}"
            )

        # =====================================================
        # FINANCIAL
        # =====================================================

        print("\nFINANCIAL SAMPLE")
        print("-" * 40)

        financial_records = (
            db.query(FinancialRecord)
            .limit(10)
            .all()
        )

        for record in financial_records:

            print(
                f"{record.transaction_id} | "
                f"{record.sender_entity_id} → "
                f"{record.receiver_entity_id} | "
                f"₹{record.amount}"
            )

        # =====================================================
        # FINAL
        # =====================================================

        print("\n")
        print("=" * 60)
        print("✅ DATABASE VERIFICATION COMPLETE")
        print("=" * 60)

    finally:

        db.close()


if __name__ == "__main__":

    test_database()