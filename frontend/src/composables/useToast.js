import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  function showToast(message, type = 'success') {
    const id = Date.now()
    toasts.value.push({ id, message, type })

    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  function success(message) {
    showToast(message, 'success')
  }

  function error(message) {
    showToast(message, 'error')
  }

  return {
    toasts,
    showToast,
    success,
    error
  }
}
