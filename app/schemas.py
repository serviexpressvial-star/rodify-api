from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class Role(str, Enum):
    customer = "customer"
    technician = "technician"
    admin = "admin"

class Zone(str, Enum):
    ciudad = "ciudad"
    este = "este"
    chepo = "chepo"

class ServiceType(str, Enum):
    bateria = "bateria"
    cerrajeria = "cerrajeria"
    llanta = "llanta"
    combustible = "combustible"
    inspeccion = "inspeccion"

class ServiceStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    en_route = "en_route"
    arrived = "arrived"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"

class LocationIn(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None
    zone: Zone

class ServiceRequestIn(BaseModel):
    customer_id: int
    service_type: ServiceType
    location: LocationIn
    payment_method: str = Field(description="ej.: yappy, link, efectivo, transferencia")

class StatusUpdate(BaseModel):
    status: ServiceStatus
    notes: Optional[str] = None
    photos: Optional[list[str]] = None

class QuoteIn(BaseModel):
    service_type: ServiceType
    zone: Zone
    date_time_iso: Optional[str] = None
    is_holiday: bool = False
