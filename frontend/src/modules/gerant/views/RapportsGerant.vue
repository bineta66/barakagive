<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Rapports</h1>
        <p class="text-xs text-gray-500 mt-1">
          Rapports d'impact et financiers de l'organisation.
        </p>
      </div>
    </div>

    <!-- Rapports -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 flex flex-col items-center text-center">
         <div class="w-16 h-16 rounded-full bg-or/10 flex items-center justify-center mb-4">
          <FileText class="text-or" :size="32" />
        </div>
        <h3 class="text-lg font-bold text-slate-900 mb-2">Rapport d'exécution</h3>
        <p class="text-sm text-gray-500 mb-4">Synthèse budgétaire et taux d'exécution par projet.</p>
        <BoutonPrimary>
          Générer
        </BoutonPrimary>
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-6 flex flex-col items-center text-center">
        <div class="w-16 h-16 rounded-full bg-or/10 flex items-center justify-center mb-4">
          <BarChart3 class="text-or" :size="32" />
        </div>
        <h3 class="text-lg font-bold text-slate-900 mb-2">Rapport d'impact</h3>
        <p class="text-sm text-gray-500 mb-4">Bénéficiaires, zones d'intervention et indicateurs clés.</p>
        <BoutonPrimary>
          Générer
        </BoutonPrimary>
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-6 flex flex-col items-center text-center">
        <div class="w-16 h-16 rounded-full bg-bleu-nuit/10 flex items-center justify-center mb-4">
          <Download class="text-bleu-nuit" :size="32" />
        </div>
        <h3 class="text-lg font-bold text-slate-900 mb-2">Export complet</h3>
        <p class="text-sm text-gray-500 mb-4">Exporter toutes les données en format PDF ou Excel.</p>
        <BoutonPrimary>
          Télécharger
        </BoutonPrimary>
      </div>
    </div>

    <!-- Historique des rapports -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="px-6 py-4 ">
        <h3 class="text-sm font-bold uppercase text-slate-900">Historique des rapports générés</h3>
      </div>

      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-3">Type</th>
            <th class="text-left px-4 py-3">Date</th>
            <th class="text-left px-4 py-3">Généré par</th>
            <th class="text-center px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-t hover:bg-slate-50">
            <td class="px-4 py-3 text-sm font-semibold text-slate-800">Rapport d'exécution</td>
            <td class="px-4 py-3 text-sm text-slate-600">12 Sep 2025</td>
            <td class="px-4 py-3 text-sm text-slate-600">Amine Diop</td>
            <td class="px-4 text-center">
             <StatusBadge statut="Terminé">
               Terminé
             </StatusBadge>
            </td>
            <td class="px-4 text-center">
              <button class="p-1 text-slate-500 hover:text-bleu-nuit rounded-lg transition-colors">
                <Eye class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { FileText, BarChart3, Download, Eye } from 'lucide-vue-next'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
</script>






