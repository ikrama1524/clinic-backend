from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io
import crud, schemas, database

# Create tables on startup
database.create_tables()

app = FastAPI(
    title="Clinic Management API",
    description="A comprehensive clinic management system API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Patient endpoints
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(database.get_db)):
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    patients = crud.get_patients(db, skip=skip, limit=limit, search=search)
    return patients

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(database.get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.put("/patients/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int, 
    patient: schemas.PatientUpdate, 
    db: Session = Depends(database.get_db)
):
    db_patient = crud.update_patient(db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(database.get_db)):
    try:
        db_patient = crud.delete_patient(db, patient_id=patient_id)
        if db_patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"message": "Patient deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

# Appointment endpoints
@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_appointment(db=db, appointment=appointment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    appointments = crud.get_appointments(db, skip=skip, limit=limit)
    return appointments

@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(appointment_id: int, db: Session = Depends(database.get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int, 
    appointment: schemas.AppointmentUpdate, 
    db: Session = Depends(database.get_db)
):
    db_appointment = crud.update_appointment(db, appointment_id=appointment_id, appointment=appointment)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(database.get_db)):
    db_appointment = crud.delete_appointment(db, appointment_id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}

# Payment endpoints
@app.post("/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_payment(db=db, payment=payment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/payments/", response_model=List[schemas.Payment])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    payments = crud.get_payments(db, skip=skip, limit=limit)
    return payments

@app.get("/payments/patient/{patient_id}", response_model=List[schemas.Payment])
def read_payments_by_patient(patient_id: int, db: Session = Depends(database.get_db)):
    payments = crud.get_payments_by_patient(db, patient_id=patient_id)
    return payments

@app.get("/payments/{payment_id}", response_model=schemas.Payment)
def read_payment(payment_id: int, db: Session = Depends(database.get_db)):
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.put("/payments/{payment_id}", response_model=schemas.Payment)
def update_payment(
    payment_id: int, 
    payment: schemas.PaymentUpdate, 
    db: Session = Depends(database.get_db)
):
    db_payment = crud.update_payment(db, payment_id=payment_id, payment=payment)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(database.get_db)):
    db_payment = crud.delete_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}

# Analytics endpoints
@app.get("/analytics/patients", response_model=schemas.PatientStats)
def get_patient_analytics(db: Session = Depends(database.get_db)):
    return crud.get_patient_stats(db)

@app.get("/analytics/appointments", response_model=schemas.AppointmentStats)
def get_appointment_analytics(db: Session = Depends(database.get_db)):
    return crud.get_appointment_stats(db)

@app.get("/analytics/finance", response_model=schemas.FinanceStats)
def get_finance_analytics(db: Session = Depends(database.get_db)):
    return crud.get_finance_stats(db)

@app.get("/analytics/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    # Parse date strings if provided
    parsed_start_date = None
    parsed_end_date = None
    if start_date:
        parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    patient_stats = crud.get_patient_stats(db, parsed_start_date, parsed_end_date)
    appointment_stats = crud.get_appointment_stats(db)
    finance_stats = crud.get_finance_stats(db)
    visit_stats = crud.get_visit_stats(db)
    
    return {
        "patient_stats": patient_stats,
        "appointment_stats": appointment_stats,
        "finance_stats": finance_stats,
        "visit_stats": visit_stats
    }

# Patient Visit endpoints
@app.post("/visits/", response_model=schemas.PatientVisit)
def create_visit(visit: schemas.PatientVisitCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_visit(db=db, visit=visit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/visits/", response_model=List[schemas.PatientVisit])
def read_visits(
    skip: int = 0, 
    limit: int = 100, 
    patient_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    visits = crud.get_visits(db, skip=skip, limit=limit, patient_id=patient_id, start_date=start_date, end_date=end_date)
    return visits

@app.get("/visits/{visit_id}", response_model=schemas.PatientVisit)
def read_visit(visit_id: int, db: Session = Depends(database.get_db)):
    db_visit = crud.get_visit(db, visit_id=visit_id)
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Visit not found")
    return db_visit

@app.put("/visits/{visit_id}", response_model=schemas.PatientVisit)
def update_visit(
    visit_id: int, 
    visit: schemas.PatientVisitUpdate, 
    db: Session = Depends(database.get_db)
):
    db_visit = crud.update_visit(db, visit_id=visit_id, visit=visit)
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Visit not found")
    return db_visit

@app.delete("/visits/{visit_id}")
def delete_visit(visit_id: int, db: Session = Depends(database.get_db)):
    db_visit = crud.delete_visit(db, visit_id=visit_id)
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Visit not found")
    return {"message": "Visit deleted successfully"}

@app.get("/analytics/visits", response_model=schemas.VisitStats)
def get_visit_analytics(db: Session = Depends(database.get_db)):
    return crud.get_visit_stats(db)

# Import/Export endpoints
@app.get("/export/patients")
def export_patients_csv(db: Session = Depends(database.get_db)):
    df = crud.export_patients_csv(db)
    
    # Convert DataFrame to CSV string
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Return as downloadable file
    headers = {
        'Content-Disposition': 'attachment; filename="patients_export.csv"'
    }
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers=headers
    )

@app.post("/import/patients")
async def import_patients_csv(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    
    try:
        imported_count = crud.import_patients_csv(db, csv_data)
        return {"message": f"Successfully imported {imported_count} patients"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Clinic Management API is running", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)