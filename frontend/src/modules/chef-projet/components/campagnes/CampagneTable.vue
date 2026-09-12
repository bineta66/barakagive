<template>
  <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-sky-900">
        <tr>
          <th class="text-left px-4 py-4">Campagne</th>
          <th class="text-left px-4">Projet</th>
          <th class="text-left px-4">Zone</th>
          <th class="text-left px-4">Statut</th>
          <th class="text-right px-4">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="campagne in campagnes" :key="campagne.id">
          <CampagneRow :campagne="campagne" />
        </tr>
      </tbody>
    </table>

    <CampagnePagination
      :page-courante="pageCourante"
      :total-pages="totalPages"
      @change-page="pageCourante = $event"
    />
  </div>
</template>

<script setup>
import CampagneRow from "./CampagneRow.vue"
import CampagnePagination from "./CampagnePagination.vue"

defineProps({
  campagnes: {
    type: Array,
    default: () => [],
  },
  pageCourante: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
})
</script>
