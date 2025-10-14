from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    mobile = Column(String(15), nullable=False)
    address = Column(Text, nullable=True)
    referral = Column(String(100), nullable=True)
    history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    payments = relationship("Payment", back_populates="patient")
    visits = relationship("PatientVisit", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_name = Column(String(100), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False,
                    default="scheduled")  # scheduled/completed/cancelled

    # Relationships
    patient = relationship("Patient", back_populates="appointments")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_mode = Column(String(20), nullable=False)  # cash/upi/card
    notes = Column(Text, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="payments")


class PatientVisit(Base):
    __tablename__ = "patient_visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_date = Column(Date, nullable=False)
    visit_type = Column(String(20), nullable=False)  # new/follow-up
    doctor_name = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Prescription fields
    observation = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    medicines = Column(Text, nullable=True)
    next_visit_date = Column(Date, nullable=True)
    tests = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="visits")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
