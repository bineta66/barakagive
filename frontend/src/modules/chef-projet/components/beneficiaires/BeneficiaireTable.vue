<template>
  <div class="bg-white border border-slate-200/60 rounded-xl shadow-[0px_1px_2px_0px_rgba(0,0,0,0.05)] overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-sky-900">
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
              <span
                class="px-2 py-1 rounded text-xs font-semibold"
                :class="{
                  'bg-red-100 text-red-700': beneficiaire.statut === 'Critique',
                  'bg-orange-100 text-orange-700': beneficiaire.statut === 'Élevé',
                  'bg-gray-100 text-gray-600': beneficiaire.statut === 'Modéré',
                }"
              >
                {{ beneficiaire.statut }}
              </span>
            </td>
            <td class="px-4">
              <div class="flex justify-end">
                <button class="text-slate-500 hover:text-sky-900">
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
import { Eye } from "lucide-vue-next"

defineProps({
  beneficiaires: {
    type: Array,
    required: true,
  },
})
</script>
