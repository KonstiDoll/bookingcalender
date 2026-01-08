<script setup lang="ts">
import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { useApi } from '../composables/useApi'
import type { Booking } from '../types'

const { bookings } = useApi()

const currentYear: Ref<number> = ref(new Date().getFullYear())

const monthNames: readonly string[] = [
  'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
]

const weekdays: readonly string[] = ['M', 'D', 'M', 'D', 'F', 'S', 'S']

interface MiniDay {
  date: string
  dayNumber: number
  isCurrentMonth: boolean
  isToday: boolean
  booking: Booking | null
}

interface MonthData {
  name: string
  days: MiniDay[]
}

const yearData: ComputedRef<MonthData[]> = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayStr = formatDateISO(today)

  return monthNames.map((name, monthIndex) => {
    const firstDay = new Date(currentYear.value, monthIndex, 1)
    const lastDay = new Date(currentYear.value, monthIndex + 1, 0)

    let startOffset = firstDay.getDay() - 1
    if (startOffset < 0) startOffset = 6

    const days: MiniDay[] = []

    // Previous month days (empty placeholders)
    for (let i = 0; i < startOffset; i++) {
      const date = new Date(currentYear.value, monthIndex, -startOffset + i + 1)
      days.push({
        date: formatDateISO(date),
        dayNumber: date.getDate(),
        isCurrentMonth: false,
        isToday: false,
        booking: null
      })
    }

    // Current month days
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(currentYear.value, monthIndex, i)
      const dateStr = formatDateISO(date)
      days.push({
        date: dateStr,
        dayNumber: i,
        isCurrentMonth: true,
        isToday: dateStr === todayStr,
        booking: getBookingForDate(dateStr)
      })
    }

    // Fill remaining days to complete 6 rows (42 cells)
    const remaining = 42 - days.length
    for (let i = 1; i <= remaining; i++) {
      const date = new Date(currentYear.value, monthIndex + 1, i)
      days.push({
        date: formatDateISO(date),
        dayNumber: i,
        isCurrentMonth: false,
        isToday: false,
        booking: null
      })
    }

    return { name, days }
  })
})

function formatDateISO(date: Date): string {
  return date.toISOString().split('T')[0]
}

function getBookingForDate(dateStr: string): Booking | null {
  return bookings.value.find(b => dateStr >= b.start_date && dateStr <= b.end_date) || null
}

function previousYear(): void {
  currentYear.value--
}

function nextYear(): void {
  currentYear.value++
}

function goToCurrentYear(): void {
  currentYear.value = new Date().getFullYear()
}
</script>

<template>
  <section class="card">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 pb-4 border-b border-black/5">
      <div class="flex gap-2">
        <button
          class="w-11 h-11 rounded-xl border border-black/15 bg-white flex items-center justify-center transition-all hover:bg-bg-cream hover:border-text-tertiary text-text-secondary hover:text-text-primary"
          @click="previousYear"
          aria-label="Vorheriges Jahr"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <button
          class="w-11 h-11 rounded-xl border border-black/15 bg-white flex items-center justify-center transition-all hover:bg-bg-cream hover:border-text-tertiary text-text-secondary hover:text-text-primary"
          @click="nextYear"
          aria-label="Nächstes Jahr"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>

      <h2 class="font-display text-2xl font-medium text-text-primary">
        {{ currentYear }}
      </h2>

      <button
        class="px-4 py-2 rounded-lg border border-black/15 bg-white text-sm font-medium text-text-secondary transition-all hover:bg-bg-cream hover:text-text-primary"
        @click="goToCurrentYear"
      >
        Aktuelles Jahr
      </button>
    </div>

    <!-- Year Grid - 4 columns x 3 rows -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <div
        v-for="month in yearData"
        :key="month.name"
        class="bg-bg-warm rounded-xl p-3"
      >
        <!-- Month Name -->
        <h3 class="text-sm font-semibold text-text-primary mb-2 text-center">
          {{ month.name }}
        </h3>

        <!-- Weekday Headers -->
        <div class="grid grid-cols-7 gap-px mb-1">
          <div
            v-for="day in weekdays"
            :key="day"
            class="text-center text-[10px] font-medium text-text-tertiary"
          >
            {{ day }}
          </div>
        </div>

        <!-- Days Grid -->
        <div class="grid grid-cols-7 gap-px">
          <div
            v-for="(day, index) in month.days"
            :key="index"
            class="aspect-square flex items-center justify-center text-[10px] rounded-sm transition-colors"
            :class="{
              'text-text-tertiary/30': !day.isCurrentMonth,
              'text-text-primary': day.isCurrentMonth && !day.booking && !day.isToday,
              'bg-white ring-1 ring-family-1 text-family-1 font-bold': day.isToday && !day.booking,
              'text-white font-medium': day.booking
            }"
            :style="day.booking ? { backgroundColor: day.booking.party_color } : {}"
            :title="day.booking ? `${day.booking.party_name}: ${day.booking.start_date} - ${day.booking.end_date}${day.booking.note ? ' (' + day.booking.note + ')' : ''}` : ''"
          >
            <span v-if="day.isCurrentMonth">{{ day.dayNumber }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
