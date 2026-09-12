<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-3xl font-bold text-amber-800">Modifier la campagne</h1>
        <p class="text-xs text-gray-500 mt-1">
          Modifiez les informations de la campagne.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/campagnes">
          <List :size="18" />
          Liste des campagnes
        </BoutonSecondary>
      </div>
    </div>

    <!-- Formulaire -->
    <div class="max-w-2xl" v-if="campagne">
      <form @submit.prevent="modifierCampagne" class="space-y-6">
        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Nom de la campagne</label>
          <input v-model="form.nom" type="text" class="w-full h-12 rounded-md border border-slate-300 px-4" required />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Projet</label>
          <select v-model="form.projet" class="w-full h-12 rounded-md border border-slate-300 px-4" required>
            <option value="">Sélectionner un projet</option>
            <option>Projet Santé</option>
            <option>Projet Nutrition</option>
            <option>Projet Eau</option>
            <option>Projet Education</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Zone</label>
          <select v-model="form.zone" class="w-full h-12 rounded-md border border-slate-300 px-4" required>
            <option value="">Sélectionner une zone</option>
            <option>Dakar</option>
            <option>Louga</option>
            <option>Kolda</option>
            <option>Matam</option>
            <option>Thiès</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Date de début</label>
            <input v-model="form.dateDebut" type="date" class="w-full h-12 rounded-md border border-slate-300 px-4" required />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Date de fin</label>
            <input v-model="form.dateFin" type="date" class="w-full h-12 rounded-md border border-slate-300 px-4" required />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Statut</label>
          <select v-model="form.statut" class="w-full h-12 rounded-md border border-slate-300 px-4" required>
            <option value="Planifiée">Planifiée</option>
            <option value="En cours">En cours</option>
            <option value="Terminée">Terminée</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Description</label>
          <textarea v-model="form.description" rows="4" class="w-full rounded-md border border-slate-300 px-4 py-3"></textarea>
        </div>

        <button
          type="submit"
          class="w-full h-12 rounded-md bg-yellow-800 hover:bg-yellow-900 text-white font-semibold uppercase transition"
        >
          Enregistrer les modifications
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue"
import { useRoute, RouterLink } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import { campagnesMock } from "@/data/campagnesMock.js"

const route = useRoute()

const campagne = ref(null)

const form = reactive({
  nom: "",
  projet: "",
  zone: "",
  dateDebut: "",
  dateFin: "",
  statut: "Planifiée",
  description: "",
})

onMounted(() => {
  const id = Number(route.params.id)
  const found = campagnesMock.value.find((c) => c.id === id)
  if (found) {
    campagne.value = found
    Object.assign(form, found)
  }
})

const modifierCampagne = () => {
  const index = campagnesMock.value.findIndex((c) => c.id === campagne.value.id)
  if (index !== -1) {
    campagnesMock.value[index] = { ...campagne.value, ...form }
    alert("Campagne modifiée avec succès !")
  }
}
</script>
