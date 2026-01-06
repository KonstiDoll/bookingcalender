"""
Tests for booking endpoints
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta


class TestGetBookings:
    """Tests for GET /api/bookings"""

    @pytest.mark.asyncio
    async def test_get_bookings_empty(self, client: AsyncClient, auth_headers_admin: dict):
        """Empty database returns empty list"""
        response = await client.get("/api/bookings", headers=auth_headers_admin)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_bookings_unauthenticated(self, client: AsyncClient):
        """Unauthenticated request returns 401"""
        response = await client.get("/api/bookings")

        assert response.status_code == 401


class TestCreateBooking:
    """Tests for POST /api/bookings"""

    @pytest.mark.asyncio
    async def test_create_booking_admin(self, client: AsyncClient, auth_headers_admin: dict):
        """Admin can create booking for any party"""
        today = date.today()
        response = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 1,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=3)),
                "note": "Test booking"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["party_id"] == 1
        assert data["party_name"] == "Siggi & Mausi"
        assert data["note"] == "Test booking"

    @pytest.mark.asyncio
    async def test_create_booking_own_party(self, client: AsyncClient, auth_headers_party1: dict):
        """User can create booking for own party"""
        today = date.today()
        response = await client.post(
            "/api/bookings",
            headers=auth_headers_party1,
            json={
                "party_id": 1,
                "start_date": str(today + timedelta(days=10)),
                "end_date": str(today + timedelta(days=12))
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["party_id"] == 1

    @pytest.mark.asyncio
    async def test_create_booking_other_party_forbidden(self, client: AsyncClient, auth_headers_party1: dict):
        """User cannot create booking for other party"""
        today = date.today()
        response = await client.post(
            "/api/bookings",
            headers=auth_headers_party1,
            json={
                "party_id": 2,
                "start_date": str(today + timedelta(days=20)),
                "end_date": str(today + timedelta(days=22))
            }
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_booking_invalid_party(self, client: AsyncClient, auth_headers_admin: dict):
        """Invalid party_id returns 422"""
        today = date.today()
        response = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 99,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=1))
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_end_before_start(self, client: AsyncClient, auth_headers_admin: dict):
        """End date before start date returns 422"""
        today = date.today()
        response = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 1,
                "start_date": str(today + timedelta(days=5)),
                "end_date": str(today)
            }
        )

        assert response.status_code == 422


class TestBookingOverlap:
    """Tests for booking overlap detection"""

    @pytest.mark.asyncio
    async def test_overlapping_booking_rejected(self, client: AsyncClient, auth_headers_admin: dict):
        """Overlapping bookings are rejected"""
        today = date.today() + timedelta(days=100)  # Use future dates to avoid conflicts

        # Create first booking
        response1 = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 1,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=5))
            }
        )
        assert response1.status_code == 201

        # Try to create overlapping booking
        response2 = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 2,
                "start_date": str(today + timedelta(days=3)),
                "end_date": str(today + timedelta(days=7))
            }
        )
        assert response2.status_code == 409

    @pytest.mark.asyncio
    async def test_adjacent_booking_allowed(self, client: AsyncClient, auth_headers_admin: dict):
        """Adjacent (non-overlapping) bookings are allowed"""
        today = date.today() + timedelta(days=200)  # Use future dates

        # Create first booking
        response1 = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 1,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=5))
            }
        )
        assert response1.status_code == 201

        # Create adjacent booking (starts day after first ends)
        response2 = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 2,
                "start_date": str(today + timedelta(days=6)),
                "end_date": str(today + timedelta(days=10))
            }
        )
        assert response2.status_code == 201

    @pytest.mark.asyncio
    async def test_same_day_booking_overlap(self, client: AsyncClient, auth_headers_admin: dict):
        """Same day end and start is considered overlap"""
        today = date.today() + timedelta(days=300)

        # Create first booking
        response1 = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 1,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=5))
            }
        )
        assert response1.status_code == 201

        # Try booking starting on same day as first ends
        response2 = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 2,
                "start_date": str(today + timedelta(days=5)),
                "end_date": str(today + timedelta(days=7))
            }
        )
        assert response2.status_code == 409


class TestDeleteBooking:
    """Tests for DELETE /api/bookings/{id}"""

    @pytest.mark.asyncio
    async def test_delete_booking_admin(self, client: AsyncClient, auth_headers_admin: dict):
        """Admin can delete any booking"""
        today = date.today() + timedelta(days=400)

        # Create booking
        create_response = await client.post(
            "/api/bookings",
            headers=auth_headers_admin,
            json={
                "party_id": 1,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=2))
            }
        )
        booking_id = create_response.json()["id"]

        # Delete booking
        delete_response = await client.delete(
            f"/api/bookings/{booking_id}",
            headers=auth_headers_admin
        )
        assert delete_response.status_code == 200

        # Verify deleted
        get_response = await client.get("/api/bookings", headers=auth_headers_admin)
        bookings = get_response.json()
        assert not any(b["id"] == booking_id for b in bookings)

    @pytest.mark.asyncio
    async def test_delete_own_booking(self, client: AsyncClient, auth_headers_party1: dict, auth_headers_admin: dict):
        """User can delete own party's booking"""
        today = date.today() + timedelta(days=500)

        # Create booking as party 1
        create_response = await client.post(
            "/api/bookings",
            headers=auth_headers_party1,
            json={
                "party_id": 1,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=2))
            }
        )
        booking_id = create_response.json()["id"]

        # Delete as party 1
        delete_response = await client.delete(
            f"/api/bookings/{booking_id}",
            headers=auth_headers_party1
        )
        assert delete_response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_other_booking_forbidden(self, client: AsyncClient, auth_headers_party1: dict, auth_headers_party2: dict):
        """User cannot delete other party's booking"""
        today = date.today() + timedelta(days=600)

        # Create booking as party 2
        create_response = await client.post(
            "/api/bookings",
            headers=auth_headers_party2,
            json={
                "party_id": 2,
                "start_date": str(today),
                "end_date": str(today + timedelta(days=2))
            }
        )
        booking_id = create_response.json()["id"]

        # Try to delete as party 1
        delete_response = await client.delete(
            f"/api/bookings/{booking_id}",
            headers=auth_headers_party1
        )
        assert delete_response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_booking(self, client: AsyncClient, auth_headers_admin: dict):
        """Deleting non-existent booking returns 404"""
        response = await client.delete(
            "/api/bookings/99999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404


class TestGetParties:
    """Tests for GET /api/parties"""

    @pytest.mark.asyncio
    async def test_get_parties(self, client: AsyncClient, auth_headers_admin: dict):
        """Returns all predefined parties"""
        response = await client.get("/api/parties", headers=auth_headers_admin)

        assert response.status_code == 200
        parties = response.json()
        assert len(parties) == 4
        assert parties[0]["name"] == "Siggi & Mausi"

    @pytest.mark.asyncio
    async def test_get_parties_unauthenticated(self, client: AsyncClient):
        """Unauthenticated request returns 401"""
        response = await client.get("/api/parties")

        assert response.status_code == 401
