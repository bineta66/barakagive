<template>
  <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
    <p class="text-slate-500">
      Affichage de 1 Ã  {{ beneficiairesPage.length }} sur {{ total }} bÃ©nÃ©ficiaires
    </p>

    <div class="flex gap-1">
      <button
        class="px-3 py-2 border rounded bg-slate-100 text-slate-400"
        :disabled="page === 1"
        @click="$emit('update:page', page - 1)"
      >
        PrÃ©cÃ©dent
      </button>

      <button
        v-for="p in totalPages"
        :key="p"
        class="w-8 h-8 border rounded"
        :class="p === page ? 'bg-bleu-nuit text-white' : ''"
        @click="$emit('update:page', p)"
      >
        {{ p }}
      </button>

      <button
        class="px-3 py-2 border rounded"
        :disabled="page === totalPages"
        @click="$emit('update:page', page + 1)"
      >
        Suivant
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  beneficiairesPage: {
    type: Array,
    required: true,
  },
  total: {
    type: Number,
    required: true,
  },
  page: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
})

defineEmits(["update:page"])
</script>

