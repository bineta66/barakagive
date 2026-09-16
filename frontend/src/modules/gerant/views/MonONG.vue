<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
      <div>
        <h1 class="text-3xl font-bold text-or">Mon Organisation (ONG)</h1>
        <p class="text-sm text-slate-500 mt-1">
          Informations administratives et structurelles de votre organisation.
        </p>
      </div>
      <button
        @click="chargerDonnees"
        class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition self-start sm:self-auto"
      >
        Actualiser
      </button>
    </div>

    <!-- Alert Error -->
    <AlertMessage v-if="erreur" type="error" :message="erreur" :dismissible="true" @dismiss="erreur = null" />

    <!-- Loading State -->
    <LoadingSpinner v-if="chargement" message="Chargement des informations de l'ONG..." />

    <div v-else-if="ong" class="space-y-6">
      <!-- Carte principale ONG -->
      <div class="bg-white border border-slate-200/60 rounded-2xl p-6 shadow-xs-sm">
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-5 pb-6 border-b border-slate-100">
          <div class="w-16 h-16 rounded-2xl bg-or/10 border border-or/30 text-or font-black text-2xl flex items-center justify-center">
            {{ ong.acronym ? ong.acronym.slice(0, 3) : (ong.name ? ong.name.slice(0, 2).toUpperCase() : 'ONG') }}
          </div>
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-slate-900">{{ ong.name }}</h2>
            <p v-if="ong.acronym" class="text-sm font-bold text-or">Sigle officiel : {{ ong.acronym }}</p>
            <p class="text-xs text-slate-500 mt-1">Domaine : {{ ong.intervention_domain || "Non précisé" }}</p>
          </div>
          <div>
            <span
              class="inline-block px-3 py-1.5 text-xs font-bold rounded-full"
              :class="ong.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'"
            >
              {{ ong.status === 'ACTIVE' ? 'Organisation Active' : 'En attente de validation' }}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-6 text-sm">
          <div>
            <span class="text-xs text-slate-400 font-semibold uppercase block">Email officiel</span>
            <span class="font-medium text-slate-800">{{ ong.email }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 font-semibold uppercase block">Téléphone</span>
            <span class="font-medium text-slate-800">{{ ong.phone }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 font-semibold uppercase block">Pays & Région</span>
            <span class="font-medium text-slate-800">{{ ong.country }} · {{ ong.region }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 font-semibold uppercase block">Adresse</span>
            <span class="font-medium text-slate-800">{{ ong.address || '-' }}</span>
          </div>
        </div>
      </div>

      <!-- Métriques opérationnelles de l'ONG -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Projets</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ store.statistiques.totalProjets }}</h3>
          </div>
          <FolderKanban class="text-bleu-nuit" :size="28" />
        </div>

        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Membres</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ store.statistiques.totalUtilisateurs }}</h3>
          </div>
          <Users class="text-bleu-nuit" :size="28" />
        </div>

        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Campagnes</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ store.statistiques.totalCampagnes }}</h3>
          </div>
          <ClipboardList class="text-bleu-nuit" :size="28" />
        </div>

        <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Bénéficiaires</p>
            <h3 class="text-2xl font-bold text-or mt-1">{{ store.statistiques.totalBeneficiaires }}</h3>
          </div>
          <UserCheck class="text-bleu-nuit" :size="28" />
        </div>
      </div>
    </div>

    <EmptyState
      v-else
      titre="Organisation introuvable"
      description="Impossible de charger les données de votre organisation."
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { FolderKanban, Users, ClipboardList, UserCheck } from "lucide-vue-next"
import { useAuthStore } from "@/stores/auth.js"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import api, { getErrorMessage } from "@/services/api.js"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const authStore = useAuthStore()
const store = useGerantStore()

const ong = ref(null)
const chargement = ref(false)
const erreur = ref(null)

const chargerDonnees = async () => {
  chargement.value = true
  erreur.value = null

  try {
    await store.fetchAll()
    const res = await api.get("/api/organizations/")
    const userOrgId = authStore.organizationId

    if (userOrgId) {
      ong.value = res.data.find((o) => o.id === userOrgId) || res.data[0]
    } else {
      ong.value = res.data[0] || null
    }
  } catch (err) {
    erreur.value = getErrorMessage(err)
  } finally {
    chargement.value = false
  }
}

onMounted(() => {
  chargerDonnees()
})
</script>

