<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
      <div>
        <h1 class="text-3xl font-bold text-or">Tableau de bord Gérant</h1>
        <p class="text-sm text-slate-500 mt-1">
          Suivi opérationnel des collaborateurs, projets, campagnes et bénéficiaires de votre ONG.
        </p>
      </div>
      <button
        @click="store.fetchAll"
        class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition self-start sm:self-auto"
      >
        Actualiser
      </button>
    </div>

    <!-- Alert Error -->
    <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des données de l'organisation..." />

    <div v-else class="space-y-6">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Projets</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ statistiques.totalProjets }}</h3>
            <span class="text-xs text-slate-400">En cours / planifiés</span>
          </div>
          <FolderKanban class="text-bleu-nuit" :size="32" />
        </div>

        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Collaborateurs</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ statistiques.totalUtilisateurs }}</h3>
            <span class="text-xs text-slate-400">{{ chefsProjet.length }} CP · {{ responsablesFinance.length }} Fin · {{ agents.length }} Ag</span>
          </div>
          <Users class="text-bleu-nuit" :size="32" />
        </div>

        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Campagnes</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ statistiques.totalCampagnes }}</h3>
            <span class="text-xs text-slate-400">Opérations terrain</span>
          </div>
          <ClipboardList class="text-bleu-nuit" :size="32" />
        </div>

        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Bénéficiaires</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ statistiques.totalBeneficiaires }}</h3>
            <span class="text-xs text-slate-400">Personnes assistées</span>
          </div>
          <UserCheck class="text-bleu-nuit" :size="32" />
        </div>
      </div>

      <!-- Financial & Team Summary -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Budget Card -->
        <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-slate-900">Enveloppe budgétaire totale</h2>
            <Wallet class="text-or" :size="24" />
          </div>
          <p class="text-3xl font-extrabold text-bleu-nuit">
            {{ formatMontant(statistiques.budgetTotal) }} <span class="text-sm font-semibold text-slate-500">FCFA</span>
          </p>
          <p class="text-xs text-slate-400 mt-2">
            Cumul des budgets alloués sur l'ensemble des projets actifs.
          </p>
          <div class="mt-6 pt-4 border-t border-slate-100 flex justify-between items-center text-xs">
            <span class="text-slate-500">Nombre de projets budgétisés</span>
            <span class="font-bold text-slate-800">{{ projets.length }}</span>
          </div>
        </div>

        <!-- Equipe ONG -->
        <div class="lg:col-span-2 bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-slate-900">Membres de l'équipe</h2>
            <RouterLink to="/gerant/utilisateurs" class="text-xs font-semibold text-or hover:underline">
              Gérer les membres
            </RouterLink>
          </div>

          <div class="grid grid-cols-3 gap-4 text-center">
            <div class="bg-sky-50/60 border border-sky-100 rounded-xl p-4">
              <span class="text-2xl font-bold text-sky-900">{{ chefsProjet.length }}</span>
              <p class="text-xs font-semibold text-sky-700 mt-1">Chefs de projet</p>
            </div>
            <div class="bg-amber-50/60 border border-amber-100 rounded-xl p-4">
              <span class="text-2xl font-bold text-amber-900">{{ responsablesFinance.length }}</span>
              <p class="text-xs font-semibold text-amber-700 mt-1">Responsables Finance</p>
            </div>
            <div class="bg-emerald-50/60 border border-emerald-100 rounded-xl p-4">
              <span class="text-2xl font-bold text-emerald-900">{{ agents.length }}</span>
              <p class="text-xs font-semibold text-emerald-700 mt-1">Agents Terrain</p>
            </div>
          </div>

          <div class="mt-5 pt-4 border-t border-slate-100 flex justify-end">
            <RouterLink
              to="/gerant/utilisateurs/creer"
              class="px-4 py-2 bg-bleu-nuit text-white text-xs font-semibold rounded-lg hover:bg-[#01111eff] transition"
            >
              + Inviter un collaborateur
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Aperçu Projets récents -->
      <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-xs-sm">
        <div class="px-6 py-4 flex items-center justify-between border-b border-slate-100">
          <h2 class="text-base font-bold text-slate-900">
            Projets en cours ({{ projets.length }})
          </h2>
          <RouterLink to="/gerant/projets" class="text-xs font-semibold text-or hover:underline">
            Voir tous les projets
          </RouterLink>
        </div>

        <EmptyState
          v-if="projets.length === 0"
          titre="Aucun projet"
          description="Votre organisation n'a actuellement aucun projet enregistré."
        />

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase">
              <tr>
                <th class="text-left px-6 py-3">Code & Projet</th>
                <th class="text-left px-6 py-3">Chef de projet</th>
                <th class="text-left px-6 py-3">Région</th>
                <th class="text-left px-6 py-3">Budget</th>
                <th class="text-left px-6 py-3">Période</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="proj in projets.slice(0, 5)" :key="proj.id" class="hover:bg-slate-50/50">
                <td class="px-6 py-3.5">
                  <div class="font-semibold text-slate-900">{{ proj.name }}</div>
                  <div class="text-xs text-slate-400">{{ proj.code || 'PRJ' }}</div>
                </td>
                <td class="px-6 py-3.5 text-slate-600">{{ proj.chef_projet || '-' }}</td>
                <td class="px-6 py-3.5 text-slate-600">{{ proj.region }}</td>
                <td class="px-6 py-3.5 font-semibold text-slate-900">
                  {{ formatMontant(proj.budget) }} FCFA
                </td>
                <td class="px-6 py-3.5 text-xs text-slate-500">
                  {{ proj.start_date }} au {{ proj.end_date }}
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
import {
  FolderKanban,
  Users,
  Wallet,
  ClipboardList,
  UserCheck,
} from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const store = useGerantStore()
const {
  users,
  projets,
  campaigns,
  beneficiaries,
  chefsProjet,
  responsablesFinance,
  agents,
  statistiques,
  loading,
  error,
} = storeToRefs(store)
const { formatMontant } = store

onMounted(() => {
  store.fetchAll()
})
</script>

