<template>
  <tr class="border-t hover:bg-slate-50">
    <td class="px-4 py-4">
      <h3 class="font-semibold text-sm text-slate-800">
        {{ campagne.nom }}
      </h3>
      <p class="text-xs text-gray-500">{{ campagne.code }}</p>
    </td>

    <td class="px-4 text-sm text-slate-600">
      {{ campagne.projet }}
    </td>

    <td class="px-4 text-sm text-slate-600">
      {{ campagne.zone }}
    </td>

    <td class="px-4">
      <span
        class="px-2 py-1 rounded text-xs font-semibold"
        :class="{
          'bg-emerald-100 text-emerald-700': campagne.statut === 'En cours',
          'bg-gray-100 text-gray-600': campagne.statut === 'Planifiée',
          'bg-sky-100 text-sky-700': campagne.statut === 'Terminée',
        }"
      >
        {{ campagne.statut }}
      </span>
    </td>

    <td class="px-4">
      <div class="flex justify-end gap-2">
        <RouterLink :to="`/chef-projet/campagnes/${campagne.id}`" class="text-slate-500 hover:text-sky-700">
          <Eye :size="18" />
        </RouterLink>

        <RouterLink :to="`/chef-projet/campagnes/modifier/${campagne.id}`" class="text-slate-500 hover:text-amber-700">
          <Pencil :size="18" />
        </RouterLink>

        <button class="text-slate-500 hover:text-red-600">
          <Archive :size="18" />
        </button>
      </div>
    </td>
  </tr>
</template>

<script setup>
import { Eye, Pencil, Archive } from "lucide-vue-next"
import { RouterLink } from "vue-router"

defineProps({
  campagne: {
    type: Object,
    required: true,
  },
})
</script>
