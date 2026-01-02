<script setup>
import { ref, watch } from 'vue'
import { parties, useApi } from '../composables/useApi'
import { useToast } from '../composables/useToast'

const props = defineProps({
  selectedParty: {
    type: Number,
    default: null
  },
  selectedDate: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['saved', 'partySelect'])

const { createBooking } = useApi()
const { success, error } = useToast()

const form = ref({
  partyId: '',
  startDate: '',
  endDate: '',
  note: ''
})

watch(() => props.selectedParty, (newVal) => {
  if (newVal) {
    form.value.partyId = newVal
  }
})

watch(() => props.selectedDate, (newVal) => {
  if (newVal) {
    if (!form.value.startDate) {
      form.value.startDate = newVal
    } else if (!form.value.endDate && newVal >= form.value.startDate) {
      form.value.endDate = newVal
    } else {
      form.value.startDate = newVal
      form.value.endDate = ''
    }
  }
})

async function handleSubmit() {
  if (!form.value.partyId || !form.value.startDate || !form.value.endDate) {
    error('Bitte alle Pflichtfelder ausfüllen')
    return
  }

  if (form.value.endDate < form.value.startDate) {
    error('Enddatum muss nach Startdatum liegen')
    return
  }

  try {
    await createBooking({
      party_id: parseInt(form.value.partyId),
      start_date: form.value.startDate,
      end_date: form.value.endDate,
      note: form.value.note || null
    })

    success('Buchung erfolgreich gespeichert')
    form.value = { partyId: '', startDate: '', endDate: '', note: '' }
    emit('saved')
    emit('partySelect', null)
  } catch (err) {
    error(err.message)
  }
}
</script>

<template>
  <div class="card">
    <h3 class="font-display text-xl font-medium text-text-primary mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-family-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
      </svg>
      Neue Buchung
    </h3>

    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label class="form-label">Familie</label>
        <select v-model="form.partyId" class="form-input" required>
          <option value="">Familie auswählen...</option>
          <option v-for="party in parties" :key="party.id" :value="party.id">
            {{ party.name }}
          </option>
        </select>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="form-label">Von</label>
          <input
            type="date"
            v-model="form.startDate"
            class="form-input"
            required
          />
        </div>
        <div>
          <label class="form-label">Bis</label>
          <input
            type="date"
            v-model="form.endDate"
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

      <button type="submit" class="btn-primary">
        Buchung speichern
      </button>
    </form>
  </div>
</template>
