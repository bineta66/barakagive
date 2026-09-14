<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">ONG</h1>
        <p class="text-sm text-slate-500 mt-1">
          GÃ©rer les organisations enregistrÃ©es sur la plateforme
        </p>
      </div>
      <div class="flex gap-2">
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher une ONG..."
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30 w-64"
        />
        <select
          v-model="filtreStatut"
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
        >
          <option value="tous">Tous les statuts</option>
          <option value="Actif">Actives</option>
          <option value="Inactif">Inactives</option>
        </select>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
      <KpiCard
        titre="ONG totales"
        :valeur="statistiques.totalONG"
        :icone="Building2"
        couleur="sky"
      />
      <KpiCard
        titre="ONG actives"
        :valeur="statistiques.ongActives"
        :icone="Activity"
        couleur="emerald"
      />
      <KpiCard
        titre="Total utilisateurs"
        :valeur="statistiques.totalUtilisateurs"
        :icone="Users"
        couleur="purple"
      />
      <KpiCard
        titre="Total projets"
        :valeur="statistiques.totalProjets"
        :icone="FolderKanban"
        couleur="amber"
      />
    </div>

    <!-- Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Contact
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Pays
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Date crÃ©ation
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Utilisateurs
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Projets
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="ong in ongsFiltrees" :key="ong.id">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                    <Building2 :size="16" class="text-slate-600" />
                  </div>
                  <div class="text-sm font-medium text-slate-900">
                    {{ ong.nom }}
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-slate-600">{{ ong.email }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ ong.pays }}</td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ ong.dateCreation }}
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ ong.utilisateurs }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ ong.projets }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                  :class="
                    ong.statut === 'Actif'
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-slate-700 bg-slate-100'
                  "
                >
                  {{ ong.statut }}
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
import { ref, computed } from "vue"
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import {
  Building2,
  Activity,
  Users,
  FolderKanban,
} from "lucide-vue-next"
import KpiCard from "@/components/ui/KpiCard.vue"

const store = useSuperAdminStore()
const { ongs, statistiques } = store

const search = ref("")
const filtreStatut = ref("tous")

const ongsFiltrees = computed(() => {
  let result = ongs.value
  if (search.value) {
    result = result.filter((o) =>
      o.nom.toLowerCase().includes(search.value.toLowerCase())
    )
  }
  if (filtreStatut.value !== "tous") {
    result = result.filter((o) => o.statut === filtreStatut.value)
  }
  return result
})
</script>





