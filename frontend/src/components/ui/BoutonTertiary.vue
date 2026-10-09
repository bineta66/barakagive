<template>
  <button :class="allClasses" v-bind="filteredAttrs">
    <slot />
  </button>
</template>

<script setup>
import { computed } from "vue"
import { useAttrs } from "vue"

const attrs = useAttrs()

const filteredAttrs = computed(() => {
  const { class: _, style: __, ...rest } = attrs
  return rest
})

const allClasses = computed(() => [
  "border border-slate-300 bg-white text-bleu-nuit hover:bg-bleu-nuit hover:text-white hover:border-bleu-nuit px-3 py-2 rounded-xl active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-baraka/30 focus-visible:ring-offset-2 text-sm font-semibold transition-all duration-200",
  attrs.class,
].filter(Boolean))
</script>

