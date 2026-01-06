// User & Authentication
export interface User {
  party_id: number | null
  is_admin: boolean
  username: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
  message: string
}

// Party
export interface Party {
  id: number
  name: string
  color: string
}

// Booking
export interface Booking {
  id: number
  party_id: number
  party_name: string
  party_color: string
  start_date: string
  end_date: string
  note: string | null
}

export interface BookingCreate {
  party_id: number
  start_date: string
  end_date: string
  note?: string | null
}

// API Response
export interface MessageResponse {
  message: string
}

// Toast
export type ToastType = 'success' | 'error' | 'info'

export interface Toast {
  id: number
  type: ToastType
  message: string
}

// Calendar
export type BookingPosition = 'start' | 'middle' | 'end' | 'single'

export interface DayBooking {
  id: number
  color: string
  partyName: string
  position: BookingPosition
}

export interface CalendarDay {
  date: string
  dayNumber: number
  isCurrentMonth: boolean
  isToday: boolean
  bookings: DayBooking[]
}
