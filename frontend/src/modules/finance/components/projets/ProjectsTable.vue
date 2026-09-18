<template>
  <div class="bg-white border border-slate-200/60 rounded-xl shadow-xs overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 ">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-slate-900">Projet</th>
            <th class="text-left px-4 py-3 font-medium text-slate-900">Chef de projet</th>
            <th class="text-left px-4 py-3 font-medium text-slate-900">Région</th>
            <th class="text-left px-4 py-3 font-medium text-slate-900">Budget alloué</th>
            <th class="text-left px-4 py-3 font-medium text-slate-900">Statut</th>
            <th class="text-center px-4 py-3 font-medium text-slate-900">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="project in projects" :key="project.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3">
              <div class="flex flex-col">
                <span class="font-semibold text-slate-800">{{ project.nom }}</span>
                <span class="text-xs text-slate-500">{{ project.code }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-slate-700">{{ project.chefProjet }}</td>
            <td class="px-4 py-3 text-slate-700">{{ project.region }}</td>
            <td class="px-4 py-3 font-semibold text-slate-800">{{ formatCurrency(project.budget) }} FCFA</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="project.statut">{{ project.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <button
                @click="$emit('open-project', project)"
                class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                title="Ouvrir le projet"
              >
                <Eye class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between px-4 py-3 border-t border-slate-200">
      <p class="text-xs text-slate-500">
        Affichage de {{ startItem }}-{{ endItem }} sur {{ totalItems }} projets
      </p>
      <div class="flex items-center gap-2">
        <button
          :disabled="currentPage === 1"
          @click="$emit('page-change', currentPage - 1)"
          class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <div class="flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="$emit('page-change', page)"
            :class="[
              'px-2.5 py-1 rounded text-sm font-medium transition-colors',
              page === currentPage
                ? 'bg-or text-white'
                : 'text-bleu-nuit hover:bg-bleu-nuit/10'
            ]"
          >
            {{ page }}
          </button>
        </div>
        <button
          :disabled="currentPage === totalPages"
          @click="$emit('page-change', currentPage + 1)"
          class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Eye, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  projects: { type: Array, default: () => [] },
  currentPage: { type: Number, default: 1 },
  itemsPerPage: { type: Number, default: 5 },
  totalItems: { type: Number, default: 0 },
})

defineEmits(['page-change', 'open-project'])

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.totalItems / props.itemsPerPage))
)

const startItem = computed(() =>
  props.totalItems === 0 ? 0 : (props.currentPage - 1) * props.itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(props.currentPage * props.itemsPerPage, props.totalItems)
)

const visiblePages = computed(() => {
  const total = totalPages.value
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1)

  const current = props.currentPage
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)

  if (end === total) start = Math.max(1, end - 4)

  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const formatCurrency = (value) =>
  new Intl.NumberFormat('fr-FR').format(value)

const badgeClass = (statut) => {
  switch (statut) {
    case 'Budgétisé':
      return 'bg-or/10 text-bleu-nuit'
    case 'En cours':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    case 'À budgétiser':
      return 'bg-or/10 text-or'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}
</script>


