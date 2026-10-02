# database/models.py

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


# =========================================================
# DATA LAYERS
# =========================================================

class DataLayer(Base):

    __tablename__ = "data_layers"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    layer_code = Column(
        String,
        unique=True,
        nullable=False
    )

    layer_name = Column(
        String,
        nullable=False
    )

    description = Column(Text)


# =========================================================
# CASES
# =========================================================

class Case(Base):

    __tablename__ = "cases"

    id = Column(
        String,
        primary_key=True
    )

    fir_number = Column(
        String,
        unique=True,
        nullable=True
    )

    case_type = Column(String)

    police_station = Column(String)

    incident_date = Column(DateTime)

    registered_date = Column(DateTime)

    status = Column(
        String,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    relationships = relationship(
        "Relationship",
        back_populates="case"
    )

    events = relationship(
        "Event",
        back_populates="case"
    )

    evidence = relationship(
        "Evidence",
        back_populates="case"
    )


# =========================================================
# CANONICAL ENTITIES
# =========================================================

class Entity(Base):

    __tablename__ = "entities"

    id = Column(
        String,
        primary_key=True
    )

    entity_type = Column(
        String,
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    canonical_id = Column(
        String,
        unique=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    source_evidence = relationship(
        "EntityEvidence",
        back_populates="entity"
    )


# =========================================================
# EVIDENCE
# =========================================================

class Evidence(Base):

    __tablename__ = "evidence"

    id = Column(
        String,
        primary_key=True
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    layer_id = Column(
        Integer,
        ForeignKey("data_layers.id"),
        nullable=False
    )

    evidence_type = Column(
        String,
        nullable=False
    )

    source = Column(String)

    storage_path = Column(String)

    file_hash = Column(String)

    extracted_text = Column(Text)

    created_at = Column(DateTime)

    case = relationship(
        "Case",
        back_populates="evidence"
    )


# =========================================================
# GENERIC RELATIONSHIPS
# =========================================================

class Relationship(Base):

    __tablename__ = "relationships"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    source_entity_id = Column(
        String,
        ForeignKey("entities.id"),
        nullable=False
    )

    target_entity_id = Column(
        String,
        ForeignKey("entities.id"),
        nullable=False
    )

    relationship_type = Column(
        String,
        nullable=False
    )

    layer_id = Column(
        Integer,
        ForeignKey("data_layers.id"),
        nullable=False
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    timestamp = Column(DateTime)

    confidence = Column(
        Float,
        default=1.0
    )

    evidence_id = Column(
        String,
        ForeignKey("evidence.id")
    )

    created_at = Column(DateTime)

    case = relationship(
        "Case",
        back_populates="relationships"
    )


# =========================================================
# EVENTS
# =========================================================

class Event(Base):

    __tablename__ = "events"

    id = Column(
        String,
        primary_key=True
    )

    event_type = Column(
        String,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    location_id = Column(
        String,
        ForeignKey("entities.id")
    )

    description = Column(Text)

    evidence_id = Column(
        String,
        ForeignKey("evidence.id")
    )

    case = relationship(
        "Case",
        back_populates="events"
    )


# =========================================================
# ENTITY ↔ EVIDENCE
# =========================================================

class EntityEvidence(Base):

    __tablename__ = "entity_evidence"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    entity_id = Column(
        String,
        ForeignKey("entities.id"),
        nullable=False
    )

    evidence_id = Column(
        String,
        ForeignKey("evidence.id"),
        nullable=False
    )

    mention_type = Column(String)

    confidence = Column(
        Float,
        default=1.0
    )

    entity = relationship(
        "Entity",
        back_populates="source_evidence"
    )

    __table_args__ = (
        UniqueConstraint(
            "entity_id",
            "evidence_id",
            name="unique_entity_evidence"
        ),
    )


# =========================================================
# CDR RECORDS
# =========================================================

class CDRRecord(Base):

    __tablename__ = "cdr_records"

    id = Column(
        String,
        primary_key=True
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    evidence_id = Column(
        String,
        ForeignKey("evidence.id")
    )

    caller_entity_id = Column(
        String,
        ForeignKey("entities.id")
    )

    receiver_entity_id = Column(
        String,
        ForeignKey("entities.id")
    )

    caller_phone = Column(String)

    receiver_phone = Column(String)

    timestamp = Column(
        DateTime,
        nullable=False
    )

    duration_seconds = Column(Integer)

    cell_tower = Column(String)

    communication_type = Column(String)


# =========================================================
# CCTV OBSERVATIONS
# =========================================================

class CCTVObservation(Base):

    __tablename__ = "cctv_observations"

    id = Column(
        String,
        primary_key=True
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    evidence_id = Column(
        String,
        ForeignKey("evidence.id")
    )

    camera_id = Column(String)

    timestamp = Column(
        DateTime,
        nullable=False
    )

    entity_id = Column(
        String,
        ForeignKey("entities.id")
    )

    vehicle_id = Column(
        String,
        ForeignKey("entities.id")
    )

    location_id = Column(
        String,
        ForeignKey("entities.id")
    )

    event_type = Column(String)

    confidence = Column(Float)


# =========================================================
# COURT RECORDS
# =========================================================

class CourtRecord(Base):

    __tablename__ = "court_records"

    id = Column(
        String,
        primary_key=True
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    evidence_id = Column(
        String,
        ForeignKey("evidence.id")
    )

    court_case_number = Column(String)

    court_name = Column(String)

    hearing_date = Column(DateTime)

    entity_id = Column(
        String,
        ForeignKey("entities.id")
    )

    role = Column(String)

    status = Column(String)

    description = Column(Text)


# =========================================================
# FINANCIAL RECORDS
# =========================================================

class FinancialRecord(Base):

    __tablename__ = "financial_records"

    id = Column(
        String,
        primary_key=True
    )

    case_id = Column(
        String,
        ForeignKey("cases.id")
    )

    evidence_id = Column(
        String,
        ForeignKey("evidence.id")
    )

    sender_entity_id = Column(
        String,
        ForeignKey("entities.id")
    )

    receiver_entity_id = Column(
        String,
        ForeignKey("entities.id")
    )

    sender_account = Column(String)

    receiver_account = Column(String)

    transaction_id = Column(String)

    timestamp = Column(DateTime)

    amount = Column(Float)

    bank_name = Column(String)

    transaction_type = Column(String)

    description = Column(Text)