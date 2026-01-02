import { ref, computed } from 'vue'

const API_BASE = '/api'

// Reactive state - shared across all components
const currentUser = ref(null)
const sessionToken = ref(localStorage.getItem('session_token'))

// Computed properties
const isAuthenticated = computed(() => !!currentUser.value)
const isAdmin = computed(() => currentUser.value?.is_admin || false)

export function useAuth() {
  /**
   * Login with username and password
   * @param {string} username - Party name or "Admin"
   * @param {string} password - User password
   * @returns {Promise<object>} Login response with token and user info
   */
  async function login(username, password) {
    console.log('useAuth.login called', { username })

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    console.log('Response status:', response.status)

    if (!response.ok) {
      const error = await response.json()
      console.error('Login failed:', error)
      throw new Error(error.detail || 'Login fehlgeschlagen')
    }

    const data = await response.json()
    console.log('Login response:', data)

    // Store token and user info
    sessionToken.value = data.token
    currentUser.value = data.user
    localStorage.setItem('session_token', data.token)

    return data
  }

  /**
   * Logout - clear session
   */
  function logout() {
    sessionToken.value = null
    currentUser.value = null
    localStorage.removeItem('session_token')
  }

  /**
   * Verify existing session on app load
   * @returns {Promise<boolean>} True if session is valid
   */
  async function verifySession() {
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

  /**
   * Get authorization headers for API calls
   * @returns {object} Headers object with Authorization if logged in
   */
  function getAuthHeaders() {
    if (sessionToken.value) {
      return { 'Authorization': `Bearer ${sessionToken.value}` }
    }
    return {}
  }

  /**
   * Check if current user can modify bookings for a party
   * @param {number} partyId - Party ID to check
   * @returns {boolean} True if user can modify
   */
  function canModifyBooking(partyId) {
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
