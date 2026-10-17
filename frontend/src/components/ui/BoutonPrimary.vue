<template>
  <RouterLink v-if="to" :to="to" :class="allClasses" v-bind="filteredAttrs" @click="handleClick">
    <slot />
  </RouterLink>
  <button v-else :class="allClasses" v-bind="filteredAttrs" @click="handleClick">
    <slot />
  </button>
</template>

<script setup>
import { computed } from "vue"
import { RouterLink } from "vue-router"
import { useAttrs } from "vue"

const props = defineProps({
  to: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(["click"])
const attrs = useAttrs()

const filteredAttrs = computed(() => {
  const { class: _, style: __, onClick: __onClick, ...rest } = attrs
  return rest
})

const allClasses = computed(() => [
  "bg-bleu-nuit hover:bg-[#00262f] text-white px-5 py-2.5 rounded-xl active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-baraka/40 focus-visible:ring-offset-2 flex items-center justify-center gap-2 text-sm font-semibold transition-all duration-200",
  attrs.class,
].filter(Boolean))

const handleClick = (event) => {
  emit("click", event)
}
</script>

