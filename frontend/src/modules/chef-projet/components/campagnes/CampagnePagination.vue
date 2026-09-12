<template>
  <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
    <p class="text-slate-500">
      Affichage de 1 à {{ campagnes?.length ?? 0 }} sur {{ campagnes?.length ?? 0 }} campagnes
    </p>

    <div class="flex gap-1">
      <button
        class="px-3 py-2 border rounded bg-slate-100 text-slate-400"
        :disabled="pageCourante === 1"
        @click="$emit('change-page', pageCourante - 1)"
      >
        Précédent
      </button>

      <button
        v-for="page in totalPages"
        :key="page"
        class="w-8 h-8 border rounded"
        :class="page === pageCourante ? 'bg-green-900 text-white' : ''"
        @click="$emit('change-page', page)"
      >
        {{ page }}
      </button>

      <button
        class="px-3 py-2 border rounded"
        :disabled="pageCourante === totalPages"
        @click="$emit('change-page', pageCourante + 1)"
      >
        Suivant
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pageCourante: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
})

defineEmits(["change-page"])
</script>
