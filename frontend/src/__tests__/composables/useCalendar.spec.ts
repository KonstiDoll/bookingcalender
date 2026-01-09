import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'

// Create the bookings ref
const bookings = ref([])

// Mock the useApi composable
vi.mock('../../composables/useApi', () => ({
  useApi: () => ({
    bookings,
    loadParties: vi.fn(),
    loadBookings: vi.fn(),
    createBooking: vi.fn(),
    updateBooking: vi.fn(),
    deleteBooking: vi.fn()
  })
}))

import { useCalendar } from '../../composables/useCalendar'

describe('useCalendar', () => {
  beforeEach(() => {
    bookings.value = []
  })

  describe('weekdays', () => {
    it('should have 7 days starting with Monday', () => {
      const { weekdays } = useCalendar()

      expect(weekdays).toHaveLength(7)
      expect(weekdays[0]).toBe('Mo')
      expect(weekdays[6]).toBe('So')
    })
  })

  describe('monthYearDisplay', () => {
    it('should format current month and year in German', () => {
      const { monthYearDisplay, currentDate } = useCalendar()

      // Set to a known date
      currentDate.value = new Date(2024, 0, 15) // January 2024

      expect(monthYearDisplay.value).toBe('Januar 2024')
    })

    it('should update when month changes', () => {
      const { monthYearDisplay, currentDate } = useCalendar()

      currentDate.value = new Date(2024, 5, 1) // June 2024
      expect(monthYearDisplay.value).toBe('Juni 2024')

      currentDate.value = new Date(2024, 11, 1) // December 2024
      expect(monthYearDisplay.value).toBe('Dezember 2024')
    })
  })

  describe('calendarDays', () => {
    it('should return 42 days (6 weeks)', () => {
      const { calendarDays } = useCalendar()

      expect(calendarDays.value).toHaveLength(42)
    })

    it('should mark today correctly', () => {
      const { calendarDays, currentDate } = useCalendar()
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      currentDate.value = new Date(today.getFullYear(), today.getMonth(), 1)

      const todayString = today.toISOString().split('T')[0]
      const todayDay = calendarDays.value.find(d => d.date === todayString)

      // Today should be marked if it's in the current view
      if (todayDay) {
        expect(todayDay.isToday).toBe(true)
      }
    })

    it('should include days from previous month', () => {
      const { calendarDays, currentDate } = useCalendar()

      // Set to a month that doesn't start on Monday
      currentDate.value = new Date(2024, 2, 1) // March 2024 (starts on Friday)

      // First days should be from February
      const firstDays = calendarDays.value.slice(0, 4)
      expect(firstDays.every(d => !d.isCurrentMonth)).toBe(true)
    })

    it('should include bookings for each day', () => {
      const { calendarDays, currentDate } = useCalendar()
      currentDate.value = new Date(2024, 0, 15)

      // Add a booking
      bookings.value = [{
        id: 1,
        party_id: 1,
        party_name: 'Test Party',
        party_color: '#ff0000',
        start_date: '2024-01-10',
        end_date: '2024-01-12',
        note: null
      }]

      const jan10 = calendarDays.value.find(d => d.date === '2024-01-10')
      const jan11 = calendarDays.value.find(d => d.date === '2024-01-11')
      const jan12 = calendarDays.value.find(d => d.date === '2024-01-12')
      const jan13 = calendarDays.value.find(d => d.date === '2024-01-13')

      expect(jan10?.bookings).toHaveLength(1)
      expect(jan10?.bookings[0].position).toBe('start')
      expect(jan11?.bookings[0].position).toBe('middle')
      expect(jan12?.bookings[0].position).toBe('end')
      expect(jan13?.bookings).toHaveLength(0)
    })

    it('should mark single-day bookings correctly', () => {
      const { calendarDays, currentDate } = useCalendar()
      currentDate.value = new Date(2024, 0, 15)

      bookings.value = [{
        id: 1,
        party_id: 1,
        party_name: 'Test Party',
        party_color: '#ff0000',
        start_date: '2024-01-15',
        end_date: '2024-01-15',
        note: null
      }]

      const jan15 = calendarDays.value.find(d => d.date === '2024-01-15')

      expect(jan15?.bookings[0].position).toBe('single')
    })
  })

  describe('navigation', () => {
    it('should go to previous month', () => {
      const { currentDate, previousMonth, monthYearDisplay } = useCalendar()

      currentDate.value = new Date(2024, 5, 15) // June 2024
      previousMonth()

      expect(monthYearDisplay.value).toBe('Mai 2024')
    })

    it('should go to next month', () => {
      const { currentDate, nextMonth, monthYearDisplay } = useCalendar()

      currentDate.value = new Date(2024, 5, 15) // June 2024
      nextMonth()

      expect(monthYearDisplay.value).toBe('Juli 2024')
    })

    it('should handle year transitions', () => {
      const { currentDate, previousMonth, nextMonth, monthYearDisplay } = useCalendar()

      currentDate.value = new Date(2024, 0, 15) // January 2024
      previousMonth()
      expect(monthYearDisplay.value).toBe('Dezember 2023')

      nextMonth()
      nextMonth()
      expect(monthYearDisplay.value).toBe('Februar 2024')
    })

    it('should go to today', () => {
      const { currentDate, goToToday } = useCalendar()

      currentDate.value = new Date(2020, 0, 1) // Far in the past
      goToToday()

      const today = new Date()
      expect(currentDate.value.getMonth()).toBe(today.getMonth())
      expect(currentDate.value.getFullYear()).toBe(today.getFullYear())
    })
  })
})
