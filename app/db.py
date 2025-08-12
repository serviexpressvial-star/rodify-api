from sqlalchemy import create_engine, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, Session
from sqlalchemy.sql import func
import os
from .schemas import ServiceStatus, ServiceType, Zone, Role

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rodify.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(32), unique=True)
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.customer)

class Technician(Base):
    __tablename__ = "technicians"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(32), unique=True)
    zones: Mapped[str] = mapped_column(String(120))  # csv: "ciudad,este"
    online: Mapped[bool] = mapped_column(Boolean, default=True)
    last_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

class PricingRule(Base):
    __tablename__ = "pricing_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone: Mapped[Zone] = mapped_column(SAEnum(Zone))
    service_type: Mapped[ServiceType] = mapped_column(SAEnum(ServiceType))
    base_day: Mapped[float] = mapped_column(Float)
    base_night: Mapped[float] = mapped_column(Float)
    holiday_surcharge: Mapped[float] = mapped_column(Float, default=0.0)

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    technician_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("technicians.id"), nullable=True)
    service_type: Mapped[ServiceType] = mapped_column(SAEnum(ServiceType))
    zone: Mapped[Zone] = mapped_column(SAEnum(Zone))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ServiceStatus] = mapped_column(SAEnum(ServiceStatus), default=ServiceStatus.pending)
    quoted_price: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class ServiceEvent(Base):
    __tablename__ = "service_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    status: Mapped[ServiceStatus] = mapped_column(SAEnum(ServiceStatus))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

def init_db():
    Base.metadata.create_all(engine)
    # Seed data if empty
    with Session(engine) as s:
        if s.query(User).count() == 0:
            # Users
            customer = User(name="Cliente Demo", phone="+50760000001", role=Role.customer)
            s.add(customer)
            # Technician
            tech = Technician(name="Técnico Demo", phone="+50760000002", zones="ciudad,este", online=True, last_lat=9.0, last_lng=-79.0)
            s.add(tech)
        if s.query(PricingRule).count() == 0:
            seed_rules = [
                # ciudad
                ("ciudad","bateria",18,24,5),("ciudad","cerrajeria",22,28,5),("ciudad","llanta",16,22,5),("ciudad","combustible",16,22,5),("ciudad","inspeccion",15,20,5),
                # este
                ("este","bateria",20,26,5),("este","cerrajeria",24,30,5),("este","llanta",18,24,5),("este","combustible",18,24,5),("este","inspeccion",17,22,5),
                # chepo
                ("chepo","bateria",24,32,7),("chepo","cerrajeria",28,36,7),("chepo","llanta",22,30,7),("chepo","combustible",22,30,7),("chepo","inspeccion",20,28,7)
            ]
            for z, st, d, n, h in seed_rules:
                s.add(PricingRule(zone=Zone(z), service_type=ServiceType(st), base_day=d, base_night=n, holiday_surcharge=h))
        s.commit()
