from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta, date
from typing import List, Optional
import pandas as pd
import database, schemas

# Patient CRUD operations
def get_patient(db: Session, patient_id: int):
    return db.query(database.Patient).filter(database.Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    query = db.query(database.Patient)
    if search:
        query = query.filter(database.Patient.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = database.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
    if db_patient:
        for key, value in patient.dict().items():
            setattr(db_patient, key, value)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
    if not db_patient:
        return None
    
    # Check for dependent records
    appointment_count = db.query(database.Appointment).filter(database.Appointment.patient_id == patient_id).count()
    payment_count = db.query(database.Payment).filter(database.Payment.patient_id == patient_id).count()
    visit_count = db.query(database.PatientVisit).filter(database.PatientVisit.patient_id == patient_id).count()
    
    if appointment_count > 0 or payment_count > 0 or visit_count > 0:
        raise ValueError(f"Cannot delete patient: {appointment_count} appointments, {payment_count} payments, and {visit_count} visits exist")
    
    db.delete(db_patient)
    db.commit()
    return db_patient

# Appointment CRUD operations
def get_appointment(db: Session, appointment_id: int):
    return db.query(database.Appointment).filter(database.Appointment.id == appointment_id).first()

def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Appointment).offset(skip).limit(limit).all()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    # Verify patient exists
    patient = db.query(database.Patient).filter(database.Patient.id == appointment.patient_id).first()
    if not patient:
        raise ValueError(f"Patient with id {appointment.patient_id} not found")
    
    db_appointment = database.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment: schemas.AppointmentUpdate):
    db_appointment = db.query(database.Appointment).filter(database.Appointment.id == appointment_id).first()
    if db_appointment:
        for key, value in appointment.dict().items():
            setattr(db_appointment, key, value)
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = db.query(database.Appointment).filter(database.Appointment.id == appointment_id).first()
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
    return db_appointment

# Payment CRUD operations
def get_payment(db: Session, payment_id: int):
    return db.query(database.Payment).filter(database.Payment.id == payment_id).first()

def get_payments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Payment).offset(skip).limit(limit).all()

def get_payments_by_patient(db: Session, patient_id: int):
    return db.query(database.Payment).filter(database.Payment.patient_id == patient_id).all()

def create_payment(db: Session, payment: schemas.PaymentCreate):
    # Verify patient exists
    patient = db.query(database.Patient).filter(database.Patient.id == payment.patient_id).first()
    if not patient:
        raise ValueError(f"Patient with id {payment.patient_id} not found")
    
    db_payment = database.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment(db: Session, payment_id: int, payment: schemas.PaymentUpdate):
    db_payment = db.query(database.Payment).filter(database.Payment.id == payment_id).first()
    if db_payment:
        for key, value in payment.dict().items():
            setattr(db_payment, key, value)
        db.commit()
        db.refresh(db_payment)
    return db_payment

def delete_payment(db: Session, payment_id: int):
    db_payment = db.query(database.Payment).filter(database.Payment.id == payment_id).first()
    if db_payment:
        db.delete(db_payment)
        db.commit()
    return db_payment

# Analytics functions
def get_patient_stats(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None):
    # Set default to current month if no dates provided
    if start_date is None or end_date is None:
        today = datetime.utcnow().date()
        start_date = today.replace(day=1)  # First day of current month
        # Last day of current month
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    total_patients = db.query(database.Patient).count()
    
    # Calculate average patients per day (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_patients = db.query(database.Patient).filter(
        database.Patient.created_at >= thirty_days_ago
    ).count()
    avg_patients_per_day = recent_patients / 30.0
    
    # Get patient distribution based on visit types within date range
    new_patients = db.query(database.PatientVisit).filter(
        and_(
            database.PatientVisit.visit_type == "new",
            database.PatientVisit.visit_date >= start_date,
            database.PatientVisit.visit_date <= end_date
        )
    ).count()
    
    followup_patients = db.query(database.PatientVisit).filter(
        and_(
            database.PatientVisit.visit_type == "follow-up", 
            database.PatientVisit.visit_date >= start_date,
            database.PatientVisit.visit_date <= end_date
        )
    ).count()
    
    return {
        "total_patients": total_patients,
        "avg_patients_per_day": round(avg_patients_per_day, 2),
        "new_patients": new_patients,
        "followup_patients": followup_patients,
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }

def get_appointment_stats(db: Session):
    today = datetime.utcnow().date()
    
    daily_appointments = db.query(database.Appointment).filter(
        func.date(database.Appointment.appointment_date) == today
    ).count()
    
    upcoming_appointments = db.query(database.Appointment).filter(
        and_(
            database.Appointment.appointment_date >= datetime.utcnow(),
            database.Appointment.status == "scheduled"
        )
    ).count()
    
    # Get daily appointment counts for the next 14 days (including today)
    appointment_counts = []
    for i in range(14):
        date = today + timedelta(days=i)
        count = db.query(database.Appointment).filter(
            func.date(database.Appointment.appointment_date) == date
        ).count()
        appointment_counts.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "daily_appointments": daily_appointments,
        "upcoming_appointments": upcoming_appointments,
        "appointment_counts": appointment_counts
    }

