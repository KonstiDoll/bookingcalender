<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import backgroundImageUrl from '../assets/IMG_1470.jpeg?url'

interface UserOption {
  value: string
  label: string
}

const { login } = useAuth()

const username: Ref<string> = ref('')
const password: Ref<string> = ref('')
const errorMessage: Ref<string> = ref('')
const loading: Ref<boolean> = ref(false)
const isLoggedIn: Ref<boolean> = ref(false)

// Available users for dropdown
const users: UserOption[] = [
  { value: 'Admin', label: 'Admin' },
  { value: 'Siggi & Mausi', label: 'Siggi & Mausi' },
  { value: 'Silke & Wolfi & Zoe', label: 'Silke & Wolfi & Zoe' },
  { value: 'Claudi & Wolfram', label: 'Claudi & Wolfram' },
  { value: 'Extern', label: 'Extern' }
]

async function handleLogin(): Promise<void> {
  if (!username.value || !password.value) {
    errorMessage.value = 'Bitte Benutzer und Passwort eingeben'
    return
  }

  errorMessage.value = ''
  loading.value = true

  try {
    await login(username.value, password.value)
    // Trigger fade-out animation
    isLoggedIn.value = true
    // The watch in App.vue will handle loading the data
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Ein Fehler ist aufgetreten'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container" :class="{ 'fade-out': isLoggedIn }">
    <!-- Background Image -->
    <div class="background-image" :style="{ backgroundImage: `url(${backgroundImageUrl})` }"></div>

    <!-- Overlay -->
    <div class="background-overlay"></div>

    <!-- Content -->
    <div class="login-content">
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
  </div>
</template>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  transition: opacity 0.8s ease-out;
}

.login-container.fade-out {
  opacity: 0;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(3px);
  transform: scale(1.1); /* Scale up to avoid blur edges */
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.6) 0%,
    rgba(255, 255, 255, 0.5) 50%,
    rgba(255, 255, 255, 0.6) 100%
  );
  backdrop-filter: blur(2px);
}

.login-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
</style>
