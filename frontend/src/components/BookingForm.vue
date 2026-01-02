<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { parties, useApi } from '../composables/useApi'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'

const props = defineProps({
  selectionStart: {
    type: String,
    default: ''
  },
  selectionEnd: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['saved', 'selectionChange'])

const { createBooking } = useApi()
const { currentUser, isAdmin } = useAuth()
const { success, error } = useToast()

const form = ref({
  partyId: '',
  startDate: '',
  endDate: '',
  note: ''
})

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

watch(() => props.selectionStart, (newVal) => {
  form.value.startDate = newVal
})

watch(() => props.selectionEnd, (newVal) => {
  form.value.endDate = newVal
})

// Emit changes when form dates change
function onStartDateChange(e) {
  form.value.startDate = e.target.value
  emit('selectionChange', form.value.startDate, form.value.endDate)
}

function onEndDateChange(e) {
  form.value.endDate = e.target.value
  emit('selectionChange', form.value.startDate, form.value.endDate)
}

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
    // Reset form but keep partyId for non-admin users
    const keepPartyId = !isAdmin.value ? form.value.partyId : ''
    form.value = { partyId: keepPartyId, startDate: '', endDate: '', note: '' }
    emit('saved')
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

      <button type="submit" class="btn-primary">
        Buchung speichern
      </button>
    </form>
  </div>
</template>
