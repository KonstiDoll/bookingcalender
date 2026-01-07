<script setup lang="ts">
import { ref, onMounted, type Ref } from 'vue'
import { useApi } from './composables/useApi'
import { useAuth } from './composables/useAuth'
import { useToast } from './composables/useToast'
import type { Booking } from './types'
import LoginView from './components/LoginView.vue'
import FamilyLegend from './components/FamilyLegend.vue'
import CalendarView from './components/CalendarView.vue'
import BookingForm from './components/BookingForm.vue'
import BookingList from './components/BookingList.vue'
import ToastContainer from './components/ToastContainer.vue'

const { loadParties, loadBookings } = useApi()
const { isAuthenticated, currentUser, isAdmin, verifySession, logout } = useAuth()
const { error } = useToast()

const selectionStart: Ref<string> = ref('')
const selectionEnd: Ref<string> = ref('')
const initializing: Ref<boolean> = ref(true)
const editingBooking: Ref<Booking | null> = ref(null)

function handleDayClick(date: string): void {
  if (!selectionStart.value) {
    // First click - set start date
    selectionStart.value = date
    selectionEnd.value = ''
  } else if (!selectionEnd.value && date >= selectionStart.value) {
    // Second click - set end date (must be >= start)
    selectionEnd.value = date
  } else {
    // Reset and start new selection
    selectionStart.value = date
    selectionEnd.value = ''
  }
}

function handleSelectionChange(start: string, end: string): void {
  selectionStart.value = start
  selectionEnd.value = end
}

function handleBookingSaved(): void {
  selectionStart.value = ''
  selectionEnd.value = ''
  editingBooking.value = null
}

function handleEditBooking(booking: Booking): void {
  editingBooking.value = booking
}

function handleEditCancelled(): void {
  editingBooking.value = null
  selectionStart.value = ''
  selectionEnd.value = ''
}

async function loadInitialData(): Promise<void> {
  try {
    await Promise.all([loadParties(), loadBookings()])
  } catch (err) {
    error('Fehler beim Laden der Daten')
    // If unauthorized, logout
    if (err instanceof Error && err.message?.includes('401')) {
      logout()
    }
  }
}

async function handleLoginSuccess(): Promise<void> {
  await loadInitialData()
}

function handleLogout(): void {
  logout()
  selectionStart.value = ''
  selectionEnd.value = ''
}

onMounted(async () => {
  // Check for existing session
  const sessionValid = await verifySession()

  if (sessionValid) {
    await loadInitialData()
  }

  initializing.value = false
})
</script>

<template>
  <!-- Loading State -->
  <div v-if="initializing" class="min-h-screen flex items-center justify-center">
    <div class="text-text-secondary">Laden...</div>
  </div>

  <!-- Login View -->
  <LoginView
    v-else-if="!isAuthenticated"
    @login-success="handleLoginSuccess"
  />

  <!-- Main App -->
  <div v-else class="min-h-screen p-4 lg:p-6 max-w-7xl mx-auto relative z-10">
    <!-- Header -->
    <header class="text-center mb-12 pt-8 relative">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-15 h-1 bg-gradient-to-r from-family-1 to-family-3 rounded-full" />
      <h1 class="font-display text-4xl lg:text-5xl font-normal tracking-tight text-text-primary mb-2">
        Ferienhaus <span class="italic font-light">Kalender</span>
      </h1>
      <div class="flex items-center justify-center gap-4 mt-2">
        <p class="text-text-secondary font-light">
          Angemeldet als: <span class="font-medium text-text-primary">{{ currentUser?.username }}</span>
          <span v-if="isAdmin" class="text-family-1 font-semibold ml-1">(Admin)</span>
        </p>
        <button
          @click="handleLogout"
          class="text-sm text-text-secondary hover:text-text-primary underline transition-colors"
        >
          Abmelden
        </button>
      </div>
    </header>

    <!-- Family Legend -->
    <FamilyLegend />

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
      <!-- Calendar -->
      <CalendarView
        :selection-start="selectionStart"
        :selection-end="selectionEnd"
        @day-click="handleDayClick"
      />

      <!-- Sidebar -->
      <aside class="flex flex-col gap-6">
        <BookingForm
          :selection-start="selectionStart"
          :selection-end="selectionEnd"
          :editing-booking="editingBooking"
          @saved="handleBookingSaved"
          @cancelled="handleEditCancelled"
          @selection-change="handleSelectionChange"
        />
        <BookingList @edit="handleEditBooking" />
      </aside>
    </div>

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>
