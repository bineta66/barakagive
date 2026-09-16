<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Demandes d'inscription ONG</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gérer les demandes d'inscription des organisations en attente de validation
        </p>
      </div>
      <button
        @click="store.fetchAll"
        class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition"
      >
        Actualiser
      </button>
    </div>

    <!-- Alert Error -->
    <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />

    <!-- Statistiques rapides -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <StatCard
        titre="Total organisations"
        :valeur="ongs.length"
        :icone="FileText"
        couleur="sky"
      />
      <StatCard
        titre="En attente"
        :valeur="demandesONG.length"
        :icone="Clock"
        couleur="orange"
      />
      <StatCard
        titre="Organisations actives"
        :valeur="ongsActives.length"
        :icone="CheckCircle"
        couleur="emerald"
      />
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des demandes..." />

    <!-- Table -->
    <div v-else class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-xs-sm">
      <EmptyState
        v-if="demandesONG.length === 0"
        titre="Aucune demande en attente"
        description="Il n'y a actuellement aucune organisation en attente de validation."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Contact
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Pays / Région
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Date de la demande
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="demande in demandesONG" :key="demande.id" class="hover:bg-slate-50/70 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center text-or font-bold border border-slate-200">
                    {{ demande.acronym || demande.name.slice(0, 2).toUpperCase() }}
                  </div>
                  <div>
                    <div class="text-sm font-semibold text-slate-900">
                      {{ demande.name }}
                    </div>
                    <div v-if="demande.intervention_domain" class="text-xs text-slate-500">
                      {{ demande.intervention_domain }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-slate-700">{{ demande.email }}</div>
                <div class="text-xs text-slate-500">{{ demande.phone }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                {{ demande.country }} <span v-if="demande.region">({{ demande.region }})</span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ demande.created_at ? new Date(demande.created_at).toLocaleDateString('fr-FR') : '-' }}
              </td>
              <td class="px-4 py-3">
                <span class="inline-block px-2.5 py-1 text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full">
                  En attente
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { storeToRefs } from "pinia"
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import { FileText, Clock, CheckCircle } from "lucide-vue-next"
import StatCard from "@/components/ui/StatCard.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const store = useSuperAdminStore()
const { ongs, demandesONG, ongsActives, loading, error } = storeToRefs(store)

onMounted(() => {
  store.fetchAll()
})
</script>

