<template>
  <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-sky-900">
        <tr>
          <th class="text-left px-4 py-4">Projet</th>
          <th class="text-right px-4">Budget</th>
          <th class="text-left px-4">Début</th>
          <th class="text-left px-4">Fin</th>
          <th class="text-left px-4">Statut</th>
          <th class="text-right px-4">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="projet in projects"
          :key="projet.code"
          class="border-t hover:bg-slate-50"
        >
          <td class="px-4 py-4">
            <h3 class="font-semibold text-sm text-slate-800">
              {{ projet.nom }}
            </h3>
            <p class="text-xs text-gray-500">{{ projet.code }}</p>
          </td>

          <td class="px-4 text-right text-sm font-semibold">
            {{ projet.budget }}
          </td>

          <td class="px-4 text-xs text-slate-600">
            {{ projet.debut }}
          </td>

          <td class="px-4 text-xs text-slate-600">
            {{ projet.fin }}
          </td>

          <td class="px-4">
            <StatutProjet :status="projet.statut" />
          </td>

          <td class="px-4">
            <div class="flex justify-end gap-2">
              <RouterLink :to="`/chef-projet/projets/${projet.code}`" class="text-slate-500 hover:text-sky-700">
                <Eye :size="18" />
              </RouterLink>

              <RouterLink :to="`/chef-projet/projets/modifier/${projet.code}`" class="text-slate-500 hover:text-amber-700">
                <Pencil :size="18" />
              </RouterLink>

              <button class="text-slate-500 hover:text-red-600">
                <Trash2 :size="18" />
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
      <p class="text-slate-500">
        Affichage de 1 à {{ projects?.length ?? 0 }} sur {{ projects?.length ?? 0 }} projets
      </p>

      <div class="flex gap-1">
        <button class="px-3 py-2 border rounded bg-slate-100 text-slate-400">
          Précédent
        </button>

        <button class="w-8 h-8 bg-green-900 text-white rounded">1</button>
        <button class="w-8 h-8 border rounded">2</button>
        <button class="w-8 h-8 border rounded">3</button>

        <button class="px-3 py-2 border rounded">Suivant</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Eye, Pencil, Trash2 } from "lucide-vue-next"
import { RouterLink } from "vue-router"
import StatutProjet from "./StatutProjet.vue"

defineProps({
  projects: {
    type: Array,
    default: () => [],
  },
})
</script>
