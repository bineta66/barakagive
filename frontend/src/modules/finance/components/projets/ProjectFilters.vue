<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-4 grid md:grid-cols-4 gap-3">
    <div class="relative">
      <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
      <input
        type="text"
        :value="search"
        @input="$emit('update:search', $event.target.value)"
        placeholder="Rechercher un projet..."
        class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
      />
    </div>

    <select
      :value="statut"
      @change="$emit('update:statut', $event.target.value)"
      class="border rounded-lg px-3 py-2 text-sm"
    >
      <option value="">Tous les statuts</option>
      <option v-for="s in statuts" :key="s" :value="s">{{ s }}</option>
    </select>

    <select
      :value="chef"
      @change="$emit('update:chef', $event.target.value)"
      class="border rounded-lg px-3 py-2 text-sm"
    >
      <option value="">Tous les chefs</option>
      <option v-for="c in chefs" :key="c" :value="c">{{ c }}</option>
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
  search: { type: String, default: '' },
  statut: { type: String, default: '' },
  chef: { type: String, default: '' },
  statuts: { type: Array, default: () => [] },
  chefs: { type: Array, default: () => [] },
})

defineEmits(['update:search', 'update:statut', 'update:chef', 'reset'])
</script>
