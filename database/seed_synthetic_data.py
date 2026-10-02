# database/seed_synthetic_data.py

from datetime import datetime, timedelta

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


# =========================================================
# HELPERS
# =========================================================

def add_if_missing(db, model, object_id, obj):

    existing = db.get(
        model,
        object_id
    )

    if not existing:

        db.add(obj)

        return True

    return False


# =========================================================
# MAIN SEED FUNCTION
# =========================================================

def seed_synthetic_data():

    db = SessionLocal()

    try:

        print("\n======================================")
        print("CREATING SYNTHETIC INVESTIGATION DATA")
        print("======================================")

        # =====================================================
        # GET DATA LAYERS
        # =====================================================

        layers = {
            layer.layer_code: layer.id
            for layer in db.query(DataLayer).all()
        }

        required_layers = [
            "FIR",
            "COURT",
            "CDR",
            "VEHICLE",
            "CCTV",
            "FINANCIAL",
            "LOCATION",
        ]

        for layer in required_layers:

            if layer not in layers:

                raise RuntimeError(
                    f"Missing layer {layer}. "
                    "Run: python -m database.seed_layers"
                )

        # =====================================================
        # BASE DATE
        # =====================================================

        base_date = datetime(
            2025,
            1,
            10,
            10,
            0
        )

        # =====================================================
        # PEOPLE
        # =====================================================

        people = [

            ("person:Ravi", "Ravi"),
            ("person:Arun", "Arun"),
            ("person:Kumar", "Kumar"),
            ("person:Manu", "Manu"),
            ("person:Joseph", "Joseph"),
            ("person:Vijay", "Vijay"),
            ("person:Rahul", "Rahul"),
            ("person:Suresh", "Suresh"),
            ("person:Ajay", "Ajay"),
            ("person:Vikram", "Vikram"),
            ("person:Deepak", "Deepak"),
            ("person:Manoj", "Manoj"),
            ("person:Prakash", "Prakash"),
            ("person:Santhosh", "Santhosh"),
            ("person:Karthik", "Karthik"),
            ("person:Imran", "Imran"),
            ("person:Faizal", "Faizal"),
            ("person:Naveen", "Naveen"),
            ("person:Surya", "Surya"),
            ("person:Hari", "Hari"),
            ("person:Aravind", "Aravind"),
            ("person:Mahesh", "Mahesh"),
            ("person:Ganesh", "Ganesh"),
            ("person:Ramesh", "Ramesh"),
            ("person:Lokesh", "Lokesh"),
            ("person:Sameer", "Sameer"),
            ("person:Akash", "Akash"),
            ("person:Varun", "Varun"),
            ("person:Dinesh", "Dinesh"),
            ("person:Mohit", "Mohit"),
        ]

        for entity_id, name in people:

            add_if_missing(
                db,
                Entity,
                entity_id,
                Entity(
                    id=entity_id,
                    entity_type="PERSON",
                    name=name,
                    canonical_id=entity_id.lower(),
                    created_at=base_date
                )
            )

        # =====================================================
        # PHONES
        # =====================================================

        phones = [

            ("phone:9876500001", "9876500001"),
            ("phone:9876500002", "9876500002"),
            ("phone:9876500003", "9876500003"),
            ("phone:9876500004", "9876500004"),
            ("phone:9876500005", "9876500005"),
            ("phone:9876500006", "9876500006"),
            ("phone:9876500007", "9876500007"),
            ("phone:9876500008", "9876500008"),
            ("phone:9876500009", "9876500009"),
            ("phone:9876500010", "9876500010"),
            ("phone:9876500011", "9876500011"),
            ("phone:9876500012", "9876500012"),
            ("phone:9876500013", "9876500013"),
            ("phone:9876500014", "9876500014"),
            ("phone:9876500015", "9876500015"),
        ]

        for entity_id, number in phones:

            add_if_missing(
                db,
                Entity,
                entity_id,
                Entity(
                    id=entity_id,
                    entity_type="PHONE",
                    name=number,
                    canonical_id=entity_id.lower(),
                    created_at=base_date
                )
            )

        # =====================================================
        # VEHICLES
        # =====================================================

        vehicles = [

            ("vehicle:DL01AB1001", "DL01AB1001"),
            ("vehicle:DL01AB1002", "DL01AB1002"),
            ("vehicle:DL01AB1003", "DL01AB1003"),
            ("vehicle:DL01AB1004", "DL01AB1004"),
            ("vehicle:DL01AB1005", "DL01AB1005"),
            ("vehicle:DL01AB1006", "DL01AB1006"),
            ("vehicle:DL01AB1007", "DL01AB1007"),
            ("vehicle:DL01AB1008", "DL01AB1008"),
            ("vehicle:DL01AB1009", "DL01AB1009"),
            ("vehicle:DL01AB1010", "DL01AB1010"),
        ]

        for entity_id, registration in vehicles:

            add_if_missing(
                db,
                Entity,
                entity_id,
                Entity(
                    id=entity_id,
                    entity_type="VEHICLE",
                    name=registration,
                    canonical_id=entity_id.lower(),
                    created_at=base_date
                )
            )

        # =====================================================
        # LOCATIONS
        # =====================================================

        locations = [

            ("location:Connaught Place", "Connaught Place"),
            ("location:Rajiv Chowk", "Rajiv Chowk"),
            ("location:Green Park", "Green Park"),
            ("location:Saket", "Saket"),
            ("location:Lajpat Nagar", "Lajpat Nagar"),
            ("location:Karol Bagh", "Karol Bagh"),
            ("location:Chandni Chowk", "Chandni Chowk"),
            ("location:Noida Sector 18", "Noida Sector 18"),
            ("location:Dwarka", "Dwarka"),
            ("location:Rohini", "Rohini"),
            ("location:Vasant Kunj", "Vasant Kunj"),
            ("location:Shahdara", "Shahdara"),
            ("location:Mayur Vihar", "Mayur Vihar"),
            ("location:Pitampura", "Pitampura"),
            ("location:New Delhi Railway Station", "New Delhi Railway Station"),
        ]

        for entity_id, location_name in locations:

            add_if_missing(
                db,
                Entity,
                entity_id,
                Entity(
                    id=entity_id,
                    entity_type="LOCATION",
                    name=location_name,
                    canonical_id=entity_id.lower(),
                    created_at=base_date
                )
            )

        # =====================================================
        # BANK ACCOUNTS
        # =====================================================

        accounts = [

            ("account:100001", "ACC-100001"),
            ("account:100002", "ACC-100002"),
            ("account:100003", "ACC-100003"),
            ("account:100004", "ACC-100004"),
            ("account:100005", "ACC-100005"),
            ("account:100006", "ACC-100006"),
            ("account:100007", "ACC-100007"),
            ("account:100008", "ACC-100008"),
            ("account:100009", "ACC-100009"),
            ("account:100010", "ACC-100010"),
        ]

        for entity_id, account_name in accounts:

            add_if_missing(
                db,
                Entity,
                entity_id,
                Entity(
                    id=entity_id,
                    entity_type="BANK_ACCOUNT",
                    name=account_name,
                    canonical_id=entity_id.lower(),
                    created_at=base_date
                )
            )

        # =====================================================
        # ORGANIZATIONS
        # =====================================================

        organizations = [

            (
                "organization:Delhi Police",
                "Delhi Police"
            ),

            (
                "organization:Connaught Place Police Station",
                "Connaught Place Police Station"
            ),

            (
                "organization:Saket Police Station",
                "Saket Police Station"
            ),

            (
                "organization:District Court Delhi",
                "District Court Delhi"
            ),

        ]

        for entity_id, name in organizations:

            add_if_missing(
                db,
                Entity,
                entity_id,
                Entity(
                    id=entity_id,
                    entity_type="ORGANIZATION",
                    name=name,
                    canonical_id=entity_id.lower(),
                    created_at=base_date
                )
            )

        db.flush()

        # =====================================================
        # 10 CASES
        # =====================================================

        case_definitions = [

            (
                "case:FIR-101-2025",
                "101/2025",
                "Connaught Place Police Station",
                0,
            ),

            (
                "case:FIR-102-2025",
                "102/2025",
                "Saket Police Station",
                8,
            ),

            (
                "case:FIR-103-2025",
                "103/2025",
                "Green Park Police Station",
                16,
            ),

            (
                "case:FIR-104-2025",
                "104/2025",
                "Lajpat Nagar Police Station",
                24,
            ),

            (
                "case:FIR-105-2025",
                "105/2025",
                "Karol Bagh Police Station",
                32,
            ),

            (
                "case:FIR-106-2025",
                "106/2025",
                "Chandni Chowk Police Station",
                40,
            ),

            (
                "case:FIR-107-2025",
                "107/2025",
                "Dwarka Police Station",
                48,
            ),

            (
                "case:FIR-108-2025",
                "108/2025",
                "Rohini Police Station",
                56,
            ),

            (
                "case:FIR-109-2025",
                "109/2025",
                "Vasant Kunj Police Station",
                64,
            ),

            (
                "case:FIR-110-2025",
                "110/2025",
                "Shahdara Police Station",
                72,
            ),
        ]

        cases = []

        for (
            case_id,
            fir_number,
            police_station,
            offset
        ) in case_definitions:

            incident_date = (
                base_date +
                timedelta(days=offset)
            )

            case = Case(
                id=case_id,
                fir_number=fir_number,
                case_type="FIR",
                police_station=police_station,
                incident_date=incident_date,
                registered_date=incident_date + timedelta(hours=2),
                status="ACTIVE",
                created_at=base_date
            )

            add_if_missing(
                db,
                Case,
                case_id,
                case
            )

            cases.append(
                (
                    case_id,
                    incident_date
                )
            )

        db.flush()

        # =====================================================
        # COURT CASES
        # =====================================================

        court_cases = []

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases, start=1):

            court_case_id = (
                f"case:COURT-{450 + index}-2025"
            )

            court_cases.append(
                (
                    court_case_id,
                    case_id,
                    incident_date
                )
            )

            add_if_missing(
                db,
                Case,
                court_case_id,
                Case(
                    id=court_case_id,
                    fir_number=None,
                    case_type="COURT",
                    police_station=None,
                    incident_date=incident_date,
                    registered_date=incident_date + timedelta(days=15),
                    status="ONGOING",
                    created_at=base_date
                )
            )

        db.flush()

        # =====================================================
        # PERSON ↔ PHONE MAPPING
        # =====================================================

        person_phone_map = {

            "person:Ravi":
                "phone:9876500001",

            "person:Arun":
                "phone:9876500002",

            "person:Kumar":
                "phone:9876500003",

            "person:Manu":
                "phone:9876500004",

            "person:Joseph":
                "phone:9876500005",

            "person:Vijay":
                "phone:9876500006",

            "person:Rahul":
                "phone:9876500007",

            "person:Suresh":
                "phone:9876500008",

            "person:Ajay":
                "phone:9876500009",

            "person:Vikram":
                "phone:9876500010",

            "person:Deepak":
                "phone:9876500011",

            "person:Manoj":
                "phone:9876500012",

            "person:Prakash":
                "phone:9876500013",

            "person:Santhosh":
                "phone:9876500014",

            "person:Karthik":
                "phone:9876500015",
        }

        # =====================================================
        # PERSON ↔ BANK ACCOUNT
        # =====================================================

        person_account_map = {

            "person:Ravi":
                "account:100001",

            "person:Kumar":
                "account:100002",

            "person:Joseph":
                "account:100003",

            "person:Rahul":
                "account:100004",

            "person:Suresh":
                "account:100005",

            "person:Ajay":
                "account:100006",

            "person:Vikram":
                "account:100007",

            "person:Deepak":
                "account:100008",

            "person:Manoj":
                "account:100009",

            "person:Prakash":
                "account:100010",
        }

        # =====================================================
        # PERSON ↔ VEHICLE
        # =====================================================

        person_vehicle_map = {

            "person:Ravi":
                "vehicle:DL01AB1001",

            "person:Kumar":
                "vehicle:DL01AB1002",

            "person:Joseph":
                "vehicle:DL01AB1003",

            "person:Rahul":
                "vehicle:DL01AB1004",

            "person:Suresh":
                "vehicle:DL01AB1005",

            "person:Ajay":
                "vehicle:DL01AB1006",

            "person:Vikram":
                "vehicle:DL01AB1007",

            "person:Deepak":
                "vehicle:DL01AB1008",

            "person:Manoj":
                "vehicle:DL01AB1009",

            "person:Prakash":
                "vehicle:DL01AB1010",
        }

        # =====================================================
        # CASE → PEOPLE
        #
        # Several people intentionally overlap between cases.
        # This creates the cross-case network.
        # =====================================================

        case_people = {

            "case:FIR-101-2025":
                ["person:Ravi", "person:Kumar", "person:Joseph"],

            "case:FIR-102-2025":
                ["person:Ravi", "person:Rahul", "person:Suresh"],

            "case:FIR-103-2025":
                ["person:Kumar", "person:Ajay", "person:Vikram"],

            "case:FIR-104-2025":
                ["person:Joseph", "person:Rahul", "person:Deepak"],

            "case:FIR-105-2025":
                ["person:Ravi", "person:Ajay", "person:Manoj"],

            "case:FIR-106-2025":
                ["person:Kumar", "person:Suresh", "person:Prakash"],

            "case:FIR-107-2025":
                ["person:Joseph", "person:Vikram", "person:Karthik"],

            "case:FIR-108-2025":
                ["person:Ravi", "person:Deepak", "person:Santhosh"],

            "case:FIR-109-2025":
                ["person:Rahul", "person:Manoj", "person:Karthik"],

            "case:FIR-110-2025":
                ["person:Ajay", "person:Prakash", "person:Santhosh"],
        }

        # =====================================================
        # CASE → LOCATION
        # =====================================================

        case_locations = {

            "case:FIR-101-2025":
                "location:Connaught Place",

            "case:FIR-102-2025":
                "location:Saket",

            "case:FIR-103-2025":
                "location:Green Park",

            "case:FIR-104-2025":
                "location:Lajpat Nagar",

            "case:FIR-105-2025":
                "location:Karol Bagh",

            "case:FIR-106-2025":
                "location:Chandni Chowk",

            "case:FIR-107-2025":
                "location:Dwarka",

            "case:FIR-108-2025":
                "location:Rohini",

            "case:FIR-109-2025":
                "location:Vasant Kunj",

            "case:FIR-110-2025":
                "location:Shahdara",
        }

        # =====================================================
        # EVIDENCE FOR EVERY CASE / LAYER
        # =====================================================

        evidence_by_case = {}

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases, start=1):

            evidence_by_case[case_id] = {}

            evidence_types = [

                (
                    "FIR",
                    "FIR_DOCUMENT",
                    f"minio://evidence/fir/{index:03d}.pdf"
                ),

                (
                    "COURT",
                    "COURT_DOCUMENT",
                    f"minio://evidence/court/{index:03d}.pdf"
                ),

                (
                    "CDR",
                    "CDR_FILE",
                    f"minio://evidence/cdr/{index:03d}.csv"
                ),

                (
                    "VEHICLE",
                    "VEHICLE_RECORD",
                    f"minio://evidence/vehicle/{index:03d}.json"
                ),

                (
                    "CCTV",
                    "CCTV_VIDEO",
                    f"minio://evidence/cctv/{index:03d}.mp4"
                ),

                (
                    "FINANCIAL",
                    "BANK_TRANSACTION_FILE",
                    f"minio://evidence/financial/{index:03d}.csv"
                ),

                (
                    "LOCATION",
                    "LOCATION_RECORD",
                    f"minio://evidence/location/{index:03d}.json"
                ),

            ]

            for (
                layer_code,
                evidence_type,
                storage_path
            ) in evidence_types:

                evidence_id = (
                    f"evidence:{layer_code}-"
                    f"{index:03d}-2025"
                )

                evidence_by_case[
                    case_id
                ][layer_code] = evidence_id

                add_if_missing(
                    db,
                    Evidence,
                    evidence_id,
                    Evidence(
                        id=evidence_id,
                        case_id=case_id,
                        layer_id=layers[layer_code],
                        evidence_type=evidence_type,
                        source=f"Synthetic {layer_code} Source",
                        storage_path=storage_path,
                        file_hash=f"synthetic_hash_{layer_code}_{index}",
                        extracted_text=(
                            f"Synthetic {layer_code} "
                            f"evidence for {case_id}"
                        ),
                        created_at=incident_date
                    )
                )

        db.flush()

        # =====================================================
        # GENERIC RELATIONSHIPS
        # =====================================================

        relationship_counter = 1

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases):

            people_in_case = case_people[case_id]

            location_id = case_locations[case_id]

            fir_evidence = evidence_by_case[
                case_id
            ]["FIR"]

            cdr_evidence = evidence_by_case[
                case_id
            ]["CDR"]

            vehicle_evidence = evidence_by_case[
                case_id
            ]["VEHICLE"]

            financial_evidence = evidence_by_case[
                case_id
            ]["FINANCIAL"]

            location_evidence = evidence_by_case[
                case_id
            ]["LOCATION"]

            # ---------------------------------------------
            # FIR: PERSON → CASE
            # ---------------------------------------------

            for person_id in people_in_case:

                db.add(
                    Relationship(
                        source_entity_id=person_id,
                        target_entity_id=location_id,
                        relationship_type="PRESENT_AT",
                        layer_id=layers["LOCATION"],
                        case_id=case_id,
                        timestamp=incident_date,
                        confidence=0.90,
                        evidence_id=location_evidence,
                        created_at=datetime.now()
                    )
                )

                relationship_counter += 1

            # ---------------------------------------------
            # PERSON → PHONE
            # ---------------------------------------------

            for person_id in people_in_case:

                phone_id = person_phone_map.get(
                    person_id
                )

                if phone_id:

                    db.add(
                        Relationship(
                            source_entity_id=person_id,
                            target_entity_id=phone_id,
                            relationship_type="USES_PHONE",
                            layer_id=layers["CDR"],
                            case_id=case_id,
                            timestamp=incident_date,
                            confidence=0.98,
                            evidence_id=cdr_evidence,
                            created_at=datetime.now()
                        )
                    )

            # ---------------------------------------------
            # PERSON → VEHICLE
            # ---------------------------------------------

            for person_id in people_in_case:

                vehicle_id = person_vehicle_map.get(
                    person_id
                )

                if vehicle_id:

                    db.add(
                        Relationship(
                            source_entity_id=person_id,
                            target_entity_id=vehicle_id,
                            relationship_type="ASSOCIATED_WITH_VEHICLE",
                            layer_id=layers["VEHICLE"],
                            case_id=case_id,
                            timestamp=incident_date,
                            confidence=0.92,
                            evidence_id=vehicle_evidence,
                            created_at=datetime.now()
                        )
                    )

            # ---------------------------------------------
            # PERSON → PERSON
            # ---------------------------------------------

            if len(people_in_case) >= 3:

                for i in range(
                    len(people_in_case) - 1
                ):

                    source = people_in_case[i]

                    target = people_in_case[i + 1]

                    db.add(
                        Relationship(
                            source_entity_id=source,
                            target_entity_id=target,
                            relationship_type="ASSOCIATED_WITH",
                            layer_id=layers["FIR"],
                            case_id=case_id,
                            timestamp=incident_date,
                            confidence=0.85,
                            evidence_id=fir_evidence,
                            created_at=datetime.now()
                        )
                    )

            # ---------------------------------------------
            # PERSON → BANK ACCOUNT
            # ---------------------------------------------

            for person_id in people_in_case:

                account_id = person_account_map.get(
                    person_id
                )

                if account_id:

                    db.add(
                        Relationship(
                            source_entity_id=person_id,
                            target_entity_id=account_id,
                            relationship_type="OWNS_ACCOUNT",
                            layer_id=layers["FINANCIAL"],
                            case_id=case_id,
                            timestamp=incident_date,
                            confidence=0.97,
                            evidence_id=financial_evidence,
                            created_at=datetime.now()
                        )
                    )

        # =====================================================
        # CDR RECORDS
        # =====================================================

        cdr_counter = 1

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases):

            people_in_case = case_people[case_id]

            if len(people_in_case) < 2:

                continue

            for call_index in range(2):

                caller = people_in_case[
                    call_index %
                    len(people_in_case)
                ]

                receiver = people_in_case[
                    (call_index + 1) %
                    len(people_in_case)
                ]

                caller_phone = person_phone_map.get(
                    caller
                )

                receiver_phone = person_phone_map.get(
                    receiver
                )

                cdr_id = (
                    f"cdr:{index + 1:03d}:"
                    f"{call_index + 1:03d}"
                )

                timestamp = (
                    incident_date +
                    timedelta(
                        minutes=20 +
                        call_index * 15
                    )
                )

                db.add(
                    CDRRecord(
                        id=cdr_id,
                        case_id=case_id,
                        evidence_id=evidence_by_case[
                            case_id
                        ]["CDR"],
                        caller_entity_id=caller,
                        receiver_entity_id=receiver,
                        caller_phone=caller_phone.replace(
                            "phone:",
                            ""
                        ) if caller_phone else None,
                        receiver_phone=receiver_phone.replace(
                            "phone:",
                            ""
                        ) if receiver_phone else None,
                        timestamp=timestamp,
                        duration_seconds=(
                            120 +
                            call_index * 90
                        ),
                        cell_tower=(
                            f"TOWER-{index + 1:03d}"
                        ),
                        communication_type="VOICE"
                    )
                )

                cdr_counter += 1

        # =====================================================
        # CCTV OBSERVATIONS
        # =====================================================

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases):

            people_in_case = case_people[case_id]

            location_id = case_locations[case_id]

            vehicle_id = person_vehicle_map.get(
                people_in_case[0]
            )

            for obs_index, person_id in enumerate(
                people_in_case[:2],
                start=1
            ):

                cctv_id = (
                    f"cctv:{index + 1:03d}:"
                    f"{obs_index:03d}"
                )

                db.add(
                    CCTVObservation(
                        id=cctv_id,
                        case_id=case_id,
                        evidence_id=evidence_by_case[
                            case_id
                        ]["CCTV"],
                        camera_id=(
                            f"CAM-{index + 1:03d}"
                        ),
                        timestamp=(
                            incident_date +
                            timedelta(
                                minutes=35 +
                                obs_index
                            )
                        ),
                        entity_id=person_id,
                        vehicle_id=vehicle_id,
                        location_id=location_id,
                        event_type="PERSON_DETECTED",
                        confidence=(
                            0.80 +
                            obs_index * 0.05
                        )
                    )
                )

        # =====================================================
        # FINANCIAL TRANSACTIONS
        # =====================================================

        transaction_counter = 1

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases):

            people_in_case = case_people[case_id]

            if len(people_in_case) < 2:

                continue

            sender = people_in_case[0]

            receiver = people_in_case[1]

            sender_account = person_account_map.get(
                sender
            )

            receiver_account = person_account_map.get(
                receiver
            )

            if not sender_account or not receiver_account:

                continue

            db.add(
                FinancialRecord(
                    id=(
                        f"financial:"
                        f"{index + 1:03d}"
                    ),
                    case_id=case_id,
                    evidence_id=evidence_by_case[
                        case_id
                    ]["FINANCIAL"],
                    sender_entity_id=sender,
                    receiver_entity_id=receiver,
                    sender_account=(
                        sender_account.replace(
                            "account:",
                            ""
                        )
                    ),
                    receiver_account=(
                        receiver_account.replace(
                            "account:",
                            ""
                        )
                    ),
                    transaction_id=(
                        f"TXN2025"
                        f"{index + 1:04d}"
                    ),
                    timestamp=(
                        incident_date +
                        timedelta(
                            hours=1
                        )
                    ),
                    amount=(
                        5000.0 +
                        index * 1750.0
                    ),
                    bank_name="Synthetic National Bank",
                    transaction_type="TRANSFER",
                    description=(
                        "Synthetic financial "
                        "transaction for analysis."
                    )
                )
            )

            transaction_counter += 1

        # =====================================================
        # COURT RECORDS
        # =====================================================

        for index, (
            court_case_id,
            fir_case_id,
            incident_date
        ) in enumerate(
            court_cases,
            start=1
        ):

            people_in_case = case_people[
                fir_case_id
            ]

            for person_id in people_in_case:

                db.add(
                    CourtRecord(
                        id=(
                            f"court-record:"
                            f"{index:03d}:"
                            f"{person_id.split(':')[-1]}"
                        ),
                        case_id=court_case_id,
                        evidence_id=evidence_by_case[
                            fir_case_id
                        ]["COURT"],
                        court_case_number=(
                            f"CC/{450 + index}/2025"
                        ),
                        court_name="District Court Delhi",
                        hearing_date=(
                            incident_date +
                            timedelta(
                                days=30
                            )
                        ),
                        entity_id=person_id,
                        role="PARTY",
                        status="ONGOING",
                        description=(
                            "Synthetic court record "
                            "linked to FIR case."
                        )
                    )
                )

        # =====================================================
        # ENTITY ↔ EVIDENCE LINKS
        # =====================================================

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases):

            people_in_case = case_people[case_id]

            links = []

            # FIR entities
            for person_id in people_in_case:

                links.append(
                    (
                        person_id,
                        evidence_by_case[
                            case_id
                        ]["FIR"],
                        "NAMED_PERSON",
                        0.98
                    )
                )

            # Location
            links.append(
                (
                    case_locations[case_id],
                    evidence_by_case[
                        case_id
                    ]["LOCATION"],
                    "INCIDENT_LOCATION",
                    0.97
                )
            )

            # Phones
            for person_id in people_in_case:

                phone_id = person_phone_map.get(
                    person_id
                )

                if phone_id:

                    links.append(
                        (
                            phone_id,
                            evidence_by_case[
                                case_id
                            ]["CDR"],
                            "PHONE_REFERENCE",
                            0.99
                        )
                    )

            # Vehicles
            for person_id in people_in_case:

                vehicle_id = person_vehicle_map.get(
                    person_id
                )

                if vehicle_id:

                    links.append(
                        (
                            vehicle_id,
                            evidence_by_case[
                                case_id
                            ]["VEHICLE"],
                            "VEHICLE_REFERENCE",
                            0.99
                        )
                    )

            # Insert links
            for (
                entity_id,
                evidence_id,
                mention_type,
                confidence
            ) in links:

                existing = (
                    db.query(EntityEvidence)
                    .filter(
                        EntityEvidence.entity_id ==
                        entity_id,
                        EntityEvidence.evidence_id ==
                        evidence_id
                    )
                    .first()
                )

                if not existing:

                    db.add(
                        EntityEvidence(
                            entity_id=entity_id,
                            evidence_id=evidence_id,
                            mention_type=mention_type,
                            confidence=confidence
                        )
                    )

        # =====================================================
        # TEMPORAL EVENTS
        # =====================================================

        for index, (
            case_id,
            incident_date
        ) in enumerate(cases, start=1):

            location_id = case_locations[
                case_id
            ]

            db.add(
                Event(
                    id=(
                        f"event:{index:03d}:incident"
                    ),
                    event_type="INCIDENT",
                    timestamp=incident_date,
                    case_id=case_id,
                    location_id=location_id,
                    description=(
                        f"Synthetic incident for "
                        f"{case_id}"
                    ),
                    evidence_id=evidence_by_case[
                        case_id
                    ]["FIR"]
                )
            )

            db.add(
                Event(
                    id=(
                        f"event:{index:03d}:cctv"
                    ),
                    event_type="CCTV_DETECTION",
                    timestamp=(
                        incident_date +
                        timedelta(
                            minutes=35
                        )
                    ),
                    case_id=case_id,
                    location_id=location_id,
                    description=(
                        "Synthetic CCTV "
                        "observation."
                    ),
                    evidence_id=evidence_by_case[
                        case_id
                    ]["CCTV"]
                )
            )

            db.add(
                Event(
                    id=(
                        f"event:{index:03d}:cdr"
                    ),
                    event_type="CDR_ACTIVITY",
                    timestamp=(
                        incident_date +
                        timedelta(
                            minutes=20
                        )
                    ),
                    case_id=case_id,
                    location_id=location_id,
                    description=(
                        "Synthetic communication "
                        "activity."
                    ),
                    evidence_id=evidence_by_case[
                        case_id
                    ]["CDR"]
                )
            )

            db.add(
                Event(
                    id=(
                        f"event:{index:03d}:financial"
                    ),
                    event_type="FINANCIAL_TRANSACTION",
                    timestamp=(
                        incident_date +
                        timedelta(
                            hours=1
                        )
                    ),
                    case_id=case_id,
                    location_id=location_id,
                    description=(
                        "Synthetic financial "
                        "transaction."
                    ),
                    evidence_id=evidence_by_case[
                        case_id
                    ]["FINANCIAL"]
                )
            )

        # =====================================================
        # CROSS-CASE CONNECTIONS
        #
        # These are intentional.
        # They allow the graph engine to discover
        # people appearing across multiple cases.
        # =====================================================

        cross_case_connections = [

            (
                "person:Ravi",
                "person:Kumar",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Ravi",
                "person:Rahul",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Kumar",
                "person:Ajay",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Joseph",
                "person:Rahul",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Ravi",
                "person:Ajay",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Kumar",
                "person:Suresh",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Joseph",
                "person:Vikram",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Ravi",
                "person:Deepak",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Rahul",
                "person:Manoj",
                "CROSS_CASE_ASSOCIATION"
            ),

            (
                "person:Ajay",
                "person:Prakash",
                "CROSS_CASE_ASSOCIATION"
            ),

        ]

        for source, target, relation_type in (
            cross_case_connections
        ):

            db.add(
                Relationship(
                    source_entity_id=source,
                    target_entity_id=target,
                    relationship_type=relation_type,
                    layer_id=layers["FIR"],
                    case_id=None,
                    timestamp=base_date,
                    confidence=0.75,
                    evidence_id=None,
                    created_at=datetime.now()
                )
            )

        # =====================================================
        # COMMIT EVERYTHING
        # =====================================================

        db.commit()

        print("\n======================================")
        print("✅ SYNTHETIC DATA INSERTED")
        print("======================================")

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

    except Exception as e:

        db.rollback()

        print("\n❌ Synthetic data insertion failed")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":

    seed_synthetic_data()