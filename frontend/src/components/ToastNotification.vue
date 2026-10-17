<template>
  <Transition name="toast">
    <div 
      v-if="visible"
      class="toast-notification fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg border flex items-center gap-3 max-w-sm"
      :class="toastClasses"
    >
      <div class="flex-shrink-0">
        <component :is="icon" :size="20" />
      </div>
      <div class="flex-1">
        <p class="text-sm font-medium">{{ message }}</p>
      </div>
      <button 
        @click="close"
        class="flex-shrink-0 text-current opacity-60 hover:opacity-100 transition"
      >
        <X :size="16" />
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { CheckCircle, AlertCircle, X } from 'lucide-vue-next'

const props = defineProps({
  type: {
    type: String,
    default: 'success', // success, warning, error
  },
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 4000
  }
})

const emit = defineEmits(['close'])

const visible = ref(true)
let timeout = null

const toastClasses = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-bleu-accent/10 border-bleu-accent/30 text-bleu-nuit'
    case 'warning':
      return 'bg-bleu-nuit/10 border-bleu-nuit/30 text-bleu-nuit'
    case 'error':
      return 'bg-rose-baraka/10 border-rose-baraka/30 text-rose-baraka'
    default:
      return 'bg-white border-slate-200 text-slate-800'
  }
})

const icon = computed(() => {
  switch (props.type) {
    case 'success':
      return CheckCircle
    case 'warning':
      return AlertCircle
    case 'error':
      return AlertCircle
    default:
      return CheckCircle
  }
})

const close = () => {
  visible.value = false
  emit('close')
}

watch(() => props.message, () => {
  visible.value = true
  if (timeout) clearTimeout(timeout)
  timeout = setTimeout(() => {
    close()
  }, props.duration)
}, { immediate: true })
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-notification {
  backdrop-filter: blur(10px);
}
</style>