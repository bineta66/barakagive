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
      {{ typeCampagneLabel(campagne.type) }}
    </td>

    <td class="px-4 text-sm text-slate-600">
      {{ campagne.zone }}
    </td>

    <td class="px-4">
       <StatusBadge :statut="campagne.statut">{{ campagne.statut }}</StatusBadge>
    </td>

    <td class="px-4">
      <div class="flex justify-end gap-2">
        <RouterLink :to="`/chef-projet/campagnes/${campagne.id}`" class="text-slate-500 hover:text-bleu-nuit">
          <Eye :size="18" />
        </RouterLink>

        <RouterLink :to="`/chef-projet/campagnes/modifier/${campagne.id}`" class="text-slate-500 hover:text-bleu-nuit">
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
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { Eye, Pencil, Archive } from "lucide-vue-next"
import { RouterLink } from "vue-router"

const typeCampagneLabel = (type) => ({
  COLLECTE: "Collecte de fonds (ancien type)",
  COLLECTE_BESOINS: "Collecte des besoins",
  DISTRIBUTION: "Distribution",
  SANTE: "Santé",
  ALIMENTATION: "Alimentation",
  URGENCE: "Urgence",
  SENSIBILISATION: "Sensibilisation",
  SUIVI_EVALUATION: "Suivi et évaluation",
}[type] || "—")

defineProps({
  campagne: {
    type: Object,
    required: true,
  },
})
</script>

