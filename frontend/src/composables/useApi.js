import { ref } from 'vue'

const API_BASE = '/api'

export const parties = ref([])
export const bookings = ref([])

export function useApi() {
  async function loadParties() {
    try {
      const response = await fetch(`${API_BASE}/parties`)
      parties.value = await response.json()
    } catch (error) {
      console.error('Error loading parties:', error)
      throw error
    }
  }

  async function loadBookings() {
    try {
      const response = await fetch(`${API_BASE}/bookings`)
      bookings.value = await response.json()
    } catch (error) {
      console.error('Error loading bookings:', error)
      throw error
    }
  }

  async function createBooking(booking) {
    const response = await fetch(`${API_BASE}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(booking)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Fehler beim Speichern')
    }

    await loadBookings()
    return response.json()
  }

  async function deleteBooking(id) {
    const response = await fetch(`${API_BASE}/bookings/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      throw new Error('Fehler beim Löschen')
    }

    await loadBookings()
  }

  return {
    parties,
    bookings,
    loadParties,
    loadBookings,
    createBooking,
    deleteBooking
  }
}
