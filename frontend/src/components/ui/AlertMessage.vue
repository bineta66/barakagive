<template>
  <div
    v-if="message"
    class="p-4 rounded-xl border flex items-start gap-3 transition-all"
    :class="alertClasses"
  >
    <div class="shrink-0 mt-0.5">
      <!-- Error icon -->
      <svg v-if="type === 'error'" class="w-5 h-5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <!-- Success icon -->
      <svg v-else-if="type === 'success'" class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <!-- Info icon -->
      <svg v-else class="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
    </div>
    <div class="flex-1 text-sm leading-relaxed" :class="textClass">
      <strong v-if="title" class="font-semibold block mb-0.5">{{ title }}</strong>
      <span>{{ message }}</span>
    </div>
    <button
      v-if="dismissible"
      type="button"
      @click="$emit('dismiss')"
      class="text-slate-400 hover:text-slate-600 shrink-0 p-1"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  type: {
    type: String,
    default: "error", // error, success, info
  },
  title: {
    type: String,
    default: "",
  },
  message: {
    type: String,
    required: true,
  },
  dismissible: {
    type: Boolean,
    default: false,
  },
})

defineEmits(["dismiss"])

const alertClasses = computed(() => {
  switch (props.type) {
    case "success":
      return "bg-emerald-50 border-emerald-200"
    case "info":
      return "bg-sky-50 border-sky-200"
    case "error":
    default:
      return "bg-rose-50 border-rose-200"
  }
})

const textClass = computed(() => {
  switch (props.type) {
    case "success":
      return "text-emerald-800"
    case "info":
      return "text-sky-800"
    case "error":
    default:
      return "text-rose-800"
  }
})
</script>
