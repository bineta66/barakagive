<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-xl max-w-2xl w-full overflow-hidden"
    >
      <!-- Header -->
      <div
        class="p-6 border-b border-slate-100 flex justify-between items-center"
      >
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">Type de question</h2>
          <p class="text-sm text-slate-500 mt-0.5">
            Sélectionnez le type de champ à ajouter au formulaire
          </p>
        </div>
        <button
          @click="fermer"
          class="text-slate-400 hover:text-slate-600 transition p-2 rounded-lg hover:bg-slate-100"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Grille types -->
      <div class="p-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button
          v-for="type in typesQuestions"
          :key="type.id"
          @click="selectionnerType(type.id)"
          class="flex flex-col items-center gap-3 p-4 rounded-xl border-2 border-slate-200 hover:border-bleu-nuit hover:bg-bleu-nuit/5 transition group"
        >
          <div
            class="w-12 h-12 rounded-xl bg-slate-100 group-hover:bg-bleu-nuit/10 flex items-center justify-center text-slate-600 group-hover:text-bleu-nuit transition"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="type.iconPath"
              />
            </svg>
          </div>
          <span
            class="text-sm font-semibold text-slate-700 group-hover:text-bleu-nuit text-center transition"
          >
            {{ type.label }}
          </span>
        </button>
      </div>

      <!-- Footer -->
      <div
        class="bg-slate-50 px-6 py-4 flex justify-end border-t border-slate-100"
      >
        <button
          @click="fermer"
          class="font-semibold px-5 py-2.5 rounded-lg text-sm border border-slate-200 text-slate-700 hover:bg-slate-100 transition"
        >
          Annuler
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  ouvert: { type: Boolean, default: false },
  typesQuestions: { type: Array, default: () => [] },
});

const emit = defineEmits(["fermer", "selectionner"]);

const selectionnerType = (type) => {
  emit("selectionner", type);
  fermer();
};

const fermer = () => emit("fermer");
</script>
