<script setup lang="ts">
import { ref, watch, computed, onMounted, type Ref } from 'vue'
import { useApi } from '../composables/useApi'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'
import type { Booking } from '../types'

interface BookingFormData {
  partyId: number | ''
  startDate: string
  endDate: string
  note: string
}

const props = withDefaults(defineProps<{
  selectionStart?: string
  selectionEnd?: string
  editingBooking?: Booking | null
}>(), {
  selectionStart: '',
  selectionEnd: '',
  editingBooking: null
})

const emit = defineEmits<{
  saved: []
  cancelled: []
  selectionChange: [start: string, end: string]
}>()

const { parties, createBooking, updateBooking } = useApi()
const { currentUser, isAdmin } = useAuth()
const { success, error } = useToast()

const editingId: Ref<number | null> = ref(null)

const form: Ref<BookingFormData> = ref({
  partyId: '',
  startDate: '',
  endDate: '',
  note: ''
})

const isEditing = computed(() => editingId.value !== null)

// Filter parties based on user permissions
const availableParties = computed(() => {
  if (isAdmin.value) {
    return parties.value
  }
  // Non-admin users can only select their own party
  return parties.value.filter(p => p.id === currentUser.value?.party_id)
})

// Pre-select party for non-admin users
onMounted(() => {
  if (!isAdmin.value && currentUser.value?.party_id) {
    form.value.partyId = currentUser.value.party_id
  }
})

// Watch for editing booking changes
watch(() => props.editingBooking, (booking: Booking | null | undefined) => {
  if (booking) {
    editingId.value = booking.id
    form.value = {
      partyId: booking.party_id,
      startDate: booking.start_date,
      endDate: booking.end_date,
      note: booking.note || ''
    }
    emit('selectionChange', booking.start_date, booking.end_date)
  } else {
    // Reset when editingBooking becomes null
    editingId.value = null
  }
}, { immediate: true })

watch(() => props.selectionStart, (newVal: string) => {
  if (newVal) {
    form.value.startDate = newVal
  }
})

watch(() => props.selectionEnd, (newVal: string) => {
  if (newVal) {
    form.value.endDate = newVal
  }
})

// Emit changes when form dates change
function onStartDateChange(e: Event): void {
  const target = e.target as HTMLInputElement
  form.value.startDate = target.value
  emit('selectionChange', form.value.startDate, form.value.endDate)
}

function onEndDateChange(e: Event): void {
  const target = e.target as HTMLInputElement
  form.value.endDate = target.value
  emit('selectionChange', form.value.startDate, form.value.endDate)
}

function resetForm(): void {
  editingId.value = null
  const keepPartyId = !isAdmin.value && currentUser.value?.party_id ? currentUser.value.party_id : ''
  form.value = { partyId: keepPartyId, startDate: '', endDate: '', note: '' }
}

function handleCancel(): void {
  resetForm()
  emit('cancelled')
}

async function handleSubmit(): Promise<void> {
  if (!form.value.partyId || !form.value.startDate || !form.value.endDate) {
    error('Bitte alle Pflichtfelder ausfüllen')
    return
  }

  if (form.value.endDate < form.value.startDate) {
    error('Enddatum muss nach Startdatum liegen')
    return
  }

  const bookingData = {
    party_id: form.value.partyId as number,
    start_date: form.value.startDate,
    end_date: form.value.endDate,
    note: form.value.note || null
  }

  try {
    if (isEditing.value && editingId.value) {
      await updateBooking(editingId.value, bookingData)
      success('Buchung erfolgreich aktualisiert')
    } else {
      await createBooking(bookingData)
      success('Buchung erfolgreich gespeichert')
    }

    resetForm()
    emit('saved')
  } catch (err) {
    error(err instanceof Error ? err.message : 'Fehler beim Speichern')
  }
}
</script>

<template>
  <div class="card">
    <h3 class="font-display text-xl font-medium text-text-primary mb-6 flex items-center gap-2">
      <svg v-if="isEditing" class="w-6 h-6 text-family-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
      </svg>
      <svg v-else class="w-6 h-6 text-family-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
      </svg>
      {{ isEditing ? 'Buchung bearbeiten' : 'Neue Buchung' }}
    </h3>

    <form @submit.prevent="handleSubmit">
      <!-- Familie-Auswahl nur für Admin -->
      <div v-if="isAdmin" class="mb-4">
        <label class="form-label">Familie</label>
        <select
          v-model="form.partyId"
          class="form-input"
          required
        >
          <option value="">Familie auswählen...</option>
          <option v-for="party in availableParties" :key="party.id" :value="party.id">
            {{ party.name }}
          </option>
        </select>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="form-label">Von</label>
          <input
            type="date"
            :value="form.startDate"
            @input="onStartDateChange"
            class="form-input"
            required
          />
        </div>
        <div>
          <label class="form-label">Bis</label>
          <input
            type="date"
            :value="form.endDate"
            @input="onEndDateChange"
            class="form-input"
            required
          />
        </div>
      </div>

      <div class="mb-4">
        <label class="form-label">Notiz (optional)</label>
        <textarea
          v-model="form.note"
          class="form-input min-h-20 resize-y"
          placeholder="z.B. Familienurlaub, Geburtstag..."
        />
      </div>

      <div class="flex gap-2">
        <button type="submit" class="btn-primary flex-1">
          {{ isEditing ? 'Änderungen speichern' : 'Buchung speichern' }}
        </button>
        <button
          v-if="isEditing"
          type="button"
          @click="handleCancel"
          class="px-4 py-2 rounded-lg border border-black/15 bg-white text-text-secondary hover:bg-bg-cream transition-colors"
        >
          Abbrechen
        </button>
      </div>
    </form>
  </div>
</template>
