<template>
  <div class="flex-1 flex flex-col h-full bg-gray-50 overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200 bg-white sticky top-0 z-10 shadow-sm flex items-center gap-4">
      <button 
        @click="$emit('back')" 
        class="p-2 -ml-2 text-gray-400 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
      >
        <ArrowLeft :size="20" />
      </button>
      <div>
        <h2 class="text-xl font-bold text-gray-900">{{ zone.nom }}</h2>
        <p class="text-sm text-gray-500 font-medium mt-0.5">
          {{ zone.beneficiaires.length }} bénéficiaires classés
        </p>
      </div>
    </div>

    <!-- Liste -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="space-y-3">
        <div 
          v-for="b in zone.beneficiaires" 
          :key="b.id"
          @click="$emit('select-beneficiaire', b)"
          class="bg-white border border-gray-100 rounded-xl p-4 flex justify-between items-center cursor-pointer hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <div class="flex items-center gap-4">
            <div class="h-12 w-12 rounded-full flex items-center justify-center font-bold text-lg" :class="getAvatarClass(b.score)">
              {{ b.prenom.charAt(0) }}{{ b.nom.charAt(0) }}
            </div>
            <div>
              <h4 class="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">{{ b.prenom }} {{ b.nom }}</h4>
              <p class="text-sm text-gray-500 mt-0.5">
                {{ b.sexe }} • {{ b.age ? b.age + ' ans' : 'Âge inconnu' }}
                <span v-if="b.quartier" class="ml-1 text-gray-400">•</span>
                <span v-if="b.quartier" class="ml-1">{{ b.quartier }}</span>
              </p>
            </div>
          </div>
          
          <div class="flex flex-col items-end">
            <span class="text-lg font-black" :class="getTextColorClass(b.score)">
              {{ b.score }} <span class="text-xs text-gray-400">/100</span>
            </span>
            <span class="text-xs font-bold uppercase tracking-wider mt-1" :class="getTextColorClass(b.score)">
              {{ getBadgeText(b.score) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft } from 'lucide-vue-next';

defineProps({
  zone: Object,
});

defineEmits(['back', 'select-beneficiaire']);

const getAvatarClass = (score) => {
  if (score >= 80) return 'bg-red-100 text-red-700';
  if (score >= 60) return 'bg-orange-100 text-orange-700';
  if (score >= 40) return 'bg-yellow-100 text-yellow-700';
  return 'bg-green-100 text-green-700';
};

const getTextColorClass = (score) => {
  if (score >= 80) return 'text-red-600';
  if (score >= 60) return 'text-orange-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-green-600';
};

const getBadgeText = (score) => {
  if (score >= 80) return 'Très élevée';
  if (score >= 60) return 'Élevée';
  if (score >= 40) return 'Moyenne';
  return 'Faible';
};
</script>
