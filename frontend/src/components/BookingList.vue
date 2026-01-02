<script setup>
import { computed } from 'vue'
import { bookings, useApi } from '../composables/useApi'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'

const { deleteBooking } = useApi()
const { canModifyBooking } = useAuth()
const { success, error } = useToast()

const sortedBookings = computed(() => {
  return [...bookings.value].sort((a, b) =>
    new Date(a.start_date) - new Date(b.start_date)
  )
})

function formatDateRange(start, end) {
  const startDate = new Date(start)
  const endDate = new Date(end)
  const options = { day: 'numeric', month: 'short' }

  if (start === end) {
    return startDate.toLocaleDateString('de-DE', { ...options, year: 'numeric' })
  }

  const startFormatted = startDate.toLocaleDateString('de-DE', options)
  const endFormatted = endDate.toLocaleDateString('de-DE', { ...options, year: 'numeric' })
  return `${startFormatted} – ${endFormatted}`
}

async function handleDelete(id) {
  if (!confirm('Buchung wirklich löschen?')) return

  try {
    await deleteBooking(id)
    success('Buchung gelöscht')
  } catch (err) {
    error(err.message)
  }
}
</script>

<template>
  <div class="card max-h-96 overflow-y-auto">
    <h3 class="font-display text-xl font-medium text-text-primary mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-family-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
      Buchungen
    </h3>

    <!-- Empty State -->
    <div v-if="sortedBookings.length === 0" class="text-center py-8 text-text-tertiary">
      <svg class="w-12 h-12 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <p>Noch keine Buchungen vorhanden</p>
    </div>

    <!-- Bookings List -->
    <div v-else class="flex flex-col gap-4">
      <div
        v-for="booking in sortedBookings"
        :key="booking.id"
        class="flex items-start gap-4 p-4 rounded-xl bg-bg-cream transition-colors hover:bg-bg-warm"
      >
        <div
          class="w-1 min-h-12 rounded-sm shrink-0"
          :style="{ backgroundColor: booking.party_color }"
        />

        <div class="flex-1 min-w-0">
          <div class="font-semibold text-text-primary mb-1">
            {{ booking.party_name }}
          </div>
          <div class="text-sm text-text-secondary flex items-center gap-1">
            <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            {{ formatDateRange(booking.start_date, booking.end_date) }}
          </div>
          <div v-if="booking.note" class="text-xs text-text-tertiary italic mt-1">
            {{ booking.note }}
          </div>
        </div>

        <button
          v-if="canModifyBooking(booking.party_id)"
          class="w-8 h-8 rounded-lg flex items-center justify-center text-text-tertiary transition-colors hover:bg-red-100 hover:text-red-600 shrink-0"
          @click="handleDelete(booking.id)"
          title="Löschen"
        >
          <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
