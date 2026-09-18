<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Statistiques</h1>
        <p class="text-sm text-slate-500 mt-1">
          Analyse détaillée des performances de la plateforme
        </p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
      <KpiCard
        titre="Revenu mensuel"
        :valeur="formatMontant(abonnementStats.revenuTotal) + ' FCFA'"
        :icone="PiggyBank"
        couleur="emerald"
      />
      <KpiCard
        titre="Taux d'activation"
        :valeur="statistiques.tauxActivation + '%'"
        :icone="TrendingUp"
        couleur="sky"
      />
      <KpiCard
        titre="Abonnements actifs"
        :valeur="abonnementStats.actifs"
        :icone="CreditCard"
        couleur="purple"
      />
      <KpiCard
        titre="Demandes traitées"
        :valeur="demandeStats.traitees"
        :icone="CheckCircle"
        couleur="amber"
      />
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- Revenue Chart -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">
          Évolution des revenus
        </h2>
        <SuperAdminRevenueChart />
      </div>

      <!-- ONG par pays -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">
          ONG par pays
        </h2>
        <SuperAdminCountryChart />
      </div>
    </div>

    <!-- Plan Distribution -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-5">
      <h2 class="text-lg font-semibold text-slate-900 mb-4">
        Distribution des plans
      </h2>
      <SuperAdminPlanChart />
    </div>
  </div>
</template>

<script setup>
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import {
  PiggyBank,
  CreditCard,
  TrendingUp,
  CheckCircle,
} from "lucide-vue-next"
import KpiCard from "@/components/ui/KpiCard.vue"
import SuperAdminRevenueChart from "@/modules/super-admin/components/charts/SuperAdminRevenueChart.vue"
import SuperAdminCountryChart from "@/modules/super-admin/components/charts/SuperAdminCountryChart.vue"
import SuperAdminPlanChart from "@/modules/super-admin/components/charts/SuperAdminPlanChart.vue"

const store = useSuperAdminStore()
const { statistiques, formatMontant } = store

const abonnementStats = { revenuTotal: 0, actifs: 0 }
const demandeStats = { traitees: 0 }
</script>






