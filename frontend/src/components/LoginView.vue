<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { useAuth } from '../composables/useAuth'

interface UserOption {
  value: string
  label: string
}

const emit = defineEmits<{
  'login-success': []
}>()

const { login } = useAuth()

const username: Ref<string> = ref('')
const password: Ref<string> = ref('')
const errorMessage: Ref<string> = ref('')
const loading: Ref<boolean> = ref(false)

// Available users for dropdown
const users: UserOption[] = [
  { value: 'Admin', label: 'Admin' },
  { value: 'Siggi & Mausi', label: 'Siggi & Mausi' },
  { value: 'Silke & Wolfi & Zoe', label: 'Silke & Wolfi & Zoe' },
  { value: 'Claudi & Wolfram', label: 'Claudi & Wolfram' },
  { value: 'Extern', label: 'Extern' }
]

async function handleLogin(): Promise<void> {
  console.log('handleLogin called', { username: username.value, password: password.value })

  if (!username.value || !password.value) {
    errorMessage.value = 'Bitte Benutzer und Passwort eingeben'
    return
  }

  errorMessage.value = ''
  loading.value = true

  try {
    console.log('Calling login...')
    const result = await login(username.value, password.value)
    console.log('Login successful:', result)
    emit('login-success')
  } catch (err) {
    console.error('Login error:', err)
    errorMessage.value = err instanceof Error ? err.message : 'Ein Fehler ist aufgetreten'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="card max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="font-display text-3xl font-normal tracking-tight text-text-primary mb-2">
          3Mädel<span class="italic font-light">Hausen</span>
        </h1>
        <p class="text-text-secondary">
          Bitte melden Sie sich an
        </p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- User Select -->
        <div>
          <label for="username" class="form-label">Benutzer</label>
          <select
            id="username"
            v-model="username"
            class="form-input"
            required
            :disabled="loading"
          >
            <option value="">Bitte auswählen...</option>
            <option
              v-for="user in users"
              :key="user.value"
              :value="user.value"
            >
              {{ user.label }}
            </option>
          </select>
        </div>

        <!-- Password Input -->
        <div>
          <label for="password" class="form-label">Passwort</label>
          <input
            id="password"
            type="password"
            v-model="password"
            class="form-input"
            placeholder="Passwort eingeben"
            required
            autocomplete="current-password"
            :disabled="loading"
          />
        </div>

        <!-- Error Message -->
        <div
          v-if="errorMessage"
          class="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm"
        >
          {{ errorMessage }}
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="w-full bg-family-1 hover:bg-family-1/90 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="loading"
        >
          {{ loading ? 'Anmeldung...' : 'Anmelden' }}
        </button>
      </form>
    </div>
  </div>
</template>
