<template>
  <div class="bg-white border border-slate-200/60 rounded-xl shadow-xs-[0px_1px_2px_0px_rgba(0,0,0,0.05)] overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-4">Identifiant</th>
            <th class="text-left px-4">Nom</th>
            <th class="text-left px-4">Région</th>
            <th class="text-left px-4">Zone</th>
            <th class="text-left px-4">Campagne</th>
            <th class="text-left px-4">Score IA</th>
            <th class="text-left px-4">Statut</th>
            <th class="text-right px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="beneficiaire in beneficiaires" :key="beneficiaire.id" class="border-t hover:bg-slate-50">
            <td class="px-4 py-4 text-sm text-slate-600">{{ beneficiaire.id }}</td>
            <td class="px-4 py-4">
              <h3 class="font-semibold text-sm text-slate-800">
                {{ beneficiaire.prenom }} {{ beneficiaire.nom }}
              </h3>
            </td>
            <td class="px-4 py-4 text-sm text-slate-600">{{ beneficiaire.region }}</td>
            <td class="px-4 py-4 text-sm text-slate-600">{{ beneficiaire.zone }}</td>
            <td class="px-4 py-4 text-sm text-slate-600">{{ beneficiaire.campagne }}</td>
            <td class="px-4 py-4 text-sm text-slate-600">{{ beneficiaire.scoreIA }}</td>
            <td class="px-4 py-4">
               <StatusBadge :statut="beneficiaire.statut">{{ beneficiaire.statut }}</StatusBadge>
            </td>
            <td class="px-4">
              <div class="flex justify-end">
                <button class="text-slate-500 hover:text-bleu-nuit">
                  <Eye :size="18" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { Eye } from "lucide-vue-next"

defineProps({
  beneficiaires: {
    type: Array,
    required: true,
  },
})
</script>


