import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useToast } from '../../composables/useToast'

describe('useToast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // Clear toasts
    const { toasts } = useToast()
    toasts.value = []
  })

  describe('showToast', () => {
    it('should add toast to list', () => {
      const { showToast, toasts } = useToast()

      showToast('Test message', 'success')

      expect(toasts.value).toHaveLength(1)
      expect(toasts.value[0].message).toBe('Test message')
      expect(toasts.value[0].type).toBe('success')
    })

    it('should default to success type', () => {
      const { showToast, toasts } = useToast()

      showToast('Test message')

      expect(toasts.value[0].type).toBe('success')
    })

    it('should remove toast after 3 seconds', () => {
      const { showToast, toasts } = useToast()

      showToast('Test message')
      expect(toasts.value).toHaveLength(1)

      vi.advanceTimersByTime(3000)

      expect(toasts.value).toHaveLength(0)
    })

    it('should assign unique IDs to toasts', () => {
      const { showToast, toasts } = useToast()

      showToast('Message 1')
      vi.advanceTimersByTime(1) // Advance time to ensure different timestamp
      showToast('Message 2')

      expect(toasts.value[0].id).not.toBe(toasts.value[1].id)
    })
  })

  describe('success', () => {
    it('should create success toast', () => {
      const { success, toasts } = useToast()

      success('Success message')

      expect(toasts.value[0].type).toBe('success')
      expect(toasts.value[0].message).toBe('Success message')
    })
  })

  describe('error', () => {
    it('should create error toast', () => {
      const { error, toasts } = useToast()

      error('Error message')

      expect(toasts.value[0].type).toBe('error')
      expect(toasts.value[0].message).toBe('Error message')
    })
  })
})
