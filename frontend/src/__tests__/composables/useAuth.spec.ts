import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuth } from '../../composables/useAuth'

// Mock localStorage
const localStorageMock = {
  store: {} as Record<string, string>,
  getItem: vi.fn((key: string) => localStorageMock.store[key] || null),
  setItem: vi.fn((key: string, value: string) => {
    localStorageMock.store[key] = value
  }),
  removeItem: vi.fn((key: string) => {
    delete localStorageMock.store[key]
  }),
  clear: vi.fn(() => {
    localStorageMock.store = {}
  })
}

Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
  writable: true
})

// Mock fetch
const mockFetch = vi.fn()
globalThis.fetch = mockFetch

describe('useAuth', () => {
  beforeEach(() => {
    localStorageMock.clear()
    mockFetch.mockClear()

    // Reset auth state by getting fresh composable
    const { logout } = useAuth()
    logout()
  })

  describe('initial state', () => {
    it('should have null currentUser initially', () => {
      const { currentUser } = useAuth()
      expect(currentUser.value).toBeNull()
    })

    it('should not be authenticated initially', () => {
      const { isAuthenticated } = useAuth()
      expect(isAuthenticated.value).toBe(false)
    })

    it('should not be admin initially', () => {
      const { isAdmin } = useAuth()
      expect(isAdmin.value).toBe(false)
    })
  })

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        token: 'test-token',
        user: {
          party_id: 1,
          is_admin: false,
          username: 'Test User'
        },
        message: 'Success'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const { login, currentUser, isAuthenticated, sessionToken } = useAuth()

      await login('Test User', 'password')

      expect(currentUser.value).toEqual(mockResponse.user)
      expect(isAuthenticated.value).toBe(true)
      expect(sessionToken.value).toBe('test-token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('session_token', 'test-token')
    })

    it('should throw error on failed login', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Invalid credentials' })
      })

      const { login } = useAuth()

      await expect(login('Wrong', 'credentials')).rejects.toThrow('Invalid credentials')
    })
  })

  describe('logout', () => {
    it('should clear user data on logout', async () => {
      // First login
      const mockResponse = {
        token: 'test-token',
        user: { party_id: 1, is_admin: false, username: 'Test' },
        message: 'Success'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const { login, logout, currentUser, sessionToken, isAuthenticated } = useAuth()

      await login('Test', 'password')
      expect(isAuthenticated.value).toBe(true)

      logout()

      expect(currentUser.value).toBeNull()
      expect(sessionToken.value).toBeNull()
      expect(isAuthenticated.value).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('session_token')
    })
  })

  describe('getAuthHeaders', () => {
    it('should return empty object when not authenticated', () => {
      const { getAuthHeaders, logout } = useAuth()
      logout()

      const headers = getAuthHeaders()
      expect(headers).toEqual({})
    })

    it('should return auth header when authenticated', async () => {
      const mockResponse = {
        token: 'test-token',
        user: { party_id: 1, is_admin: false, username: 'Test' },
        message: 'Success'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const { login, getAuthHeaders } = useAuth()
      await login('Test', 'password')

      const headers = getAuthHeaders()
      expect(headers).toEqual({ Authorization: 'Bearer test-token' })
    })
  })

  describe('canModifyBooking', () => {
    it('should return false when not authenticated', () => {
      const { canModifyBooking, logout } = useAuth()
      logout()

      expect(canModifyBooking(1)).toBe(false)
    })

    it('should return true for admin', async () => {
      const mockResponse = {
        token: 'admin-token',
        user: { party_id: null, is_admin: true, username: 'Admin' },
        message: 'Success'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const { login, canModifyBooking } = useAuth()
      await login('Admin', 'password')

      expect(canModifyBooking(1)).toBe(true)
      expect(canModifyBooking(2)).toBe(true)
      expect(canModifyBooking(3)).toBe(true)
    })

    it('should return true only for own party', async () => {
      const mockResponse = {
        token: 'user-token',
        user: { party_id: 1, is_admin: false, username: 'Test' },
        message: 'Success'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const { login, canModifyBooking } = useAuth()
      await login('Test', 'password')

      expect(canModifyBooking(1)).toBe(true)
      expect(canModifyBooking(2)).toBe(false)
    })
  })
})
