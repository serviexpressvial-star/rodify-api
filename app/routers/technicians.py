from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import engine, Session as SASession, Technician
from ..schemas import Zone, ServiceType

router = APIRouter(prefix="/technicians", tags=["technicians"])

@router.get("/available")
def available(zone: Zone):
    with SASession(bind=engine) as db:
        items = db.execute(select(Technician)).scalars().all()
        out = []
        for t in items:
            zones = [z.strip() for z in (t.zones or "").split(",") if z.strip()]
            if zone.value in zones and t.online:
                out.append({"id": t.id, "name": t.name, "phone": t.phone, "zones": zones, "online": t.online})
        return out
