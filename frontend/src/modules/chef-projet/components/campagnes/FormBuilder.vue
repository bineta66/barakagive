<template>
  <div class="flex-1 inline-flex flex-col justify-start items-start gap-4">
    <div class="self-stretch flex justify-between items-center">
      <h3 class="text-xl font-bold" style="color: #744D03">Questions</h3>
      <BoutonPrimary @click="$emit('ajouter-question')">
        <Plus :size="18" />
        Ajouter une question
      </BoutonPrimary>
    </div>

    <div v-if="questions.length === 0" class="self-stretch p-12 border-2 border-dashed border-gray-300 rounded-xl flex flex-col justify-center items-center">
      <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <p class="text-gray-500 text-sm">Aucune question. Cliquez sur "Ajouter une question" pour commencer.</p>
    </div>

    <div class="self-stretch bg-white rounded-xl border overflow-hidden" style="border-color: #744D03">
      <QuestionCard
        v-for="(question, index) in questions"
        :key="question.id"
        :question="question"
        :index="index"
        @mettre-a-jour="(id, champ, valeur) => $emit('mettre-a-jour', id, champ, valeur)"
        @supprimer="$emit('supprimer', $event)"
        @dupliquer="$emit('dupliquer', $event)"
        @ajouter-option="(id, option) => $emit('ajouter-option', id, option)"
        @supprimer-option="(id, idx) => $emit('supprimer-option', id, idx)"
      />
    </div>
  </div>
</template>

<script setup>
import { Plus } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import QuestionCard from "@/modules/chef-projet/components/campagnes/QuestionCard.vue"

defineProps({
  questions: {
    type: Array,
    required: true,
  },
})

defineEmits([
  "ajouter-question",
  "mettre-a-jour",
  "supprimer",
  "dupliquer",
  "ajouter-option",
  "supprimer-option",
])
</script>
