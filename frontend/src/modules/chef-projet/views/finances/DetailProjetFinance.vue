<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail du projet</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations budgétaires complètes du projet.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonPrimary @click="exporterPdf">
          <FileDown :size="18" />
          Exporter PDF
        </BoutonPrimary>

        <BoutonSecondary to="/chef-projet/finances">
          <List :size="18" />
          Retour aux finances
        </BoutonSecondary>
      </div>
    </div>

    <!-- Détails -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="grid grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Nom</p>
          <p class="text-gray-700">{{ projet.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Code</p>
          <p class="text-gray-700">{{ projet.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Région</p>
          <p class="text-gray-700">{{ projet.region }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Zone</p>
          <p class="text-gray-700">{{ projet.zone }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de début</p>
          <p class="text-gray-700">{{ projet.dateDebut }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ projet.dateFin }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Budget alloué</p>
          <p class="text-gray-700 font-semibold">{{ formatMontant(projet.budgetAllocation) }} FCFA</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Montant engagé</p>
          <p class="text-gray-700 font-semibold">{{ formatMontant(projet.montantEngage) }} FCFA</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Restant</p>
          <p class="text-gray-700 font-semibold">{{ formatMontant(projet.budgetAllocation - projet.montantEngage) }} FCFA</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Taux d'exécution</p>
          <p class="text-gray-700 font-semibold">{{ projet.tauxExecution }}%</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
           <StatusBadge :statut="projet.statut">{{ projet.statut }}</StatusBadge>
        </div>

        <div class="col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Description</p>
          <p class="text-gray-700">{{ projet.description }}</p>
        </div>
      </div>
    </div>

    <!-- Campagnes associées -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-sm font-bold uppercase text-slate-900">Campagnes associées</h3>
        <span class="text-xs text-slate-500">{{ projet.campagnes.length }} campagne(s)</span>
      </div>

      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-2">Nom</th>
            <th class="text-left px-4 py-2">Zone</th>
            <th class="text-left px-4 py-2">Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="campagne in projet.campagnes" :key="campagne.id" class="border-t">
            <td class="px-4 py-2 text-sm text-slate-700">{{ campagne.nom }}</td>
            <td class="px-4 py-2 text-sm text-slate-600">{{ campagne.zone }}</td>
            <td class="px-4 py-2">
               <StatusBadge :statut="campagne.statut">{{ campagne.statut }}</StatusBadge>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Dons associés -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-sm font-bold uppercase text-slate-900">Dons associés</h3>
        <span class="text-xs text-slate-500">{{ projet.dons.length }} don(s)</span>
      </div>

      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-2">Donateur</th>
            <th class="text-right px-4 py-2">Montant</th>
            <th class="text-left px-4 py-2">Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="don in projet.dons" :key="don.id" class="border-t">
            <td class="px-4 py-2 text-sm text-slate-700">{{ don.donateur }}</td>
            <td class="px-4 py-2 text-sm text-right text-slate-600">{{ formatMontant(don.montant) }} FCFA</td>
            <td class="px-4 py-2 text-sm text-slate-600">{{ don.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Justificatifs -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-sm font-bold uppercase text-slate-900">Justificatifs</h3>
      </div>

      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-2">Fichier</th>
            <th class="text-left px-4 py-2">Taille</th>
            <th class="text-left px-4 py-2">Date</th>
            <th class="text-right px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="justificatif in projet.justificatifs" :key="justificatif.id" class="border-t">
            <td class="px-4 py-2 text-sm text-slate-700">{{ justificatif.nom }}</td>
            <td class="px-4 py-2 text-sm text-slate-600">{{ justificatif.taille }}</td>
            <td class="px-4 py-2 text-sm text-slate-600">{{ justificatif.date }}</td>
            <td class="px-4 py-2">
              <div class="flex justify-end">
                <button class="text-slate-500 hover:text-bleu-nuit" title="Télécharger">
                  <Download :size="18" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { FileDown, List, Download } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import { useFinances } from "@/composables/useFinances.js"

const route = useRoute()
const { projetsDetail } = useFinances()

const projet = ref(null)

onMounted(() => {
  const id = Number(route.params.id)
  const found = projetsDetail.value.find((p) => p.id === id)
  if (found) {
    projet.value = found
  }
})

function formatMontant(montant) {
  if (!montant) return "0"
  return montant.toLocaleString("fr-FR")
}

function exporterPdf() {
  alert("Export PDF du projet " + projet.value?.code)
}
</script>