def get_finance_stats(db: Session):
    today = datetime.utcnow().date()
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    # Daily revenue
    daily_revenue = db.query(func.sum(database.Payment.amount)).filter(
        func.date(database.Payment.payment_date) == today
    ).scalar() or 0
    
    # Monthly revenue
    monthly_revenue = db.query(func.sum(database.Payment.amount)).filter(
        and_(
            extract('month', database.Payment.payment_date) == current_month,
            extract('year', database.Payment.payment_date) == current_year
        )
    ).scalar() or 0
    
    # Payment mode breakdown
    payment_mode_breakdown = db.query(
        database.Payment.payment_mode,
        func.sum(database.Payment.amount).label("total"),
        func.count(database.Payment.id).label("count")
    ).group_by(database.Payment.payment_mode).all()
    
    payment_breakdown = [
        {
            "mode": item.payment_mode,
            "total": float(item.total),
            "count": item.count
        }
        for item in payment_mode_breakdown
    ]
    
    return {
        "daily_revenue": float(daily_revenue),
        "monthly_revenue": float(monthly_revenue),
        "payment_mode_breakdown": payment_breakdown
    }

def export_patients_csv(db: Session):
    patients = db.query(database.Patient).all()
    data = []
    for patient in patients:
        data.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "mobile": patient.mobile,
            "address": patient.address,
            "referral": patient.referral,
            "history": patient.history,
            "created_at": patient.created_at
        })
    
    df = pd.DataFrame(data)
    return df

# Patient Visit CRUD operations
def get_visit(db: Session, visit_id: int):
    return db.query(database.PatientVisit).filter(database.PatientVisit.id == visit_id).first()

def get_visits(db: Session, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    query = db.query(database.PatientVisit)
    
    if patient_id:
        query = query.filter(database.PatientVisit.patient_id == patient_id)
    
    if start_date:
        query = query.filter(database.PatientVisit.visit_date >= start_date)
    
    if end_date:
        query = query.filter(database.PatientVisit.visit_date <= end_date)
    
    return query.order_by(database.PatientVisit.visit_date.desc()).offset(skip).limit(limit).all()

def create_visit(db: Session, visit: schemas.PatientVisitCreate):
    # Verify patient exists
    patient = db.query(database.Patient).filter(database.Patient.id == visit.patient_id).first()
    if not patient:
        raise ValueError(f"Patient with id {visit.patient_id} not found")
    
    db_visit = database.PatientVisit(**visit.dict())
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit

def update_visit(db: Session, visit_id: int, visit: schemas.PatientVisitUpdate):
    db_visit = db.query(database.PatientVisit).filter(database.PatientVisit.id == visit_id).first()
    if db_visit:
        for key, value in visit.dict().items():
            setattr(db_visit, key, value)
        db.commit()
        db.refresh(db_visit)
    return db_visit

def delete_visit(db: Session, visit_id: int):
    db_visit = db.query(database.PatientVisit).filter(database.PatientVisit.id == visit_id).first()
    if db_visit:
        db.delete(db_visit)
        db.commit()
    return db_visit

def get_visit_stats(db: Session):
    # Total visits
    total_visits = db.query(database.PatientVisit).count()
    
    # New vs follow-up
    new_visits = db.query(database.PatientVisit).filter(database.PatientVisit.visit_type == 'new').count()
    followup_visits = db.query(database.PatientVisit).filter(database.PatientVisit.visit_type == 'follow-up').count()
    
    # Daily visits (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_visits = db.query(
        database.PatientVisit.visit_date,
        func.count(database.PatientVisit.id).label('count')
    ).filter(
        database.PatientVisit.visit_date >= thirty_days_ago.date()
    ).group_by(
        database.PatientVisit.visit_date
    ).order_by(
        database.PatientVisit.visit_date
    ).all()
    
    # Average visits per day
    if total_visits > 0:
        first_visit = db.query(database.PatientVisit).order_by(database.PatientVisit.visit_date).first()
        if first_visit:
            days_since_first = (datetime.now().date() - first_visit.visit_date).days + 1
            avg_visits_per_day = total_visits / days_since_first
        else:
            avg_visits_per_day = 0.0
    else:
        avg_visits_per_day = 0.0
    
    visit_counts = [{"date": str(visit.visit_date), "count": visit.count} for visit in daily_visits]
    
    return {
        "total_visits": total_visits,
        "new_visits": new_visits,
        "followup_visits": followup_visits,
        "avg_visits_per_day": round(avg_visits_per_day, 1),
        "visit_counts": visit_counts
    }

def import_patients_csv(db: Session, csv_data: str):
    from io import StringIO
    df = pd.read_csv(StringIO(csv_data))
    imported_count = 0
    
    for _, row in df.iterrows():
        patient_data = {
            "name": row["name"],
            "age": int(row["age"]),
            "gender": row["gender"],
            "mobile": row["mobile"],
            "address": row.get("address", ""),
            "referral": row.get("referral", ""),
            "history": row.get("history", "")
        }
        
        patient = schemas.PatientCreate(**patient_data)
        create_patient(db, patient)
        imported_count += 1
    
    return imported_count