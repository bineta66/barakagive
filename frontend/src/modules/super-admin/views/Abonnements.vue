<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Abonnements</h1>
        <p class="text-sm text-slate-500 mt-1">
          GÃ©rer les abonnements des organisations
        </p>
      </div>
      <select
        v-model="filtreStatut"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
      >
        <option value="tous">Tous les statuts</option>
        <option value="Actif">Actifs</option>
        <option value="ExpirÃ©">ExpirÃ©s</option>
      </select>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <StatCard
        titre="Revenu total"
        :valeur="formatMontant(abonnementStats.revenuTotal)"
        :icone="PiggyBank"
        couleur="emerald"
      />
      <StatCard
        titre="Abonnements actifs"
        :valeur="abonnementStats.actifs"
        :icone="CreditCard"
        couleur="sky"
      />
      <StatCard
        titre="Abonnements expirÃ©s"
        :valeur="abonnementStats.expires"
        :icone="CalendarX"
        couleur="red"
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
                Plan
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Date dÃ©but
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Date fin
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Montant
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="abonnement in abonnementsFiltres" :key="abonnement.id">
              <td class="px-4 py-3 text-sm font-medium text-slate-900">
                {{ abonnement.ong }}
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium text-bleu-nuit bg-bleu-nuit/10 rounded-full"
                >
                  {{ abonnement.plan }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ abonnement.dateDebut }}
              </td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ abonnement.dateFin }}
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                {{ formatMontant(abonnement.montant) }} FCFA
              </td>
              <td class="px-4 py-3">
                <StatusBadge :statut="abonnement.statut">{{ abonnement.statut }}</StatusBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Plans available -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-5">
      <h2 class="text-lg font-semibold text-slate-900 mb-4">Plans disponibles</h2>
      <div class="grid md:grid-cols-3 gap-4">
        <div
          v-for="plan in plans"
          :key="plan.nom"
          class="border border-slate-200/60 rounded-xl p-5 text-center"
        >
          <h3 class="text-xl font-bold text-slate-900 mb-2">{{ plan.nom }}</h3>
          <p class="text-2xl font-bold text-or mb-4">
            {{ formatMontant(plan.prix) }} FCFA
          </p>
          <div class="space-y-2 text-sm text-slate-600 mb-4">
            <p>{{ plan.utilisateurs }} utilisateurs</p>
            <p>{{ plan.projets }} projets</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { ref, computed } from "vue"
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import { superAdminService } from "@/modules/super-admin/services/superAdminService.js"
import { PiggyBank, CreditCard, CalendarX } from "lucide-vue-next"
import StatCard from "@/components/ui/StatCard.vue"

const store = useSuperAdminStore()
const { abonnements, formatMontant } = store
const abonnementStats = superAdminService.getAbonnementStatistiques()
const plans = superAdminService.getPlans()

const filtreStatut = ref("tous")

const abonnementsFiltres = computed(() => {
  if (filtreStatut.value === "tous") return abonnements.value
  return abonnements.value.filter((a) => a.statut === filtreStatut.value)
})
</script>





