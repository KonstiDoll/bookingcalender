import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { useApi } from './useApi'
import type { CalendarDay, DayBooking, BookingPosition } from '../types'

const currentDate: Ref<Date> = ref(new Date())

const weekdays: readonly string[] = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

const monthNames: readonly string[] = [
  'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
]

export function useCalendar() {
  const { bookings } = useApi()
  const monthYearDisplay: ComputedRef<string> = computed(() => {
    const month = monthNames[currentDate.value.getMonth()]
    const year = currentDate.value.getFullYear()
    return `${month} ${year}`
  })

  const calendarDays: ComputedRef<CalendarDay[]> = computed(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()

    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)

    let startOffset = firstDay.getDay() - 1
    if (startOffset < 0) startOffset = 6

    const days: CalendarDay[] = []
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    // Previous month days
    for (let i = startOffset - 1; i >= 0; i--) {
      const date = new Date(year, month, -i)
      days.push(createDayObject(date, false, today))
    }

    // Current month days
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(year, month, i)
      days.push(createDayObject(date, true, today))
    }

    // Next month days
    const remaining = 42 - days.length
    for (let i = 1; i <= remaining; i++) {
      const date = new Date(year, month + 1, i)
      days.push(createDayObject(date, false, today))
    }

    return days
  })

  function createDayObject(date: Date, isCurrentMonth: boolean, today: Date): CalendarDay {
    const dateStr = formatDateISO(date)
    const dayBookings = getBookingsForDate(dateStr)

    return {
      date: dateStr,
      dayNumber: date.getDate(),
      isCurrentMonth,
      isToday: date.getTime() === today.getTime(),
      bookings: dayBookings
    }
  }

  function getBookingsForDate(dateStr: string): DayBooking[] {
    return bookings.value
      .filter(b => dateStr >= b.start_date && dateStr <= b.end_date)
      .map(b => {
        let position: BookingPosition = 'middle'
        if (b.start_date === dateStr && b.end_date === dateStr) {
          position = 'single'
        } else if (b.start_date === dateStr) {
          position = 'start'
        } else if (b.end_date === dateStr) {
          position = 'end'
        }

        return {
          id: b.id,
          color: b.party_color,
          partyName: b.party_name,
          position
        }
      })
  }

  function formatDateISO(date: Date): string {
    return date.toISOString().split('T')[0]
  }

  function previousMonth(): void {
    currentDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth() - 1,
      1
    )
  }

  function nextMonth(): void {
    currentDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth() + 1,
      1
    )
  }

  function goToToday(): void {
    currentDate.value = new Date()
  }

  return {
    currentDate,
    weekdays,
    monthYearDisplay,
    calendarDays,
    previousMonth,
    nextMonth,
    goToToday
  }
}
