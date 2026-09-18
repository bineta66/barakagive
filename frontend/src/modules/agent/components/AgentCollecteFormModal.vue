<template>
  <div
    @click.self="handleClose"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
  >
    <div class="bg-white border border-slate-200 rounded-xl shadow-xs-sm w-full max-w-lg mx-4">
      <!-- Header -->
      <div class="px-6 py-4  flex items-center justify-between">
        <h2 class="text-xl font-bold text-slate-900">Nouvelle collecte terrain</h2>
        <button
          @click="handleClose"
          class="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-bleu-nuit rounded-full hover:bg-bleu-nuit/10 transition"
        >
          <X :size="20" />
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-4">
        <div class="space-y-4">
          <!-- Date -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">
              Date de la collecte
            </label>
            <input
              v-model="form.date"
              type="date"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
            />
          </div>

          <!-- Campagne -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">
              Campagne
            </label>
            <select
              v-model="form.campagne"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
            >
              <option value="">Sélectionner une campagne</option>
              <option value="Collecte de médicaments">Collecte de médicaments</option>
              <option value="Vaccination">Vaccination</option>
              <option value="Distribution alimentaire">Distribution alimentaire</option>
            </select>
          </div>

          <!-- Zone -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">
              Zone géographique
            </label>
            <select
              v-model="form.zone"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
            >
              <option value="">Sélectionner une zone</option>
              <option value="Dakar Est">Dakar Est</option>
              <option value="Dakar Nord">Dakar Nord</option>
              <option value="Pikine">Pikine</option>
            </select>
          </div>

          <!-- Montant -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">
              Montant collecté (FCFA)
            </label>
            <input
              v-model.number="form.montant"
              type="number"
              placeholder="0"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
            />
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-slate-200 flex gap-3 justify-end">
        <button
          @click="handleClose"
          class="px-4 py-2 border border-slate-200 rounded-lg text-bleu-nuit hover:bg-bleu-nuit/10 transition"
        >
          Annuler
        </button>
        <button
          @click="handleSubmit"
          class="px-4 py-2 bg-bleu-nuit text-white rounded-lg hover:bg-[#01111eff] transition"
        >
          Enregistrer
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { X } from "lucide-vue-next"

const emit = defineEmits(["close"])

const form = ref({
  date: "",
  campagne: "",
  zone: "",
  montant: 0,
})

const handleClose = () => {
  emit("close")
}

const handleSubmit = () => {
  console.log("Nouvelle collecte:", form.value)
  emit("close")
}
</script>






