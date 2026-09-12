<template>
  <div class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden">
    <div class="p-8">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-2xl font-bold text-amber-800 mb-1">
            {{ projet.nom }}
          </h2>
          <p class="text-sm text-gray-500">{{ projet.code }}</p>
        </div>
        <StatutProjet :status="projet.statut" />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-semibold uppercase text-slate-900 mb-1">
            Responsable
          </p>
          <p class="text-sm text-gray-700">{{ projet.responsable }}</p>
        </div>

        <div>
          <p class="text-xs font-semibold uppercase text-slate-900 mb-1">
            Zone d'intervention
          </p>
          <p class="text-sm text-gray-700">{{ projet.zone }}</p>
        </div>

        <div>
          <p class="text-xs font-semibold uppercase text-slate-900 mb-1">
            Budget
          </p>
          <p class="text-sm text-gray-700 font-semibold">{{ projet.budget }}</p>
        </div>

        <div>
          <p class="text-xs font-semibold uppercase text-slate-900 mb-1">
            Dates
          </p>
          <p class="text-sm text-gray-700">
            {{ projet.debut }} - {{ projet.fin }}
          </p>
        </div>
      </div>

      <div class="mt-6 pt-6 border-t border-gray-100">
        <p class="text-sm text-gray-700">
          {{ projet.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatutProjet from "./StatutProjet.vue"

defineProps({
  projet: {
    type: Object,
    default: () => ({
      nom: "",
      code: "",
      responsable: "",
      zone: "",
      budget: "",
      debut: "",
      fin: "",
      statut: "Planifié",
      description: "",
    }),
  },
})
</script>
