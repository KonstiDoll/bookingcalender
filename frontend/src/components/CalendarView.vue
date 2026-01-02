<script setup>
import { useCalendar } from '../composables/useCalendar'

const emit = defineEmits(['dayClick'])

const {
  weekdays,
  monthYearDisplay,
  calendarDays,
  previousMonth,
  nextMonth,
  goToToday
} = useCalendar()
</script>

<template>
  <section class="card">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 pb-4 border-b border-black/5">
      <div class="flex gap-2">
        <button
          class="w-11 h-11 rounded-xl border border-black/15 bg-white flex items-center justify-center transition-all hover:bg-bg-cream hover:border-text-tertiary text-text-secondary hover:text-text-primary"
          @click="previousMonth"
          aria-label="Vorheriger Monat"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <button
          class="w-11 h-11 rounded-xl border border-black/15 bg-white flex items-center justify-center transition-all hover:bg-bg-cream hover:border-text-tertiary text-text-secondary hover:text-text-primary"
          @click="nextMonth"
          aria-label="Nächster Monat"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>

      <h2 class="font-display text-2xl font-medium text-text-primary">
        {{ monthYearDisplay }}
      </h2>

      <button
        class="px-4 py-2 rounded-lg border border-black/15 bg-white text-sm font-medium text-text-secondary transition-all hover:bg-bg-cream hover:text-text-primary"
        @click="goToToday"
      >
        Heute
      </button>
    </div>

    <!-- Weekdays -->
    <div class="grid grid-cols-7 gap-0.5 mb-2">
      <div
        v-for="day in weekdays"
        :key="day"
        class="p-2 text-center text-xs font-semibold uppercase tracking-widest text-text-tertiary"
      >
        {{ day }}
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="grid grid-cols-7 gap-0.5 bg-black/5 rounded-xl overflow-hidden">
      <div
        v-for="(day, index) in calendarDays"
        :key="index"
        class="aspect-square bg-white p-1 cursor-pointer transition-colors hover:bg-bg-cream min-h-20 flex flex-col"
        :class="{
          'bg-bg-warm': !day.isCurrentMonth,
          'bg-gradient-to-br from-family-1/10 to-family-1/5': day.isToday
        }"
        @click="emit('dayClick', day.date)"
      >
        <span
          class="text-sm font-medium mb-1"
          :class="{
            'text-text-tertiary/50': !day.isCurrentMonth,
            'bg-family-1 text-white w-7 h-7 rounded-full flex items-center justify-center': day.isToday,
            'text-text-primary': day.isCurrentMonth && !day.isToday
          }"
        >
          {{ day.dayNumber }}
        </span>

        <div class="flex-1 flex flex-col gap-0.5 overflow-hidden">
          <div
            v-for="booking in day.bookings"
            :key="booking.id"
            class="h-1.5 rounded-sm opacity-90"
            :class="{
              'ml-0.5 rounded-l-sm': booking.position === 'start',
              'mr-0.5 rounded-r-sm': booking.position === 'end',
              'rounded-none': booking.position === 'middle',
              'mx-0.5': booking.position === 'single'
            }"
            :style="{ backgroundColor: booking.color }"
            :title="booking.partyName"
          />
        </div>
      </div>
    </div>
  </section>
</template>
