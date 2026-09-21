<template>
  <div>
    <!-- Drawer Overlay -->
    <div 
      v-if="isOpen" 
      class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 transition-opacity"
      @click="$emit('close')"
    ></div>

    <!-- Drawer Content -->
    <div 
      class="fixed inset-y-0 right-0 w-full max-w-lg bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col"
      :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
    >
      <div v-if="!regionData" class="flex-1 flex items-center justify-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-or"></div>
      </div>
      
      <div v-else-if="currentView === 'region'" class="flex-1 overflow-y-auto">
        <!-- Drawer Header -->
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-start bg-gray-50/50 sticky top-0 z-10">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">{{ regionData.region }}</h2>
            <p class="text-sm text-gray-500 mt-1 font-medium">
              <span class="text-gray-900 font-semibold">{{ regionData.total_beneficiaires }} bénéficiaires</span> • 
              {{ regionData.zones.length }} zones
            </p>
          </div>
          <button 
            @click="$emit('close')" 
            class="p-2 -mr-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X :size="24" />
          </button>
        </div>

        <!-- Résumé Intelligent -->
        <div class="p-6 border-b border-gray-100 bg-gradient-to-br from-blue-50 to-indigo-50/30">
          <div class="flex items-start gap-3">
            <Sparkles class="text-blue-500 mt-1 flex-shrink-0" :size="20" />
            <div>
              <h3 class="text-sm font-bold text-blue-900 mb-2 uppercase tracking-wider">Résumé intelligent</h3>
              <p class="text-sm text-blue-800 leading-relaxed font-medium">
                {{ regionData.summary }}
              </p>
            </div>
          </div>
        </div>

        <!-- Liste des Zones -->
        <div class="p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">Zones classées</h3>
          
          <div class="space-y-4">
            <div 
              v-for="zone in regionData.zones" 
              :key="zone.id"
              class="border border-gray-100 rounded-xl p-5 hover:border-blue-200 hover:shadow-md transition-all bg-white"
            >
              <div class="flex justify-between items-start mb-3">
                <div>
                  <h4 class="text-lg font-bold text-gray-900">{{ zone.nom }}</h4>
                  <div class="flex items-center gap-2 mt-1">
                    <span 
                      class="px-2.5 py-1 text-xs font-bold rounded-full"
                      :class="getBadgeClass(zone.score_moyen)"
                    >
                      {{ getBadgeIcon(zone.score_moyen) }} {{ getBadgeText(zone.score_moyen) }}
                    </span>
                    <span class="text-gray-300">•</span>
                    <span class="text-sm font-semibold text-gray-600">{{ zone.beneficiaires.length }} bénéficiaires</span>
                  </div>
                </div>
                <div class="text-right flex flex-col items-end">
                  <span class="text-2xl font-black text-gray-900 leading-none" :class="getTextColorClass(zone.score_moyen)">
                    {{ zone.score_moyen }}
                  </span>
                  <span class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">/ 100</span>
                </div>
              </div>
              
              <button 
                @click="openZone(zone)"
                class="w-full mt-4 py-2.5 bg-gray-50 hover:bg-gray-100 text-gray-700 font-semibold rounded-lg text-sm transition-colors flex items-center justify-center gap-2 border border-gray-200"
              >
                Voir les bénéficiaires
                <ArrowRight :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- List View -->
      <BeneficiairesList 
        v-else-if="currentView === 'zone'"
        :zone="selectedZone"
        @back="currentView = 'region'"
        @select-beneficiaire="openBeneficiaire"
      />
      
      <!-- Detail View -->
      <BeneficiaireDetail
        v-else-if="currentView === 'beneficiaire'"
        :beneficiaire="selectedBeneficiaire"
        @back="currentView = 'zone'"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { X, Sparkles, ArrowRight } from 'lucide-vue-next';
import BeneficiairesList from '@/modules/chef-projet/components/priorites/BeneficiairesList.vue';
import BeneficiaireDetail from '@/modules/chef-projet/components/priorites/BeneficiaireDetail.vue';

const props = defineProps({
  isOpen: Boolean,
  regionData: Object,
});

const emit = defineEmits(['close']);

const currentView = ref('region');
const selectedZone = ref(null);
const selectedBeneficiaire = ref(null);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    currentView.value = 'region';
  }
});

const openZone = (zone) => {
  selectedZone.value = zone;
  currentView.value = 'zone';
};

const openBeneficiaire = (beneficiaire) => {
  selectedBeneficiaire.value = beneficiaire;
  currentView.value = 'beneficiaire';
};

const getBadgeClass = (score) => {
  if (score >= 80) return 'bg-red-50 text-red-700 border border-red-200';
  if (score >= 60) return 'bg-orange-50 text-orange-700 border border-orange-200';
  if (score >= 40) return 'bg-yellow-50 text-yellow-700 border border-yellow-200';
  return 'bg-green-50 text-green-700 border border-green-200';
};

const getTextColorClass = (score) => {
  if (score >= 80) return 'text-red-600';
  if (score >= 60) return 'text-orange-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-green-600';
};

const getBadgeIcon = (score) => {
  if (score >= 80) return '🔴';
  if (score >= 60) return '🟠';
  if (score >= 40) return '🟡';
  return '🟢';
};

const getBadgeText = (score) => {
  if (score >= 80) return 'Très élevée';
  if (score >= 60) return 'Élevée';
  if (score >= 40) return 'Moyenne';
  return 'Faible';
};
</script>
