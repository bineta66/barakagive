<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-4 mb-6 shadow-[0px_1px_2px_0px_rgba(0,0,0,0.05)]">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          :value="recherche"
          @input="$emit('update:recherche', $event.target.value)"
          type="text"
          placeholder="Rechercher un bénéficiaire..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select
        :value="regionSelectionnee"
        @change="$emit('update:regionSelectionnee', $event.target.value)"
        class="border rounded-lg px-3 py-2 text-sm"
      >
        <option value="">Toutes les régions</option>
        <option v-for="region in regions" :key="region" :value="region">
          {{ region }}
        </option>
      </select>

      <select
        :value="zoneSelectionnee"
        @change="$emit('update:zoneSelectionnee', $event.target.value)"
        class="border rounded-lg px-3 py-2 text-sm"
      >
        <option value="">Toutes les zones</option>
        <option v-for="zone in zones" :key="zone" :value="zone">
          {{ zone }}
        </option>
      </select>

      <select
        :value="filtreStatut"
        @change="$emit('update:filtreStatut', $event.target.value)"
        class="border rounded-lg px-3 py-2 text-sm"
      >
        <option value="">Tous les statuts</option>
        <option value="Critique">Critique</option>
        <option value="Élevé">Élevé</option>
        <option value="Modéré">Modéré</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { Search } from "lucide-vue-next"

defineProps({
  recherche: String,
  regionSelectionnee: String,
  zoneSelectionnee: String,
  filtreStatut: String,
  regions: Array,
  zones: Array,
})

defineEmits(["update:recherche", "update:regionSelectionnee", "update:zoneSelectionnee", "update:filtreStatut"])
</script>
