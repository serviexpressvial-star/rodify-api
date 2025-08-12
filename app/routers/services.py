from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from ..db import engine, Session as SASession, Service, ServiceEvent, User, Technician
from ..schemas import ServiceRequestIn, ServiceStatus, QuoteIn
from ..pricing import quote
from ..schemas import Zone, ServiceType

router = APIRouter(prefix="/services", tags=["services"])

def next_code(db: Session) -> str:
    last = db.execute(select(Service).order_by(Service.id.desc())).scalars().first()
    n = (last.id + 1) if last else 1
    return f"SVC-{n:05d}"

@router.post("")
def create_service(payload: ServiceRequestIn):
    with SASession(bind=engine) as db:
        # verify customer exists
        customer = db.get(User, payload.customer_id)
        if not customer:
            raise HTTPException(400, "customer not found")
        price = quote(db, payload.service_type, payload.location.zone, datetime.utcnow(), False)
        code = next_code(db)
        svc = Service(
            code=code,
            customer_id=payload.customer_id,
            technician_id=None,
            service_type=payload.service_type,
            zone=payload.location.zone,
            lat=payload.location.lat,
            lng=payload.location.lng,
            address=payload.location.address,
            status=ServiceStatus.pending,
            quoted_price=price,
            payment_method=payload.payment_method
        )
        db.add(svc)
        db.flush()
        db.add(ServiceEvent(service_id=svc.id, status=ServiceStatus.pending, notes="created"))
        db.commit()
        return {"id": svc.id, "code": svc.code, "status": svc.status, "quoted_price": svc.quoted_price}

@router.get("/{code}")
def get_service(code: str):
    with SASession(bind=engine) as db:
        svc = db.execute(select(Service).where(Service.code == code)).scalars().first()
        if not svc:
            raise HTTPException(404, "service not found")
        return {
            "id": svc.id, "code": svc.code, "status": svc.status,
            "customer_id": svc.customer_id, "technician_id": svc.technician_id,
            "service_type": svc.service_type, "zone": svc.zone, "lat": svc.lat, "lng": svc.lng,
            "address": svc.address, "quoted_price": svc.quoted_price, "payment_method": svc.payment_method,
            "created_at": str(svc.created_at), "updated_at": str(svc.updated_at), "notes": svc.notes
        }

@router.post("/{code}/accept")
def accept_service(code: str, technician_id: int):
    with SASession(bind=engine) as db:
        svc = db.execute(select(Service).where(Service.code == code)).scalars().first()
        if not svc:
            raise HTTPException(404, "service not found")
        tech = db.get(Technician, technician_id)
        if not tech:
            raise HTTPException(400, "technician not found")
        svc.technician_id = technician_id
        svc.status = ServiceStatus.assigned
        db.add(ServiceEvent(service_id=svc.id, status=ServiceStatus.assigned, notes=f"assigned to {technician_id}"))
        db.commit()
        return {"ok": True, "code": svc.code, "status": svc.status, "technician_id": svc.technician_id}

@router.post("/{code}/status")
def update_status(code: str, status: ServiceStatus, notes: str | None = None):
    with SASession(bind=engine) as db:
        svc = db.execute(select(Service).where(Service.code == code)).scalars().first()
        if not svc:
            raise HTTPException(404, "service not found")
        svc.status = status
        if notes:
            svc.notes = (svc.notes + " | " if svc.notes else "") + notes
        db.add(ServiceEvent(service_id=svc.id, status=status, notes=notes))
        db.commit()
        return {"ok": True, "code": svc.code, "status": svc.status}

@router.post("/quote")
def quote_route(payload: QuoteIn):
    with SASession(bind=engine) as db:
        when = datetime.fromisoformat(payload.date_time_iso) if payload.date_time_iso else datetime.utcnow()
        price = quote(db, payload.service_type, payload.zone, when, payload.is_holiday)
        return {"price": price, "currency": "USD", "at": when.isoformat()}
