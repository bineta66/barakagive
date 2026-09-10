<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-4xl font-bold text-amber-800">Projets</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez et suivez les projets humanitaires sur le terrain et en phase de déploiement.
        </p>
      </div>

      <RouterLink
        to="/projets/creer"
        class="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg flex items-center gap-2 text-sm font-semibold"
      >
        <Plus :size="18" />
        Nouveau projet
      </RouterLink>
    </div>

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Volume budgétaire alloué</p>
          <h3 class="text-xl font-bold text-sky-900 mt-2">2 525 000 €</h3>
        </div>
        <Wallet class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Taux d'exécution terrain</p>
          <h3 class="text-xl font-bold text-amber-800 mt-2">78.4 %</h3>
        </div>
        <Activity class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Zones d'intervention</p>
          <h3 class="text-xl font-bold text-slate-800 mt-2">14 secteurs</h3>
        </div>
        <MapPinned class="text-slate-400" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>En cours</option>
        <option>Planifié</option>
        <option>Terminé</option>
      </select>

      <select class="border rounded-lg px-3 py-2 text-sm">
        <option>Toutes les zones</option>
      </select>

      <select class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les responsables</option>
      </select>

      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher un projet..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>
    </div>

    <!-- Tableau -->
    <TableauProjets :projects="projetsFiltres" />
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import {
  Plus,
  Wallet,
  Activity,
  MapPinned,
  Search,
} from "lucide-vue-next"
import TableauProjets from "@/components/projets/TableauProjets.vue"

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")

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

const projetsFiltres = computed(() => {
  return projets.value.filter((p) => {
    const okRecherche =
      p.nom.toLowerCase().includes(recherche.value.toLowerCase()) ||
      p.code.toLowerCase().includes(recherche.value.toLowerCase())

    const okStatut =
      filtreStatut.value === "Tous les statuts" ||
      p.statut === filtreStatut.value

    return okRecherche && okStatut
  })
})
</script>
