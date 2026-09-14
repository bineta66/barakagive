<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">
          Tableau de bord Super Administrateur
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          Vue d'ensemble de la plateforme BarakaGive
        </p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
      <KpiCard
        titre="ONG totales"
        :valeur="statistiques.totalONG"
        :icone="Building2"
        couleur="sky"
      />
      <KpiCard
        titre="ONG actives"
        :valeur="statistiques.ongActives"
        :icone="Activity"
        couleur="emerald"
      />
      <KpiCard
        titre="Utilisateurs"
        :valeur="statistiques.totalUtilisateurs"
        :icone="Users"
        couleur="purple"
      />
      <KpiCard
        titre="Projets"
        :valeur="statistiques.totalProjets"
        :icone="FolderKanban"
        couleur="amber"
      />
    </div>

    <!-- Revenue & Stats Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Revenue Card -->
      <div class="lg:col-span-2 bg-white border border-slate-200/60 rounded-xl p-5">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">
          Revenus mensuels
        </h2>
        <SuperAdminRevenueChart />
      </div>

      <!-- Stats Summary -->
      <div class="space-y-4">
        <StatCard
          titre="Revenu mensuel"
          :valeur="formatMontant(statistiques.revenuMensuel)"
          :icone="PiggyBank"
          couleur="emerald"
        />
        <StatCard
          titre="Taux d'activation"
          :valeur="statistiques.tauxActivation + '%'"
          :icone="TrendingUp"
          couleur="sky"
        />
        <StatCard
          titre="Abonnements actifs"
          :valeur="statistiques.abonnementsActifs"
          :icone="CreditCard"
          couleur="purple"
        />
        <StatCard
          titre="Abonnements expirÃ©s"
          :valeur="statistiques.abonnementsExpires"
          :icone="CalendarX"
          couleur="red"
        />
      </div>
    </div>

    <!-- Demandes en attente -->
    <div class="bg-white border border-slate-200/60 rounded-xl">
      <div class="px-5 py-4 ">
        <h2 class="text-lg font-semibold text-slate-900">
          Demandes d'inscription rÃ©centes
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Pays
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Date
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
            <tr v-for="(demande, index) in demandesONG" :key="demande.id">
              <td class="px-4 py-3">
                <div class="text-sm font-medium text-slate-900">
                  {{ demande.nom }}
                </div>
                <div class="text-xs text-slate-500">
                  {{ demande.email }}
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ demande.pays }}</td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ demande.dateDemande }}
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium text-orange-700 bg-orange-50 rounded-full"
                >
                  {{ demande.statut }}
                </span>
              </td>
              <td class="px-4 py-3">
                <button
                  @click="traiterDemande(demande.id)"
                  class="text-xs text-bleu-nuit hover:text-[#01111eff] font-medium"
                >
                  Traiter
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import {
  Building2,
  Activity,
  Users,
  FolderKanban,
  PiggyBank,
  CreditCard,
  CalendarX,
  TrendingUp,
} from "lucide-vue-next"
import KpiCard from "@/components/ui/KpiCard.vue"
import StatCard from "@/components/ui/StatCard.vue"
import SuperAdminRevenueChart from "@/modules/super-admin/components/charts/SuperAdminRevenueChart.vue"

const store = useSuperAdminStore()
const { demandesONG, statistiques, formatMontant } = store

const traiterDemande = (id) => {
  console.log("Traiter la demande:", id)
}
</script>





