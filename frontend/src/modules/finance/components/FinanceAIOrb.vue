<template>
  <div class="fixed bottom-8 right-8 z-50 cursor-pointer" @click="toggleAssistant">
    <div class="relative w-20 h-20">
      <!-- Orb principal -->
      <div class="absolute inset-0 rounded-full" :class="alertClass" style="background: linear-gradient(135deg, #021427 0%, #1a3a5c 100%); box-shadow: 0 0 30px rgba(2, 20, 39, 0.5), inset 0 0 20px rgba(255, 215, 0, 0.1);">
        <!-- Contour doré -->
        <div class="absolute inset-0 rounded-full border-4 border-yellow-500/60 animate-pulse"></div>
        
        <!-- Pièces dorées flottantes -->
        <div class="absolute inset-0 animate-spin" style="animation-duration: 8s;">
          <div class="absolute top-0 left-1/2 w-3 h-3 bg-yellow-400 rounded-full transform -translate-x-1/2 -translate-y-1/2 shadow-lg"></div>
          <div class="absolute bottom-0 left-1/2 w-2 h-2 bg-yellow-300 rounded-full transform -translate-x-1/2 translate-y-1/2 shadow-lg"></div>
          <div class="absolute left-0 top-1/2 w-2.5 h-2.5 bg-yellow-500 rounded-full transform -translate-x-1/2 -translate-y-1/2 shadow-lg"></div>
          <div class="absolute right-0 top-1/2 w-2 h-2 bg-yellow-400 rounded-full transform translate-x-1/2 -translate-y-1/2 shadow-lg"></div>
        </div>
        
        <!-- Badge d'alerte -->
        <div class="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center" :class="alertBadgeClass">
          <div class="w-2 h-2 rounded-full bg-white"></div>
        </div>
        
        <!-- Halo lumineux -->
        <div class="absolute inset-0 rounded-full opacity-30 animate-ping" :class="alertHaloClass"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alertLevel: {
    type: String,
    default: 'green',
    validator: (value) => ['green', 'yellow', 'orange', 'red'].includes(value)
  }
})

const emit = defineEmits(['toggle'])

const alertClass = computed(() => {
  const classes = {
    green: 'border-green-500',
    yellow: 'border-yellow-500',
    orange: 'border-orange-500',
    red: 'border-red-500'
  }
  return classes[props.alertLevel] || classes.green
})

const alertBadgeClass = computed(() => {
  const classes = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500'
  }
  return classes[props.alertLevel] || classes.green
})

const alertHaloClass = computed(() => {
  const classes = {
    green: 'bg-green-400',
    yellow: 'bg-yellow-400',
    orange: 'bg-orange-400',
    red: 'bg-red-400'
  }
  return classes[props.alertLevel] || classes.green
})

const toggleAssistant = () => {
  emit('toggle')
}
</script>

<style scoped>
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin linear infinite;
}
</style>