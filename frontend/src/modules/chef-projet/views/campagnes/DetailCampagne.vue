<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">DÃ©tail de la campagne</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complÃ¨tes de la campagne.
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

    <!-- DÃ©tails -->
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
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de dÃ©but</p>
          <p class="text-gray-700">{{ campagne.dateDebut }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ campagne.dateFin }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
           <StatusBadge :statut="campagne.statut">{{ campagne.statut }}</StatusBadge>
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
import StatusBadge from "@/components/ui/StatusBadge.vue"
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

