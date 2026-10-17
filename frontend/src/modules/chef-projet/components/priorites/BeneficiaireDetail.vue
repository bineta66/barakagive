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
        <h2 class="text-xl font-bold text-gray-900">Détail du bénéficiaire</h2>
      </div>
    </div>

    <!-- Contenu -->
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      
      <!-- Fiche Info -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden relative">
        <div class="h-2 w-full" :class="getBgColorClass(beneficiaire.score)"></div>
        <div class="p-6 flex items-start gap-5">
          <div class="h-16 w-16 rounded-full flex items-center justify-center font-bold text-2xl" :class="getAvatarClass(beneficiaire.score)">
            {{ initials }}
          </div>
          <div class="flex-1">
            <h3 class="text-2xl font-bold text-gray-900">{{ displayName }}</h3>
            <div class="grid grid-cols-2 gap-y-2 mt-4 text-sm">
              <div class="flex items-center gap-2 text-gray-600">
                <Phone class="w-4 h-4 text-gray-400" />
                {{ beneficiaire.telephone || 'Non renseigné' }}
              </div>
              <div class="flex items-center gap-2 text-gray-600">
                <MapPin class="w-4 h-4 text-gray-400" />
                {{ beneficiaire.quartier || beneficiaire.adresse || 'Non renseigné' }}
              </div>
              <div class="flex items-center gap-2 text-gray-600">
                <User class="w-4 h-4 text-gray-400" />
                {{ beneficiaire.sexe }} • {{ beneficiaire.age ? beneficiaire.age + ' ans' : 'Âge inconnu' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Critères de vulnérabilité -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
          <h3 class="font-bold text-gray-900">Critères ayant donné le score</h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="text-xs text-gray-500 bg-gray-50/50 uppercase">
              <tr>
                <th class="px-6 py-3 font-semibold">Critère</th>
                <th class="px-6 py-3 font-semibold">Réponse</th>
                <th class="px-6 py-3 font-semibold text-right">Points</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr 
                v-for="(critere, index) in beneficiaire.criteres_detail" 
                :key="index"
                class="hover:bg-gray-50/50 transition-colors"
              >
                <td class="px-6 py-4 font-medium text-gray-900">{{ critere.nom }}</td>
                <td class="px-6 py-4">
                  <span 
                    class="px-2.5 py-1 rounded-full text-xs font-semibold"
                    :class="critere.obtenu ? 'bg-red-50 text-red-700' : 'bg-gray-100 text-gray-600'"
                  >
                    {{ critere.reponse }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right font-bold" :class="critere.obtenu ? 'text-red-600' : 'text-gray-400'">
                  +{{ critere.points }}
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50 font-bold border-t border-gray-200">
              <tr>
                <td colspan="2" class="px-6 py-4 text-right text-gray-900 uppercase text-xs tracking-wider">Score final</td>
                <td class="px-6 py-4 text-right text-xl" :class="getTextColorClass(beneficiaire.score)">
                  {{ beneficiaire.score }} <span class="text-xs text-gray-500 font-medium">/ 100</span>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Resultat Final -->
      <div class="flex items-center justify-between p-5 rounded-xl border border-dashed" :class="getBorderColorClass(beneficiaire.score)">
        <span class="text-sm font-semibold text-gray-600 uppercase tracking-wider">Niveau d'urgence</span>
        <span class="px-4 py-1.5 rounded-full font-bold text-sm" :class="getBadgeClass(beneficiaire.score)">
          {{ getBadgeIcon(beneficiaire.score) }} {{ getBadgeText(beneficiaire.score) }}
        </span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { ArrowLeft, Phone, MapPin, User } from 'lucide-vue-next';

const props = defineProps({
  beneficiaire: Object,
});

defineEmits(['back']);

const displayName = computed(() => {
  const b = props.beneficiaire || {};
  if (b.nom_complet) return b.nom_complet;
  return [b.prenom, b.nom].filter(Boolean).join(' ') || 'Bénéficiaire';
});

const initials = computed(() => {
  const b = props.beneficiaire || {};
  const prenom = b.prenom || '';
  const nom = b.nom || '';
  const fromParts = `${prenom.charAt(0)}${nom.charAt(0)}`.toUpperCase();
  if (fromParts.trim()) return fromParts;
  const full = b.nom_complet || '';
  const bits = full.split(/\s+/).filter(Boolean);
  return ((bits[0]?.[0] || '') + (bits[1]?.[0] || '')).toUpperCase() || '?';
});

const getAvatarClass = (score) => {
  if (score >= 80) return 'bg-red-100 text-red-700';
  if (score >= 60) return 'bg-orange-100 text-orange-700';
  if (score >= 40) return 'bg-yellow-100 text-yellow-700';
  return 'bg-green-100 text-green-700';
};

const getBgColorClass = (score) => {
  if (score >= 80) return 'bg-red-500';
  if (score >= 60) return 'bg-orange-500';
  if (score >= 40) return 'bg-yellow-500';
  return 'bg-green-500';
};

const getBorderColorClass = (score) => {
  if (score >= 80) return 'border-red-200 bg-red-50/30';
  if (score >= 60) return 'border-orange-200 bg-orange-50/30';
  if (score >= 40) return 'border-yellow-200 bg-yellow-50/30';
  return 'border-green-200 bg-green-50/30';
};

const getTextColorClass = (score) => {
  if (score >= 80) return 'text-red-600';
  if (score >= 60) return 'text-orange-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-green-600';
};

const getBadgeClass = (score) => {
  if (score >= 80) return 'bg-red-100 text-red-700';
  if (score >= 60) return 'bg-orange-100 text-orange-700';
  if (score >= 40) return 'bg-yellow-100 text-yellow-700';
  return 'bg-green-100 text-green-700';
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
