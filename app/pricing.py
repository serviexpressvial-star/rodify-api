from datetime import datetime, time
from sqlalchemy.orm import Session
from .db import PricingRule
from .schemas import Zone, ServiceType

NIGHT_START = time(22, 0, 0)
NIGHT_END = time(6, 0, 0)

def is_night(dt: datetime) -> bool:
    t = dt.time()
    return t >= NIGHT_START or t < NIGHT_END

def quote(db: Session, service_type: ServiceType, zone: Zone, when: datetime, is_holiday: bool=False) -> float:
    rule = db.query(PricingRule).filter_by(zone=zone, service_type=service_type).first()
    if not rule:
        raise ValueError("No pricing rule for given zone/service")
    base = rule.base_night if is_night(when) else rule.base_day
    price = base + (rule.holiday_surcharge if is_holiday else 0.0)
    return round(price, 2)
