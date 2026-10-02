from database.connection import SessionLocal
from database.models import FinancialRecord
from database.neo4j_connection import driver


def normalize_entity_id(value):
    """
    PostgreSQL:
        person:Ravi

    Neo4j:
        person:ravi
    """
    if not value:
        return None

    return value.strip().lower()


def sync_financial_to_neo4j():

    db = SessionLocal()

    try:

        records = db.query(FinancialRecord).all()

        print(
            f"✅ Financial records found: {len(records)}"
        )

        synced = 0
        skipped = 0

        with driver.session() as session:

            for record in records:

                # ---------------------------------------------
                # Normalize entity IDs
                # ---------------------------------------------

                sender_id = normalize_entity_id(
                    record.sender_entity_id
                )

                receiver_id = normalize_entity_id(
                    record.receiver_entity_id
                )

                # Case/Evidence IDs preserve original case
                case_id = (
                    record.case_id.strip()
                    if record.case_id
                    else None
                )

                evidence_id = (
                    record.evidence_id.strip()
                    if record.evidence_id
                    else None
                )

                # ---------------------------------------------
                # Account canonical IDs
                # ---------------------------------------------

                sender_account_id = (
                    f"account:{record.sender_account}"
                    if record.sender_account
                    else None
                )

                receiver_account_id = (
                    f"account:{record.receiver_account}"
                    if record.receiver_account
                    else None
                )

                # ---------------------------------------------
                # Check required nodes
                # ---------------------------------------------

                check_query = """

                MATCH (sender:Person {
                    canonical_id: $sender_id
                })

                MATCH (receiver:Person {
                    canonical_id: $receiver_id
                })

                MATCH (sender_account:Account {
                    canonical_id: $sender_account_id
                })

                MATCH (receiver_account:Account {
                    canonical_id: $receiver_account_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                RETURN sender,
                       receiver,
                       sender_account,
                       receiver_account,
                       case_node,
                       evidence

                """

                result = session.run(
                    check_query,

                    sender_id=sender_id,

                    receiver_id=receiver_id,

                    sender_account_id=sender_account_id,

                    receiver_account_id=receiver_account_id,

                    case_id=case_id,

                    evidence_id=evidence_id
                )

                existing = result.single()

                if not existing:

                    print(
                        f"⚠️ Skipping financial record: "
                        f"{record.id}"
                    )

                    print(
                        f"   Sender         : {sender_id}"
                    )

                    print(
                        f"   Receiver       : {receiver_id}"
                    )

                    print(
                        f"   Sender Account : "
                        f"{sender_account_id}"
                    )

                    print(
                        f"   Receiver Account: "
                        f"{receiver_account_id}"
                    )

                    print(
                        f"   Case           : {case_id}"
                    )

                    print(
                        f"   Evidence       : {evidence_id}"
                    )

                    skipped += 1

                    continue

                # ---------------------------------------------
                # Create financial graph relationships
                # ---------------------------------------------

                sync_query = """

                MATCH (sender:Person {
                    canonical_id: $sender_id
                })

                MATCH (receiver:Person {
                    canonical_id: $receiver_id
                })

                MATCH (sender_account:Account {
                    canonical_id: $sender_account_id
                })

                MATCH (receiver_account:Account {
                    canonical_id: $receiver_account_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                // -----------------------------------------
                // Person → Person transaction
                // -----------------------------------------

                MERGE (
                    sender
                )-[r:RELATED {
                    relationship_id: $record_id
                }]->(
                    receiver
                )

                SET
                    r.relationship_type =
                        "FINANCIAL_TRANSFER",

                    r.source_layer = "FINANCIAL",

                    r.transaction_id =
                        $transaction_id,

                    r.amount =
                        $amount,

                    r.bank_name =
                        $bank_name,

                    r.transaction_type =
                        $transaction_type,

                    r.timestamp =
                        $timestamp,

                    r.case_id =
                        $case_id,

                    r.evidence_id =
                        $evidence_id

                // -----------------------------------------
                // Sender → Account
                // -----------------------------------------

                MERGE (
                    sender
                )-[sa:RELATED {
                    relationship_id:
                        $record_id + ":SENDER_ACCOUNT"
                }]->(
                    sender_account
                )

                SET
                    sa.relationship_type =
                        "SENT_FROM_ACCOUNT",

                    sa.source_layer =
                        "FINANCIAL",

                    sa.transaction_id =
                        $transaction_id,

                    sa.timestamp =
                        $timestamp,

                    sa.case_id =
                        $case_id,

                    sa.evidence_id =
                        $evidence_id

                // -----------------------------------------
                // Receiver → Account
                // -----------------------------------------

                MERGE (
                    receiver
                )-[ra:RELATED {
                    relationship_id:
                        $record_id + ":RECEIVER_ACCOUNT"
                }]->(
                    receiver_account
                )

                SET
                    ra.relationship_type =
                        "RECEIVED_IN_ACCOUNT",

                    ra.source_layer =
                        "FINANCIAL",

                    ra.transaction_id =
                        $transaction_id,

                    ra.timestamp =
                        $timestamp,

                    ra.case_id =
                        $case_id,

                    ra.evidence_id =
                        $evidence_id

                // -----------------------------------------
                // Sender Account → Receiver Account
                // -----------------------------------------

                MERGE (
                    sender_account
                )-[tr:RELATED {
                    relationship_id:
                        $record_id + ":ACCOUNT_TRANSFER"
                }]->(
                    receiver_account
                )

                SET
                    tr.relationship_type =
                        "ACCOUNT_TRANSFER",

                    tr.source_layer =
                        "FINANCIAL",

                    tr.transaction_id =
                        $transaction_id,

                    tr.amount =
                        $amount,

                    tr.bank_name =
                        $bank_name,

                    tr.transaction_type =
                        $transaction_type,

                    tr.timestamp =
                        $timestamp,

                    tr.case_id =
                        $case_id,

                    tr.evidence_id =
                        $evidence_id

                // -----------------------------------------
                // Sender → Evidence
                // -----------------------------------------

                MERGE (
                    sender
                )-[se:FINANCIAL_RECORDED_IN {
                    record_id: $record_id
                }]->(
                    evidence
                )

                SET
                    se.transaction_id =
                        $transaction_id,

                    se.amount =
                        $amount,

                    se.timestamp =
                        $timestamp

                // -----------------------------------------
                // Receiver → Evidence
                // -----------------------------------------

                MERGE (
                    receiver
                )-[re:FINANCIAL_RECORDED_IN {
                    record_id: $record_id
                }]->(
                    evidence
                )

                SET
                    re.transaction_id =
                        $transaction_id,

                    re.amount =
                        $amount,

                    re.timestamp =
                        $timestamp

                // -----------------------------------------
                // Evidence → Case
                // -----------------------------------------

                MERGE (
                    evidence
                )-[:BELONGS_TO]->(
                    case_node
                )

                RETURN sender,
                       receiver,
                       sender_account,
                       receiver_account,
                       evidence,
                       case_node

                """

                session.run(
                    sync_query,

                    sender_id=sender_id,

                    receiver_id=receiver_id,

                    sender_account_id=sender_account_id,

                    receiver_account_id=receiver_account_id,

                    case_id=case_id,

                    evidence_id=evidence_id,

                    record_id=record.id,

                    transaction_id=record.transaction_id,

                    amount=record.amount,

                    bank_name=record.bank_name,

                    transaction_type=record.transaction_type,

                    timestamp=record.timestamp
                )

                synced += 1

        print()
        print("================================")
        print(" FINANCIAL → Neo4j Sync Complete")
        print("================================")

        print(
            f"✅ Financial records synced : {synced}"
        )

        print(
            f"⚠️ Financial records skipped: {skipped}"
        )

        print(
            f"📊 Total records           : "
            f"{len(records)}"
        )

    except Exception as e:

        print()
        print("❌ Financial sync failed")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":

    try:
        sync_financial_to_neo4j()

    finally:
        driver.close()