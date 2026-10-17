<template>
  <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-5 gap-3">
    <div class="relative">
      <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
      <input
        :value="recherche"
        @input="$emit('update:recherche', $event.target.value)"
        type="text"
        placeholder="Rechercher une campagne..."
        class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
      />
    </div>

    <select
      :value="filtreStatut"
      @change="$emit('update:filtreStatut', $event.target.value)"
      class="border rounded-lg px-3 py-2 text-sm"
    >
      <option>Tous les statuts</option>
      <option>En cours</option>
      <option>Planifiée</option>
      <option>Terminée</option>
    </select>

    <select
      :value="filtreProjet"
      @change="$emit('update:filtreProjet', $event.target.value)"
      class="border rounded-lg px-3 py-2 text-sm"
    >
      <option>Tous les projets</option>
      <option>Projet Santé</option>
      <option>Projet Nutrition</option>
      <option>Projet Eau</option>
      <option>Projet Education</option>
    </select>

    <select
      :value="filtreZone"
      @change="$emit('update:filtreZone', $event.target.value)"
      class="border rounded-lg px-3 py-2 text-sm"
    >
      <option>Toutes les zones</option>
      <option>Dakar</option>
      <option>Louga</option>
      <option>Kolda</option>
      <option>Matam</option>
      <option>Thiès</option>
    </select>

    <BoutonTertiary @click="$emit('reset')">
      Réinitialiser
    </BoutonTertiary>
  </div>
</template>

<script setup>
import { Search } from "lucide-vue-next"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"

defineProps({
  recherche: String,
  filtreStatut: String,
  filtreProjet: String,
  filtreZone: String,
})

defineEmits([
  "update:recherche",
  "update:filtreStatut",
  "update:filtreProjet",
  "update:filtreZone",
  "reset",
])
</script>


