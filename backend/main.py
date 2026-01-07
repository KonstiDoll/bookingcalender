"""
Ferienhaus Kalender - FastAPI Backend
Vacation rental booking calendar API with PostgreSQL
"""
from datetime import date
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db, Booking, Party
from auth import (
    verify_password,
    create_session_token,
    get_current_user,
    can_modify_booking,
    User
)


# Pydantic Models
class BookingCreate(BaseModel):
    party_id: int
    start_date: date
    end_date: date
    note: Optional[str] = None

    @field_validator('end_date')
    @classmethod
    def end_date_after_start(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v

    @field_validator('party_id')
    @classmethod
    def valid_party_id(cls, v):
        if v < 1 or v > 4:
            raise ValueError('party_id must be between 1 and 4')
        return v


class BookingResponse(BaseModel):
    id: int
    party_id: int
    party_name: str
    party_color: str
    start_date: date
    end_date: date
    note: Optional[str]

    class Config:
        from_attributes = True


class PartyResponse(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict
    message: str


class UserResponse(BaseModel):
    party_id: Optional[int]
    is_admin: bool
    username: str


# Predefined parties with earth-tone colors
PARTIES = [
    {"id": 1, "name": "Siggi & Mausi", "color": "#2D5A47"},   # Forest Green
    {"id": 2, "name": "Silke & Wolfi & Zoe", "color": "#4A6B8A"},  # Ocean Slate
    {"id": 3, "name": "Claudi & Wolfram", "color": "#C4703D"},    # Terracotta
    {"id": 4, "name": "Extern", "color": "#6B4E71"}  # Wild Plum
    # {"id": 5, "name": "Familie Wagner", "color": "#B8860B"},   # Golden Amber
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize database on startup"""
    await init_db()
    yield


# FastAPI Application
app = FastAPI(
    title="Ferienhaus Kalender API",
    description="Buchungskalender für Ferienwohnungen",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
def get_party_by_id(party_id: int) -> Optional[dict]:
    """Get party info by ID"""
    for party in PARTIES:
        if party["id"] == party_id:
            return party
    return None


async def check_booking_overlap(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    exclude_id: Optional[int] = None
) -> bool:
    """Check if there's an overlapping booking"""
    query = select(Booking).where(
        and_(
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        )
    )
    if exclude_id:
        query = query.where(Booking.id != exclude_id)

    result = await db.execute(query)
    return result.scalar() is not None


# Authentication Routes
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Authenticate user and return session token"""
    user = verify_password(credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Ungültiger Benutzername oder Passwort"
        )

    token = create_session_token(user)

    return LoginResponse(
        token=token,
        user={
            "party_id": user.party_id,
            "is_admin": user.is_admin,
            "username": user.username
        },
        message=f"Erfolgreich angemeldet als {user.username}"
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return UserResponse(
        party_id=current_user.party_id,
        is_admin=current_user.is_admin,
        username=current_user.username
    )


@app.post("/api/auth/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (token invalidation handled client-side)"""
    return MessageResponse(message="Erfolgreich abgemeldet")


# API Routes
@app.get("/api/parties", response_model=list[PartyResponse])
async def get_parties(current_user: User = Depends(get_current_user)):
    """Get all available parties (families) - requires authentication"""
    return PARTIES


@app.get("/api/bookings", response_model=list[BookingResponse])
async def get_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings with party information - requires authentication"""
    result = await db.execute(
        select(Booking).order_by(Booking.start_date)
    )
    bookings = result.scalars().all()

    response = []
    for booking in bookings:
        party = get_party_by_id(booking.party_id)
        response.append(BookingResponse(
            id=booking.id,
            party_id=booking.party_id,
            party_name=party["name"] if party else "Unbekannt",
            party_color=party["color"] if party else "#888888",
            start_date=booking.start_date,
            end_date=booking.end_date,
            note=booking.note
        ))

    return response


@app.post("/api/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new booking - requires authentication and authorization"""
    # Validate party exists
    party = get_party_by_id(booking.party_id)
    if not party:
        raise HTTPException(status_code=400, detail="Ungültige Familie")

    # Check authorization: users can only book for their own party
    if not can_modify_booking(current_user, booking.party_id):
        raise HTTPException(
            status_code=403,
            detail="Sie können nur Buchungen für Ihre eigene Familie erstellen"
        )

    # Check for overlapping bookings
    if await check_booking_overlap(db, booking.start_date, booking.end_date):
        raise HTTPException(
            status_code=409,
            detail="Es gibt bereits eine Buchung in diesem Zeitraum"
        )

    # Create booking
    db_booking = Booking(
        party_id=booking.party_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        note=booking.note
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)

    return BookingResponse(
        id=db_booking.id,
        party_id=db_booking.party_id,
        party_name=party["name"],
        party_color=party["color"],
        start_date=db_booking.start_date,
        end_date=db_booking.end_date,
        note=db_booking.note
    )


@app.put("/api/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a booking by ID - requires authentication and authorization"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar()

    if not booking:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")

    # Check authorization: users can only update their own party's bookings
    if not can_modify_booking(current_user, booking.party_id):
        raise HTTPException(
            status_code=403,
            detail="Sie können nur Ihre eigenen Buchungen bearbeiten"
        )

    # If changing party, check authorization for new party too
    if booking_data.party_id != booking.party_id:
        if not can_modify_booking(current_user, booking_data.party_id):
            raise HTTPException(
                status_code=403,
                detail="Sie können keine Buchungen für andere Familien erstellen"
            )

    # Validate new party exists
    party = get_party_by_id(booking_data.party_id)
    if not party:
        raise HTTPException(status_code=400, detail="Ungültige Familie")

    # Check for overlapping bookings (exclude current booking)
    if await check_booking_overlap(db, booking_data.start_date, booking_data.end_date, exclude_id=booking_id):
        raise HTTPException(
            status_code=409,
            detail="Es gibt bereits eine Buchung in diesem Zeitraum"
        )

    # Update booking
    booking.party_id = booking_data.party_id
    booking.start_date = booking_data.start_date
    booking.end_date = booking_data.end_date
    booking.note = booking_data.note

    await db.commit()
    await db.refresh(booking)

    return BookingResponse(
        id=booking.id,
        party_id=booking.party_id,
        party_name=party["name"],
        party_color=party["color"],
        start_date=booking.start_date,
        end_date=booking.end_date,
        note=booking.note
    )


@app.delete("/api/bookings/{booking_id}", response_model=MessageResponse)
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a booking by ID - requires authentication and authorization"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar()

    if not booking:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")

    # Check authorization: users can only delete their own party's bookings
    if not can_modify_booking(current_user, booking.party_id):
        raise HTTPException(
            status_code=403,
            detail="Sie können nur Ihre eigenen Buchungen löschen"
        )

    await db.delete(booking)
    await db.commit()

    return MessageResponse(message="Buchung erfolgreich gelöscht")


# Mount static files and serve frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the Vue frontend"""
    return FileResponse("../frontend/index.html")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}
