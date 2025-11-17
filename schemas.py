"""
Database Schemas for Sports Club MVP

Each Pydantic model represents a MongoDB collection.
Collection name = lowercase class name (e.g., Club -> "club").
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime

# Core entities
class Club(BaseModel):
    name: str = Field(..., description="Club name")
    country: Optional[str] = Field(None, description="Country")
    city: Optional[str] = Field(None, description="City")
    address: Optional[str] = Field(None, description="Street address")
    contact_email: Optional[EmailStr] = Field(None, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, description="Primary contact phone")

class Team(BaseModel):
    club_id: str = Field(..., description="Parent club ID")
    name: str = Field(..., description="Team name")
    age_group: Optional[str] = Field(None, description="e.g., U8, U12, Seniors")
    coach_ids: List[str] = Field(default_factory=list, description="List of coach member IDs")

class Member(BaseModel):
    club_id: str = Field(..., description="Parent club ID")
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Literal['player','coach','parent']
    birthdate: Optional[date] = None
    position: Optional[str] = Field(None, description="Player position")
    parent_ids: List[str] = Field(default_factory=list, description="Linked parent member IDs")
    team_ids: List[str] = Field(default_factory=list, description="Teams this member belongs to")
    notes: Optional[str] = None

class Event(BaseModel):
    team_id: str
    club_id: str
    type: Literal['training','match']
    title: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    opponent: Optional[str] = Field(None, description="For matches")

class Attendance(BaseModel):
    event_id: str
    member_id: str
    status: Literal['present','absent','excused']

class PaymentSetup(BaseModel):
    club_id: str
    team_id: Optional[str] = None
    member_id: Optional[str] = None
    amount: float = Field(..., ge=0)
    interval: Literal['monthly','quarterly','yearly']
    currency: Literal['EUR','USD','GBP'] = 'EUR'

class Payment(BaseModel):
    club_id: str
    member_id: str
    team_id: Optional[str] = None
    amount: float = Field(..., ge=0)
    currency: Literal['EUR','USD','GBP'] = 'EUR'
    status: Literal['pending','paid','failed'] = 'pending'
    method: Optional[Literal['stripe','sepa','manual']] = None
    due_date: Optional[date] = None
    paid_at: Optional[datetime] = None
    reference: Optional[str] = None

class Announcement(BaseModel):
    team_id: str
    club_id: str
    title: str
    message: str
    level: Literal['info','warning','urgent'] = 'info'

class Document(BaseModel):
    club_id: str
    member_id: Optional[str] = None
    payment_id: Optional[str] = None
    type: Literal['receipt','tax_report']
    url: Optional[str] = None
    period: Optional[str] = Field(None, description="e.g., 2025 or 2025-01")

# The /schema endpoint will read these models for viewer/validation
__all__ = [
    'Club','Team','Member','Event','Attendance','PaymentSetup','Payment','Announcement','Document'
]
