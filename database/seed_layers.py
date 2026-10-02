# database/seed_layers.py

from database.connection import SessionLocal
from database.models import DataLayer


LAYERS = [

    (
        "FIR",
        "FIR Records",
        "First Information Reports and police records"
    ),

    (
        "COURT",
        "Court Records",
        "Court cases, hearings, orders and judgments"
    ),

    (
        "CDR",
        "Call Detail Records",
        "Telephone communication records"
    ),

    (
        "VEHICLE",
        "Vehicle Records",
        "Vehicle registration, ownership and movement records"
    ),

    (
        "CCTV",
        "CCTV Records",
        "CCTV observations and detections"
    ),

    (
        "FINANCIAL",
        "Financial Records",
        "Bank accounts and financial transactions"
    ),

    (
        "LOCATION",
        "Location Records",
        "Locations, movements and geographic observations"
    ),

]


def seed_layers():

    db = SessionLocal()

    try:

        for code, name, description in LAYERS:

            existing = (
                db.query(DataLayer)
                .filter(
                    DataLayer.layer_code == code
                )
                .first()
            )

            if not existing:

                db.add(
                    DataLayer(
                        layer_code=code,
                        layer_name=name,
                        description=description
                    )
                )

        db.commit()

        print("✅ All 7 data layers inserted")

    finally:

        db.close()


if __name__ == "__main__":
    seed_layers()