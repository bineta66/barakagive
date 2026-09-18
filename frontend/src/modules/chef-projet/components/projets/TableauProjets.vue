<template>
  <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
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
          :key="projet.id || projet.code"
          class="border-t hover:bg-slate-50"
        >
          <td class="px-4 py-4">
            <h3 class="font-semibold text-sm text-slate-800">
              {{ projet.name || projet.nom }}
            </h3>
            <p class="text-xs text-gray-500">{{ projet.code }}</p>
          </td>

          <td class="px-4 text-right text-sm font-semibold">
            {{ formatBudget(projet.budget) }}
          </td>

          <td class="px-4 text-xs text-slate-600">
            {{ projet.start_date || projet.debut || "-" }}
          </td>

          <td class="px-4 text-xs text-slate-600">
            {{ projet.end_date || projet.fin || "-" }}
          </td>

          <td class="px-4">
            <span
              class="px-2.5 py-1 text-xs font-semibold rounded-full"
              :class="projet.archived ? 'bg-slate-100 text-slate-600' : 'bg-emerald-50 text-emerald-700'"
            >
              {{ projet.archived ? 'Archivé' : (projet.statut || 'En cours') }}
            </span>
          </td>

          <td class="px-4">
            <div class="flex justify-end gap-2">
              <RouterLink
                :to="`/chef-projet/projets/${projet.id || projet.code}`"
                class="text-slate-500 hover:text-bleu-nuit p-1"
                title="Voir détails"
              >
                <Eye :size="18" />
              </RouterLink>

              <button
                v-if="canManage && !projet.archived"
                @click="$emit('delete', projet.id)"
                class="text-slate-500 hover:text-red-600 p-1"
                title="Archiver"
              >
                <Trash2 :size="18" />
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!projects || projects.length === 0" class="p-8 text-center text-sm text-slate-500">
      Aucun projet trouvé.
    </div>

    <!-- Pagination -->
    <div v-else class="flex items-center justify-between px-4 py-3 border-t text-xs">
      <p class="text-slate-500">
        Affichage de {{ projects.length }} projet(s)
      </p>
    </div>
  </div>
</template>

<script setup>
import { Eye, Trash2 } from "lucide-vue-next"
import { RouterLink } from "vue-router"

defineProps({
  projects: {
    type: Array,
    default: () => [],
  },
  canManage: {
    type: Boolean,
    default: true,
  },
})

defineEmits(["delete"])

const formatBudget = (val) => {
  if (!val && val !== 0) return "-"
  return new Intl.NumberFormat("fr-FR").format(val) + " FCFA"
}
</script>


