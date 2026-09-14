<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Demandes ONG</h1>
        <p class="text-sm text-slate-500 mt-1">
          GÃ©rer les demandes d'inscription des organisations
        </p>
      </div>
      <div class="flex gap-2">
        <select
          v-model="filtreStatut"
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
        >
          <option value="tous">Tous les statuts</option>
          <option value="En attente">En attente</option>
          <option value="ApprouvÃ©e">ApprouvÃ©es</option>
          <option value="RejetÃ©e">RejetÃ©es</option>
        </select>
      </div>
    </div>

    <!-- Statistiques rapides -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <StatCard
        titre="Total demandes"
        :valeur="demandeStats.totalDemandes"
        :icone="FileText"
        couleur="sky"
      />
      <StatCard
        titre="En attente"
        :valeur="demandeStats.enAttente"
        :icone="Clock"
        couleur="orange"
      />
      <StatCard
        titre="TraitÃ©e"
        :valeur="demandeStats.traitees"
        :icone="CheckCircle"
        couleur="emerald"
      />
    </div>

    <!-- Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Contact
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Pays
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Date de la demande
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="demande in demandesFiltrees" :key="demande.id">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                    <Building2 :size="16" class="text-slate-600" />
                  </div>
                  <div class="text-sm font-medium text-slate-900">
                    {{ demande.nom }}
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-slate-600">{{ demande.email }}</div>
                <div class="text-xs text-slate-500">{{ demande.telephone }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ demande.pays }}</td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ demande.dateDemande }}
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                  :class="
                    demande.statut === 'En attente'
                      ? 'text-orange-700 bg-orange-50'
                      : demande.statut === 'ApprouvÃ©e'
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-red-700 bg-red-50'
                  "
                >
                  {{ demande.statut }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-2">
                  <button
                    v-if="demande.statut === 'En attente'"
                    @click="approuverDemande(demande.id)"
                    class="text-xs text-bleu-nuit hover:text-bleu-nuit font-medium"
                  >
                    Approuver
                  </button>
                  <button
                    v-if="demande.statut === 'En attente'"
                    @click="rejeterDemande(demande.id)"
                    class="text-xs text-red-700 hover:text-red-900 font-medium"
                  >
                    Rejeter
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import { superAdminService } from "@/modules/super-admin/services/superAdminService.js"
import { FileText, Clock, CheckCircle } from "lucide-vue-next"
import StatCard from "@/components/ui/StatCard.vue"

const store = useSuperAdminStore()
const { demandesONG } = store

const demandeStats = superAdminService.getDemandeStatistiques()

const filtreStatut = ref("tous")

const demandesFiltrees = computed(() => {
  if (filtreStatut.value === "tous") return demandesONG.value
  return demandesONG.value.filter((d) => d.statut === filtreStatut.value)
})

const approuverDemande = (id) => {
  console.log("Approuver la demande:", id)
}

const rejeterDemande = (id) => {
  console.log("Rejeter la demande:", id)
}
</script>





