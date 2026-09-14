<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail du projet</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes du projet humanitaire.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/projets">
          <List :size="18" />
          Liste des projets
        </BoutonSecondary>
      </div>
    </div>

    <!-- Détails -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="grid grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Nom</p>
          <p class="text-gray-700">{{ projet.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Code</p>
          <p class="text-gray-700">{{ projet.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Budget</p>
          <p class="text-gray-700 font-semibold">{{ projet.budget }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
          <StatusBadge :statut="projet.statut">{{ projet.statut }}</StatusBadge>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de début</p>
          <p class="text-gray-700">{{ projet.debut }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ projet.fin }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { List } from "lucide-vue-next"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"

const route = useRoute()

const projets = ref([
  {
    nom: "Secours Alimentaire & Nutrition d'Urgence",
    code: "PRJ-2025-089",
    budget: "340 000 €",
    debut: "15 Jan 2025",
    fin: "30 Nov 2025",
    statut: "En cours",
  },
  {
    nom: "Accès Eau Potable & Forages Solaires",
    code: "PRJ-2025-072",
    budget: "520 000 €",
    debut: "01 Fév 2025",
    fin: "31 Déc 2025",
    statut: "En cours",
  },
  {
    nom: "Cliniques Mobiles & Soins Pédiatriques",
    code: "PRJ-2025-104",
    budget: "280 000 €",
    debut: "01 Juil 2025",
    fin: "30 Juin 2026",
    statut: "Planifié",
  },
  {
    nom: "Appui Agricole & Résilience Maraîchère",
    code: "PRJ-2024-045",
    budget: "195 000 €",
    debut: "10 Mar 2024",
    fin: "15 Mai 2025",
    statut: "Terminé",
  },
])

const projet = ref(null)

onMounted(() => {
  const code = route.params.id
  const found = projets.value.find((p) => p.code === code)
  if (found) {
    projet.value = found
  }
})
</script>
