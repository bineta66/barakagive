<template>
  <nav v-if="items.length" aria-label="Fil d’Ariane" class="mb-3 text-sm text-slate-500">
    <ol class="flex flex-wrap items-center gap-2">
      <li v-for="(item, index) in items" :key="`${item.label}-${index}`" class="flex items-center gap-2">
        <router-link
          v-if="item.to && index < items.length - 1"
          :to="item.to"
          class="hover:text-bleu-nuit hover:underline"
        >{{ item.label }}</router-link>
        <span v-else :aria-current="index === items.length - 1 ? 'page' : undefined" :class="index === items.length - 1 ? 'text-slate-700' : ''">
          {{ item.label }}
        </span>
        <span v-if="index < items.length - 1" aria-hidden="true">/</span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});
</script>
