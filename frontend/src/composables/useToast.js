import { ref } from 'vue'

const toast = ref(null)

export function useToast() {
  const showToast = (message, type = 'success', duration = 4000) => {
    toast.value = {
      message,
      type,
      duration
    }
  }

  const hideToast = () => {
    toast.value = null
  }

  return {
    toast,
    showToast,
    hideToast
  }
}

export default useToast