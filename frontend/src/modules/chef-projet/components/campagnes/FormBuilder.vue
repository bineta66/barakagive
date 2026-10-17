<template>
  <div class="w-full min-w-0 flex-1 inline-flex flex-col justify-start items-start gap-4">
    <!-- En-tête -->
    <div class="self-stretch flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h3 class="text-lg font-bold text-[#00313C] sm:text-xl">Questions du formulaire</h3>
      <BoutonPrimary class="w-full justify-center sm:w-auto" @click="$emit('ajouter-question')">
        <Plus :size="18" />
        Ajouter une question
      </BoutonPrimary>
    </div>

    <!-- État vide -->
    <div
      v-if="questions.length === 0"
      class="self-stretch p-6 sm:p-12 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col justify-center items-center text-center"
    >
      <div
        class="w-16 h-16 rounded-2xl bg-bleu-nuit/5 flex items-center justify-center mb-4"
      >
        <svg
          class="w-8 h-8 text-bleu-nuit/40"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <p class="text-slate-500 text-sm font-medium">
        Aucune question pour l'instant
      </p>
      <p class="text-slate-400 text-xs mt-1">
        Cliquez sur "Ajouter une question" pour commencer.
      </p>
    </div>

    <!-- Liste des questions -->
    <div
      v-else
      class="w-full min-w-0 self-stretch bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden"
    >
      <QuestionCard
        v-for="(question, index) in questions"
        :key="question.id"
        :question="question"
        :index="index"
        :questions-count="questions.length"
        :criteres="criteres"
        @mettre-a-jour="
          (id, champ, valeur) => $emit('mettre-a-jour', id, champ, valeur)
        "
        @supprimer="$emit('supprimer', $event)"
        @dupliquer="$emit('dupliquer', $event)"
        @ajouter-option="(id, option) => $emit('ajouter-option', id, option)"
        @supprimer-option="(id, idx) => $emit('supprimer-option', id, idx)"
        @reorder="$emit('reorder', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { Plus } from "lucide-vue-next";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import QuestionCard from "@/modules/chef-projet/components/campagnes/QuestionCard.vue";

defineProps({
  questions: { type: Array, required: true },
  criteres: { type: Array, default: () => [] },
});

defineEmits([
  "ajouter-question",
  "mettre-a-jour",
  "supprimer",
  "dupliquer",
  "ajouter-option",
  "supprimer-option",
  "reorder",
]);
</script>
