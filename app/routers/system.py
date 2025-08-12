from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import engine, Session as SASession, User, Technician

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/demo-users")
def demo_users():
    with SASession(bind=engine) as db:
        cust = db.execute(select(User).order_by(User.id.asc())).scalars().first()
        tech = db.execute(select(Technician).order_by(Technician.id.asc())).scalars().first()
        return {
            "customer": {"id": cust.id, "name": cust.name, "phone": cust.phone},
            "technician": {"id": tech.id, "name": tech.name, "phone": tech.phone}
        }
