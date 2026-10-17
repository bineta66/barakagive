<template>
  <div class="border-t border-slate-200/80 bg-white px-4 py-3">
    <form @submit.prevent="handleSubmit" class="flex items-end gap-3">
      <!-- Zone de texte -->
      <div
        class="flex-1 relative bg-slate-50 border border-slate-200 rounded-2xl
               focus-within:border-[#CCA43B]/60 focus-within:ring-2 focus-within:ring-[#CCA43B]/20
               transition-all duration-200"
      >
        <textarea
          ref="textareaRef"
          v-model="draft"
          maxlength="4000"
          :disabled="disabled"
          placeholder="Posez votre question au contrôleur financier IA…"
          rows="1"
          class="w-full bg-transparent resize-none px-4 py-3 text-sm text-slate-800
                 placeholder:text-slate-400 focus:outline-none rounded-2xl
                 min-h-[44px] max-h-[140px] leading-relaxed"
          @keydown.enter.exact.prevent="handleSubmit"
          @input="autoResize"
        />
      </div>

      <!-- Bouton envoyer -->
      <button
        type="submit"
        :disabled="!canSend"
        class="flex-shrink-0 w-11 h-11 rounded-2xl flex items-center justify-center
               transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#CCA43B]/40"
        :class="canSend
          ? 'bg-[#021427] hover:bg-[#032040] shadow-md hover:shadow-lg cursor-pointer'
          : 'bg-slate-200 cursor-not-allowed'"
        aria-label="Envoyer"
      >
        <svg v-if="disabled" class="w-5 h-5 text-slate-400 animate-spin"
             xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <svg v-else class="w-5 h-5 transition-colors duration-200"
             :class="canSend ? 'text-[#CCA43B]' : 'text-slate-400'"
             xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m22 2-7 20-4-9-9-4Z"/>
          <path d="M22 2 11 13"/>
        </svg>
      </button>
    </form>
    <p class="text-[10px] text-slate-400 mt-2 text-center">
      Entrée pour envoyer · Maj+Entrée pour nouvelle ligne
    </p>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from "vue"

const props = defineProps({ disabled: { type: Boolean, default: false } })
const emit  = defineEmits(["send"])

const draft       = ref("")
const textareaRef = ref(null)

const canSend = computed(() => !props.disabled && draft.value.trim().length > 0)

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = "auto"
  el.style.height = Math.min(el.scrollHeight, 140) + "px"
}

const handleSubmit = () => {
  if (!canSend.value) return
  const q = draft.value.trim()
  emit("send", q, () => {
    if (draft.value.trim() !== q) return
    draft.value = ""
    nextTick(() => {
      const el = textareaRef.value
      if (el) el.style.height = "auto"
    })
  })
}

const focus = () => nextTick(() => textareaRef.value?.focus())
defineExpose({ focus })
</script>
