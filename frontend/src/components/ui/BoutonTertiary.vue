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
  "border border-slate-300 text-bleu-nuit hover:bg-bleu-nuit hover:text-white px-3 py-2 rounded-lg text-sm font-semibold transition-colors",
  attrs.class,
].filter(Boolean))
</script>

