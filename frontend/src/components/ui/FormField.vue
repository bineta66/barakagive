<template>
  <div class="form-field">
    <!-- Label -->
    <label
      v-if="label"
      :for="id"
      class="block text-xs font-semibold uppercase text-slate-600 mb-1.5"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-0.5">*</span>
    </label>

    <!-- Slot par défaut — contient l'input/select/textarea -->
    <div class="relative">
      <slot />

      <!-- Icône succès -->
      <div
        v-if="showSuccess && !error"
        class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
      >
        <svg class="w-4 h-4 text-bleu-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <!-- Icône erreur -->
      <div
        v-if="error"
        class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
      >
        <svg class="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    </div>

    <!-- Message d'erreur -->
    <p v-if="error" class="mt-1 text-xs text-red-600 flex items-center gap-1">
      {{ error }}
    </p>

    <!-- Hint (texte d'aide) -->
    <p v-else-if="hint" class="mt-1 text-xs text-slate-400">
      {{ hint }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  label:       { type: String,  default: ''    },
  error:       { type: String,  default: ''    },
  hint:        { type: String,  default: ''    },
  required:    { type: Boolean, default: false },
  showSuccess: { type: Boolean, default: false },
  id:          { type: String,  default: ''    },
})
</script>