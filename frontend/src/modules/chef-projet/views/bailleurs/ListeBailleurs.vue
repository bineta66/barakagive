<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Bailleurs de fonds</h1>
        <p class="text-xs text-gray-500 mt-1">
          Partenaires institutionnels, agences multilatérales et mécènes finançant les interventions humanitaires.
        </p>
      </div>

      <BoutonPrimary @click="ajouterBailleur">
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
          placeholder="Rechercher par bailleur ou contact..."
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

    <!-- Section : Bailleurs -->
    <div class="space-y-4">
      <div class="bg-white px-4 py-3 inline-flex items-center gap-3">
        <Landmark :size="20" class="text-bleu-nuit" />
        <span class="text-base font-semibold text-slate-900">Bailleurs & Fonds Partenaires</span>
      </div>

      <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
            <tr>
              <th class="text-left px-4 py-3">BAILLEUR</th>
              <th class="text-left px-4 py-3">ORGANISATION / FONDATION</th>
              <th class="text-left px-4 py-3">POINT DE CONTACT</th>
              <th class="text-center px-4 py-3">STATUT</th>
              <th class="text-center px-4 py-3">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bailleur in bailleursFiltres" :key="bailleur.id" class="border-t hover:bg-slate-50">
              <td class="px-4 py-3">
                <p class="text-slate-900 text-sm font-semibold">{{ bailleur.nom }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-slate-900 text-xs">{{ bailleur.organisation }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-slate-900 text-xs">{{ bailleur.contact }}</p>
              </td>
              <td class="px-4 py-3 text-center">
                <StatusBadge :statut="bailleur.statut">{{ bailleur.statut }}</StatusBadge>
              </td>
              <td class="px-4 py-3">
                <div class="flex justify-center gap-1.5">
                  <button @click="supprimer(bailleur.id)" class="p-1 text-slate-400 hover:text-red-600">
                    <Trash2 :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
          <p class="text-slate-500">
            Affichage de {{ bailleursFiltres.length }} bailleur(s)
          </p>
        </div>
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { ref, computed } from "vue"
import { Plus, Search, Landmark, Trash2 } from "lucide-vue-next"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")

const bailleurs = ref([
  {
    id: 1,
    nom: "UNICEF Sénégal",
    organisation: "Agence des Nations Unies",
    contact: "dakar@unicef.org",
    statut: "ACTIF",
  },
  {
    id: 2,
    nom: "Union Européenne (ECHO)",
    organisation: "Aide Humanitaire Européenne",
    contact: "echo-dakar@ec.europa.eu",
    statut: "ACTIF",
  },
  {
    id: 3,
    nom: "USAID Bureau Humanitaire",
    organisation: "Gouvernement Américain",
    contact: "dakar-info@usaid.gov",
    statut: "ACTIF",
  },
])

const bailleursFiltres = computed(() => {
  return bailleurs.value.filter((b) => {
    const okRecherche =
      b.nom.toLowerCase().includes(recherche.value.toLowerCase()) ||
      b.contact.toLowerCase().includes(recherche.value.toLowerCase())
    const okStatut = filtreStatut.value === "Tous les statuts" || b.statut === filtreStatut.value
    return okRecherche && okStatut
  })
})

function reinitialiserFiltres() {
  recherche.value = ""
  filtreStatut.value = "Tous les statuts"
}

function ajouterBailleur() {
  const nom = prompt("Nom du bailleur de fonds :")
  if (nom) {
    bailleurs.value.push({
      id: Date.now(),
      nom,
      organisation: "Partenaire Institutionnel",
      contact: "contact@partenaire.org",
      statut: "ACTIF",
    })
  }
}

function supprimer(id) {
  bailleurs.value = bailleurs.value.filter((b) => b.id !== id)
}
</script>

