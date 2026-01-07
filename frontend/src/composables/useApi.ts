import { ref, type Ref } from 'vue'
import { useAuth } from './useAuth'
import type { Party, Booking, BookingCreate } from '../types'

const API_BASE = '/api'

// Reactive state - shared across all components
export const parties: Ref<Party[]> = ref([])
export const bookings: Ref<Booking[]> = ref([])

export function useApi() {
  const { getAuthHeaders } = useAuth()

  async function loadParties(): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/parties`, {
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      parties.value = await response.json()
    } catch (error) {
      console.error('Error loading parties:', error)
      throw error
    }
  }

  async function loadBookings(): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/bookings`, {
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      bookings.value = await response.json()
    } catch (error) {
      console.error('Error loading bookings:', error)
      throw error
    }
  }

  async function createBooking(booking: BookingCreate): Promise<Booking> {
    const response = await fetch(`${API_BASE}/bookings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(booking)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Fehler beim Speichern')
    }

    await loadBookings()
    return response.json()
  }

  async function updateBooking(id: number, booking: BookingCreate): Promise<Booking> {
    const response = await fetch(`${API_BASE}/bookings/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(booking)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Fehler beim Aktualisieren')
    }

    const result = await response.json()
    await loadBookings()
    return result
  }

  async function deleteBooking(id: number): Promise<void> {
    const response = await fetch(`${API_BASE}/bookings/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Fehler beim Löschen')
    }

    await loadBookings()
  }

  return {
    parties,
    bookings,
    loadParties,
    loadBookings,
    createBooking,
    updateBooking,
    deleteBooking
  }
}
