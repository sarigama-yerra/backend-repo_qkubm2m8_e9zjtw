import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Sports Club MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Sports Club MVP Backend Running"}


# ============== Schemas endpoint for viewer ==============
from schemas import Club, Team, Member, Event, Attendance, PaymentSetup, Payment, Announcement, Document

class SchemaInfo(BaseModel):
    name: str
    fields: List[str]

@app.get("/schema")
def get_schema():
    models = [Club, Team, Member, Event, Attendance, PaymentSetup, Payment, Announcement, Document]
    return {
        "models": [
            {
                "name": m.__name__,
                "collection": m.__name__.lower(),
                "fields": list(m.model_fields.keys()),
            }
            for m in models
        ]
    }


# ============== Helper functions ==============

def ensure_db():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")


# ============== Club & Team Management ==============

@app.post("/clubs")
def create_club(payload: Club):
    ensure_db()
    club_id = create_document("club", payload)
    return {"id": club_id}

@app.get("/clubs")
def list_clubs():
    ensure_db()
    return get_documents("club")

@app.post("/teams")
def create_team(payload: Team):
    ensure_db()
    team_id = create_document("team", payload)
    return {"id": team_id}

@app.get("/teams")
def list_teams(club_id: Optional[str] = None):
    ensure_db()
    filt = {"club_id": club_id} if club_id else {}
    return get_documents("team", filt)

@app.post("/members")
def create_member(payload: Member):
    ensure_db()
    member_id = create_document("member", payload)
    return {"id": member_id}

@app.get("/members")
def list_members(club_id: Optional[str] = None, team_id: Optional[str] = None):
    ensure_db()
    filt = {}
    if club_id:
        filt["club_id"] = club_id
    if team_id:
        filt["team_ids"] = team_id
    return get_documents("member", filt)


# ============== Schedules & Attendance ==============

@app.post("/events")
def create_event(payload: Event):
    ensure_db()
    event_id = create_document("event", payload)
    return {"id": event_id}

@app.get("/events")
def list_events(club_id: Optional[str] = None, team_id: Optional[str] = None):
    ensure_db()
    filt = {}
    if club_id:
        filt["club_id"] = club_id
    if team_id:
        filt["team_id"] = team_id
    return get_documents("event", filt)

class AttendanceIn(BaseModel):
    event_id: str
    member_id: str
    status: str

@app.post("/attendance")
def mark_attendance(payload: AttendanceIn):
    ensure_db()
    att_id = create_document("attendance", payload.model_dump())
    return {"id": att_id}

@app.get("/attendance")
def list_attendance(event_id: Optional[str] = None):
    ensure_db()
    filt = {"event_id": event_id} if event_id else {}
    return get_documents("attendance", filt)


# ============== Payments & Basic Finance ==============

@app.post("/payment-setups")
def create_payment_setup(payload: PaymentSetup):
    ensure_db()
    setup_id = create_document("paymentsetup", payload)
    return {"id": setup_id}

@app.get("/payment-setups")
def list_payment_setups(club_id: Optional[str] = None, team_id: Optional[str] = None, member_id: Optional[str] = None):
    ensure_db()
    filt = {}
    if club_id:
        filt["club_id"] = club_id
    if team_id:
        filt["team_id"] = team_id
    if member_id:
        filt["member_id"] = member_id
    return get_documents("paymentsetup", filt)

@app.post("/payments")
def create_payment(payload: Payment):
    ensure_db()
    pay_id = create_document("payment", payload)
    return {"id": pay_id}

@app.get("/payments")
def list_payments(club_id: Optional[str] = None, status: Optional[str] = None):
    ensure_db()
    filt = {}
    if club_id:
        filt["club_id"] = club_id
    if status:
        filt["status"] = status
    return get_documents("payment", filt)

@app.get("/finance/summary")
def finance_summary(club_id: str):
    ensure_db()
    payments = get_documents("payment", {"club_id": club_id})
    total_paid = sum(p.get("amount", 0) for p in payments if p.get("status") == "paid")
    total_pending = sum(p.get("amount", 0) for p in payments if p.get("status") == "pending")
    return {
        "total_paid": total_paid,
        "total_pending": total_pending,
        "paid_count": sum(1 for p in payments if p.get("status") == "paid"),
        "pending_count": sum(1 for p in payments if p.get("status") == "pending"),
    }


# ============== Communication ==============

@app.post("/announcements")
def create_announcement(payload: Announcement):
    ensure_db()
    ann_id = create_document("announcement", payload)
    return {"id": ann_id}

@app.get("/announcements")
def list_announcements(team_id: Optional[str] = None, club_id: Optional[str] = None):
    ensure_db()
    filt = {}
    if team_id:
        filt["team_id"] = team_id
    if club_id:
        filt["club_id"] = club_id
    return get_documents("announcement", filt)


# ============== Documents & Tax Support ==============

@app.post("/documents")
def create_document_record(payload: Document):
    ensure_db()
    doc_id = create_document("document", payload)
    return {"id": doc_id}

@app.get("/documents")
def list_documents(club_id: Optional[str] = None, member_id: Optional[str] = None, type: Optional[str] = None):
    ensure_db()
    filt = {}
    if club_id:
        filt["club_id"] = club_id
    if member_id:
        filt["member_id"] = member_id
    if type:
        filt["type"] = type
    return get_documents("document", filt)


# ============== Health/Test ==============

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            import os as _os
            response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
