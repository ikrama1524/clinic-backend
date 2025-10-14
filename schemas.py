from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# Patient Schemas
class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    mobile: str
    address: Optional[str] = None
    referral: Optional[str] = None
    history: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_name: str
    appointment_date: datetime
    status: str = "scheduled"  # scheduled/completed/cancelled

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient: Optional[Patient] = None
    
    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    patient_id: int
    amount: float
    payment_mode: str  # cash/upi/card
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    payment_date: Optional[datetime] = None

class PaymentUpdate(PaymentBase):
    payment_date: datetime

class Payment(PaymentBase):
    id: int
    payment_date: datetime
    patient: Optional[Patient] = None
    
    class Config:
        from_attributes = True

# Patient Visit Schemas
class PatientVisitBase(BaseModel):
    patient_id: int
    visit_date: date
    visit_type: str  # new/follow-up
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    
    # Prescription fields
    observation: Optional[str] = None
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    next_visit_date: Optional[date] = None
    tests: Optional[str] = None

class PatientVisitCreate(PatientVisitBase):
    pass

class PatientVisitUpdate(PatientVisitBase):
    pass

class PatientVisit(PatientVisitBase):
    id: int
    created_at: datetime
    patient: Optional[Patient] = None
    
    class Config:
        from_attributes = True

# Analytics Schemas
class PatientStats(BaseModel):
    total_patients: int
    avg_patients_per_day: float
    new_patients: int
    followup_patients: int

class AppointmentStats(BaseModel):
    daily_appointments: int
    upcoming_appointments: int
    appointment_counts: List[dict]

class FinanceStats(BaseModel):
    daily_revenue: float
    monthly_revenue: float
    payment_mode_breakdown: List[dict]

class VisitStats(BaseModel):
    total_visits: int
    new_visits: int
    followup_visits: int
    avg_visits_per_day: float
    visit_counts: List[dict]

class DashboardStats(BaseModel):
    patient_stats: PatientStats
    appointment_stats: AppointmentStats
    finance_stats: FinanceStats
    visit_stats: VisitStats