import { ref, computed, type Ref, type ComputedRef } from 'vue'
import type { User, LoginResponse } from '../types'

const API_BASE = '/api'

// Reactive state - shared across all components
const currentUser: Ref<User | null> = ref(null)
const sessionToken: Ref<string | null> = ref(localStorage.getItem('session_token'))

// Computed properties
const isAuthenticated: ComputedRef<boolean> = computed(() => !!currentUser.value)
const isAdmin: ComputedRef<boolean> = computed(() => currentUser.value?.is_admin || false)

export function useAuth() {
  async function login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login fehlgeschlagen')
    }

    const data: LoginResponse = await response.json()

    // Store token and user info
    sessionToken.value = data.token
    currentUser.value = data.user
    localStorage.setItem('session_token', data.token)

    return data
  }

  function logout(): void {
    sessionToken.value = null
    currentUser.value = null
    localStorage.removeItem('session_token')
  }

  async function verifySession(): Promise<boolean> {
    if (!sessionToken.value) {
      return false
    }

    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${sessionToken.value}`
        }
      })

      if (response.ok) {
        currentUser.value = await response.json()
        return true
      }
    } catch (error) {
      console.error('Session verification failed:', error)
    }

    // Invalid session - clear it
    logout()
    return false
  }

  function getAuthHeaders(): Record<string, string> {
    if (sessionToken.value) {
      return { 'Authorization': `Bearer ${sessionToken.value}` }
    }
    return {}
  }

  function canModifyBooking(partyId: number): boolean {
    if (!currentUser.value) return false
    if (currentUser.value.is_admin) return true
    return currentUser.value.party_id === partyId
  }

  return {
    // State
    currentUser,
    sessionToken,

    // Computed
    isAuthenticated,
    isAdmin,

    // Methods
    login,
    logout,
    verifySession,
    getAuthHeaders,
    canModifyBooking
  }
}
