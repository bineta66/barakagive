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
      <button
        @click="store.fetchAll"
        class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition"
      >
        Actualiser
      </button>
    </div>

    <!-- Alert Error -->
    <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des données de la plateforme..." />

    <div v-else class="space-y-6">
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
          titre="Demandes en attente"
          :valeur="demandesONG.length"
          :icone="Users"
          couleur="amber"
        />
        <KpiCard
          titre="Régions couvertes"
          :valeur="statistiques.regionsCount"
          :icone="FolderKanban"
          couleur="purple"
        />
      </div>

      <!-- Stats Summary -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div class="lg:col-span-2 bg-white border border-slate-200/60 rounded-xl p-5">
          <h2 class="text-lg font-semibold text-slate-900 mb-2">
            Répartition des organisations
          </h2>
          <p class="text-sm text-slate-500 mb-4">
            Total des ONG enregistrées avec statut d'activation
          </p>
          <div class="space-y-3">
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-600">Actives</span>
              <span class="font-bold text-emerald-600">{{ statistiques.ongActives }}</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div
                class="bg-emerald-500 h-full rounded-full transition-all"
                :style="{ width: `${statistiques.totalONG ? (statistiques.ongActives / statistiques.totalONG) * 100 : 0}%` }"
              ></div>
            </div>

            <div class="flex justify-between items-center text-sm pt-2">
              <span class="text-slate-600">En attente de validation</span>
              <span class="font-bold text-amber-600">{{ demandesONG.length }}</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div
                class="bg-amber-500 h-full rounded-full transition-all"
                :style="{ width: `${statistiques.totalONG ? (demandesONG.length / statistiques.totalONG) * 100 : 0}%` }"
              ></div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <StatCard
            titre="Taux d'activation"
            :valeur="statistiques.tauxActivation + '%'"
            :icone="TrendingUp"
            couleur="emerald"
          />
          <StatCard
            titre="Organisations actives"
            :valeur="statistiques.ongActives"
            :icone="CreditCard"
            couleur="sky"
          />
          <StatCard
            titre="En attente"
            :valeur="demandesONG.length"
            :icone="CalendarX"
            couleur="orange"
          />
        </div>
      </div>

      <!-- Demandes en attente -->
      <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
        <div class="px-5 py-4 flex items-center justify-between border-b border-slate-100">
          <h2 class="text-lg font-semibold text-slate-900">
            Demandes d'inscription en attente ({{ demandesONG.length }})
          </h2>
          <RouterLink
            to="/super-admin/ongs"
            class="text-xs font-semibold text-or hover:underline"
          >
            Voir toutes les ONG
          </RouterLink>
        </div>

        <EmptyState
          v-if="demandesONG.length === 0"
          titre="Aucune demande en attente"
          description="Toutes les demandes d'inscription ont été traitées."
        />

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                  Organisation
                </th>
                <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                  Pays / Région
                </th>
                <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                  Date
                </th>
                <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                  Statut
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="demande in demandesONG" :key="demande.id">
                <td class="px-4 py-3">
                  <div class="text-sm font-medium text-slate-900">
                    {{ demande.name }}
                  </div>
                  <div class="text-xs text-slate-500">
                    {{ demande.email }}
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-slate-600">
                  {{ demande.country }} <span v-if="demande.region">({{ demande.region }})</span>
                </td>
                <td class="px-4 py-3 text-sm text-slate-500">
                  {{ demande.created_at ? new Date(demande.created_at).toLocaleDateString('fr-FR') : '-' }}
                </td>
                <td class="px-4 py-3">
                  <span class="inline-block px-2 py-1 text-xs font-medium text-amber-700 bg-amber-50 rounded-full">
                    En attente
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { storeToRefs } from "pinia"
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import {
  Building2,
  Activity,
  Users,
  FolderKanban,
  CreditCard,
  CalendarX,
  TrendingUp,
} from "lucide-vue-next"
import KpiCard from "@/components/ui/KpiCard.vue"
import StatCard from "@/components/ui/StatCard.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const store = useSuperAdminStore()
const { demandesONG, statistiques, loading, error } = storeToRefs(store)

onMounted(() => {
  store.fetchAll()
})
</script>

