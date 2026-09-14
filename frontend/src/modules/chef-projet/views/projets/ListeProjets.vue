<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Projets</h1>
        <p class="text-xs text-gray-500 mt-1">
          GÃ©rez et suivez les projets humanitaires sur le terrain et en phase de dÃ©ploiement.
        </p>
      </div>
    </div>

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Volume budgÃ©taire allouÃ©</p>
          <h3 class="text-xl font-bold text-or mt-2">2 525 000 â‚¬</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Taux d'exÃ©cution terrain</p>
          <h3 class="text-xl font-bold text-or mt-2">78.4 %</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Zones d'intervention</p>
          <h3 class="text-xl font-bold text-slate-800 mt-2">14 secteurs</h3>
        </div>
        <MapPinned class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>En cours</option>
        <option>PlanifiÃ©</option>
        <option>TerminÃ©</option>
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
  Wallet,
  Activity,
  MapPinned,
  Search,
} from "lucide-vue-next"
import TableauProjets from "@/modules/chef-projet/components/projets/TableauProjets.vue"

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")

const projets = ref([
  {
    nom: "Secours Alimentaire & Nutrition d'Urgence",
    code: "PRJ-2025-089",
    budget: "340 000 â‚¬",
    debut: "15 Jan 2025",
    fin: "30 Nov 2025",
    statut: "En cours",
  },
  {
    nom: "AccÃ¨s Eau Potable & Forages Solaires",
    code: "PRJ-2025-072",
    budget: "520 000 â‚¬",
    debut: "01 FÃ©v 2025",
    fin: "31 DÃ©c 2025",
    statut: "En cours",
  },
  {
    nom: "Cliniques Mobiles & Soins PÃ©diatriques",
    code: "PRJ-2025-104",
    budget: "280 000 â‚¬",
    debut: "01 Juil 2025",
    fin: "30 Juin 2026",
    statut: "PlanifiÃ©",
  },
  {
    nom: "Appui Agricole & RÃ©silience MaraÃ®chÃ¨re",
    code: "PRJ-2024-045",
    budget: "195 000 â‚¬",
    debut: "10 Mar 2024",
    fin: "15 Mai 2025",
    statut: "TerminÃ©",
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

