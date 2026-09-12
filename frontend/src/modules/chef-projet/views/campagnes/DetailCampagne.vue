<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-3xl font-bold text-amber-800">Détail de la campagne</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes de la campagne.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonPrimary :to="`/chef-projet/campagnes/${route.params.id}/formulaire`">
          <FileText :size="18" />
          Formulaire
        </BoutonPrimary>

        <BoutonSecondary to="/chef-projet/campagnes">
          <List :size="18" />
          Liste des campagnes
        </BoutonSecondary>
      </div>
    </div>

    <!-- Détails -->
    <div class="max-w-2xl bg-white border border-slate-200/60 rounded-xl p-6" v-if="campagne">
      <div class="grid grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Nom</p>
          <p class="text-gray-700">{{ campagne.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Code</p>
          <p class="text-gray-700">{{ campagne.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Projet</p>
          <p class="text-gray-700">{{ campagne.projet }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Zone</p>
          <p class="text-gray-700">{{ campagne.zone }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de début</p>
          <p class="text-gray-700">{{ campagne.dateDebut }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ campagne.dateFin }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
          <span
            class="px-2 py-1 rounded text-xs font-semibold"
            :class="{
              'bg-emerald-100 text-emerald-700': campagne.statut === 'En cours',
              'bg-gray-100 text-gray-600': campagne.statut === 'Planifiée',
              'bg-sky-100 text-sky-700': campagne.statut === 'Terminée',
            }"
          >
            {{ campagne.statut }}
          </span>
        </div>

        <div class="col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Description</p>
          <p class="text-gray-700">{{ campagne.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute, RouterLink } from "vue-router"
import { List, FileText } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import { campagnesMock } from "@/data/campagnesMock.js"

const route = useRoute()

const campagne = ref(null)

onMounted(() => {
  const id = Number(route.params.id)
  const found = campagnesMock.value.find((c) => c.id === id)
  if (found) {
    campagne.value = found
  }
})
</script>
