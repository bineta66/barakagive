<template>
  <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
        <tr>
          <th class="text-left px-4 py-3">Nom</th>
          <th class="text-left px-4">Région</th>
          <th class="text-left px-4">Département</th>
          <th class="text-right px-4">Rayon</th>
          <th class="text-left px-4">Statut</th>
          <th class="text-right px-4">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="zone in zones" :key="zone.id" class="border-t hover:bg-slate-50">
          <td class="px-4 py-3">
            <span class="font-semibold text-sm text-slate-800">{{ zone.nom }}</span>
          </td>

          <td class="px-4 text-xs text-slate-600">{{ zone.region }}</td>
<td class="px-4 text-xs text-slate-600">{{ zone.departement || "-" }}</td>

          <td class="px-4 text-right text-xs text-slate-600">
            {{ zone.rayon ? zone.rayon + ' m' : '-' }}
          </td>

          <td class="px-4">
            <span
              class="px-2 py-1 rounded text-xs font-semibold"
              :class="isActive(zone.statut) ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600'"
            >
              {{ isActive(zone.statut) ? 'Actif' : 'Inactif' }}
            </span>
          </td>

          <td class="px-4">
            <div class="flex justify-end gap-2">
              <RouterLink
                :to="`/chef-projet/zones/${zone.id}`"
                class="text-slate-500 hover:text-bleu-nuit p-1"
                title="Voir détails"
              >
                <Eye :size="16" />
              </RouterLink>

              <RouterLink
                :to="`/chef-projet/zones/modifier/${zone.id}`"
                class="text-slate-500 hover:text-or p-1"
                title="Modifier"
              >
                <Pencil :size="16" />
              </RouterLink>

              <button
                @click="$emit('delete', zone.id)"
                class="text-slate-500 hover:text-red-600 p-1"
                title="Supprimer"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </td>
        </tr>

        <tr v-if="!zones || zones.length === 0">
          <td colspan="6" class="px-4 py-6 text-center text-sm text-gray-500">
            Aucune zone enregistrée.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { Eye, Pencil, Trash2 } from "lucide-vue-next"
import { RouterLink } from "vue-router"

defineProps({
  zones: {
    type: Array,
    default: () => [],
  },
})

defineEmits(["delete"])

const isActive = (statut) => {
  return statut === true || statut === "Actif" || statut === "ACTIF"
}
</script>

