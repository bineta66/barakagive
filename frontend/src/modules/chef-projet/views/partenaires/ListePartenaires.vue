<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Partenaires</h1>
        <p class="text-xs text-gray-500 mt-1">
          Suivez les organisations partenaires opérationnelles et locales des missions humanitaires.
        </p>
      </div>

      <BoutonPrimary @click="ajouterPartenaire">
        <Plus :size="18" />
        Ajouter
      </BoutonPrimary>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-3 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher par nom d'organisation..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-2 focus:ring-or/30"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm bg-white">
        <option value="Tous les statuts">Tous les statuts</option>
        <option value="ACTIF">ACTIF</option>
        <option value="INACTIF">INACTIF</option>
      </select>

      <BoutonTertiary @click="reinitialiserFiltres">
        Réinitialiser
      </BoutonTertiary>
    </div>

    <!-- Section : Partenaires Opérationnels & Locaux -->
    <div class="space-y-4">
      <div class="bg-white px-4 py-3 inline-flex items-center gap-3">
        <Users :size="20" class="text-bleu-nuit" />
        <span class="text-base font-semibold text-slate-900">Partenaires Opérationnels & Locaux</span>
      </div>

      <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
            <tr>
              <th class="text-left px-4 py-3">ORGANISATION</th>
              <th class="text-left px-4 py-3">DOMAINE D'INTERVENTION</th>
              <th class="text-left px-4 py-3">ZONE DE DEPLOIEMENT</th>
              <th class="text-center px-4 py-3">STATUT OPERATIONNEL</th>
              <th class="text-center px-4 py-3">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="partenaire in partenairesFiltres" :key="partenaire.id" class="border-t hover:bg-slate-50">
              <td class="px-4 py-3">
                <p class="text-slate-900 text-sm font-semibold">{{ partenaire.nom }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-slate-900 text-xs">{{ partenaire.domaine }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-slate-900 text-xs">{{ partenaire.zone }}</p>
              </td>
              <td class="px-4 py-3 text-center">
                <StatusBadge :statut="partenaire.statut">{{ partenaire.statut }}</StatusBadge>
              </td>
              <td class="px-4 py-3">
                <div class="flex justify-center gap-1.5">
                  <button @click="supprimer(partenaire.id)" class="p-1 text-slate-400 hover:text-red-600">
                    <Trash2 :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
          <p class="text-slate-500">
            Affichage de {{ partenairesFiltres.length }} partenaire(s)
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { Plus, Search, Users, Trash2 } from "lucide-vue-next"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")

const partenaires = ref([
  {
    id: 1,
    nom: "Croix-Rouge Sénégalaise",
    domaine: "Secours d'Urgence & Santé",
    zone: "Dakar, Louga, Kolda",
    statut: "ACTIF",
  },
  {
    id: 2,
    nom: "Action Contre la Faim",
    domaine: "Nutrition & Sécurité Alimentaire",
    zone: "Matam, Tambacounda",
    statut: "ACTIF",
  },
  {
    id: 3,
    nom: "Enda Tiers-Monde",
    domaine: "Forages Solaires & Assainissement",
    zone: "Thiès, Fatick",
    statut: "ACTIF",
  },
])

const partenairesFiltres = computed(() => {
  return partenaires.value.filter((p) => {
    const okRecherche = p.nom.toLowerCase().includes(recherche.value.toLowerCase())
    const okStatut = filtreStatut.value === "Tous les statuts" || p.statut === filtreStatut.value
    return okRecherche && okStatut
  })
})

function reinitialiserFiltres() {
  recherche.value = ""
  filtreStatut.value = "Tous les statuts"
}

function ajouterPartenaire() {
  const nom = prompt("Nom du partenaire :")
  if (nom) {
    partenaires.value.push({
      id: Date.now(),
      nom,
      domaine: "Humanitaire Général",
      zone: "Sénégal",
      statut: "ACTIF",
    })
  }
}

function supprimer(id) {
  partenaires.value = partenaires.value.filter((p) => p.id !== id)
}
</script>

