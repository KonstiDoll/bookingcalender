<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from './composables/useApi'
import { useToast } from './composables/useToast'
import FamilyLegend from './components/FamilyLegend.vue'
import CalendarView from './components/CalendarView.vue'
import BookingForm from './components/BookingForm.vue'
import BookingList from './components/BookingList.vue'
import ToastContainer from './components/ToastContainer.vue'

const { loadParties, loadBookings } = useApi()
const { error } = useToast()

const selectedParty = ref(null)
const selectedDate = ref('')

function handlePartySelect(partyId) {
  selectedParty.value = partyId
}

function handleDayClick(date) {
  selectedDate.value = date
}

function handleBookingSaved() {
  selectedDate.value = ''
}

onMounted(async () => {
  try {
    await Promise.all([loadParties(), loadBookings()])
  } catch (err) {
    error('Fehler beim Laden der Daten')
  }
})
</script>

<template>
  <div class="min-h-screen p-4 lg:p-6 max-w-7xl mx-auto relative z-10">
    <!-- Header -->
    <header class="text-center mb-12 pt-8 relative">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-15 h-1 bg-gradient-to-r from-family-1 to-family-3 rounded-full" />
      <h1 class="font-display text-4xl lg:text-5xl font-normal tracking-tight text-text-primary mb-2">
        Ferienhaus <span class="italic font-light">Kalender</span>
      </h1>
      <p class="text-lg text-text-secondary font-light">
        Buchungsübersicht für unsere Familien
      </p>
    </header>

    <!-- Family Legend -->
    <FamilyLegend
      :selected-party="selectedParty"
      @select="handlePartySelect"
    />

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
      <!-- Calendar -->
      <CalendarView @day-click="handleDayClick" />

      <!-- Sidebar -->
      <aside class="flex flex-col gap-6">
        <BookingForm
          :selected-party="selectedParty"
          :selected-date="selectedDate"
          @saved="handleBookingSaved"
          @party-select="handlePartySelect"
        />
        <BookingList />
      </aside>
    </div>

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>
