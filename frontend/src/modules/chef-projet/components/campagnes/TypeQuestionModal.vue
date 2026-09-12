<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden">
      <div class="p-6 border-b border-gray-100">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold" style="color: #744D03">
            Type de question
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-2">
          Sélectionnez le type de champ à ajouter au formulaire
        </p>
      </div>

      <div class="p-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <button
          v-for="type in typesQuestions"
          :key="type.id"
          @click="selectionnerType(type.id)"
          class="flex flex-col items-center gap-3 p-4 rounded-xl border-2 border-gray-200 hover:border-[#744D03] hover:bg-[#744D03]/5 transition"
        >
          <div class="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center text-slate-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="type.iconPath" />
            </svg>
          </div>
          <span class="text-sm font-semibold text-gray-700 text-center">
            {{ type.label }}
          </span>
        </button>
      </div>

      <div class="bg-gray-50 px-6 py-4 flex justify-end">
        <button
          @click="fermer"
          class="font-semibold px-5 py-2.5 rounded-lg text-sm"
          style="border: 1px solid #744D03; color: #744D03"
        >
          Annuler
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue"

const props = defineProps({
  ouvert: {
    type: Boolean,
    default: false,
  },
  typesQuestions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(["fermer", "selectionner"])

const selectionnerType = (type) => {
  emit("selectionner", type)
  fermer()
}

const fermer = () => {
  emit("fermer")
}
</script>