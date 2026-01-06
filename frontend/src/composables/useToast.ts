import { ref, type Ref } from 'vue'
import type { Toast, ToastType } from '../types'

const toasts: Ref<Toast[]> = ref([])

export function useToast() {
  function showToast(message: string, type: ToastType = 'success'): void {
    const id = Date.now()
    toasts.value.push({ id, message, type })

    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  function success(message: string): void {
    showToast(message, 'success')
  }

  function error(message: string): void {
    showToast(message, 'error')
  }

  return {
    toasts,
    showToast,
    success,
    error
  }
}
