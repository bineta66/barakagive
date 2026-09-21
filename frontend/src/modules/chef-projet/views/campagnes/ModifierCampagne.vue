<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Modifier la campagne</h1>
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

    <LoadingSpinner v-if="loading" message="Chargement des données de la campagne..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Formulaire -->
    <div class="max-w-2xl" v-if="!loading && form.nom">
      <form @submit.prevent="modifierCampagne" class="space-y-6">
        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Nom de la campagne *</label>
          <input
            v-model="form.nom"
            type="text"
            class="w-full h-12 rounded-md border border-slate-300 px-4 focus:ring-2 focus:ring-or/30 outline-none text-sm"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Zones d'intervention</label>
          <div class="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto border rounded-lg p-3 bg-slate-50">
            <label
              v-for="z in zoneStore.zones"
              :key="z.id"
              class="flex items-center gap-2 p-1.5 rounded hover:bg-white cursor-pointer text-sm"
            >
              <input
                type="checkbox"
                :value="z.id"
                v-model="form.zone_ids"
                class="rounded text-bleu-nuit focus:ring-or/30"
              />
              <span>{{ z.nom }} ({{ z.region }})</span>
            </label>
          </div>
        </div>

<div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Date de début *</label>
            <input
              v-model="form.date_debut"
              type="date"
              class="w-full h-12 rounded-md border border-slate-300 px-4 text-sm"
              required
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Date de fin *</label>
            <input
              v-model="form.date_fin"
              type="date"
              class="w-full h-12 rounded-md border border-slate-300 px-4 text-sm"
              required
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Statut *</label>
            <select
              v-model="form.statut"
              class="w-full h-12 rounded-md border border-slate-300 px-4 text-sm"
              required
            >
              <option value="BROUILLON">Brouillon</option>
              <option value="PLANIFIER">Planifiée</option>
              <option value="EN_COURS">En cours</option>
              <option value="TERMINE">Terminée</option>
              <option value="ANNULEE">Annulée</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-gray-800 mb-2">Description</label>
          <textarea
            v-model="form.description"
            rows="4"
            class="w-full rounded-md border border-slate-300 px-4 py-3 text-sm focus:ring-2 focus:ring-or/30 outline-none"
          ></textarea>
        </div>

        <button
          type="submit"
          :disabled="submitting"
          class="w-full h-12 rounded-md bg-or hover:bg-[#6b4203] text-white font-semibold uppercase transition disabled:opacity-50"
        >
          {{ submitting ? "Enregistrement..." : "Enregistrer les modifications" }}
        </button>
</form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"
import { useZoneStore } from "@/stores/zone.js"

const route = useRoute()
const router = useRouter()
const campaignStore = useCampaignStore()
const zoneStore = useZoneStore()

const loading = ref(true)
const submitting = ref(false)
const feedback = reactive({ type: "success", message: "" })

const form = reactive({
  nom: "",
  description: "",
  zone_ids: [],
  date_debut: "",
  date_fin: "",
  statut: "PLANIFIER",
})

onMounted(async () => {
  loading.value = true
  try {
    await zoneStore.fetchZones()
const data = await campaignStore.fetchCampaign(route.params.id)
    form.nom = data.nom || ""
    form.description = data.description || ""
    form.date_debut = data.date_debut || ""
    form.date_fin = data.date_fin || ""
    form.statut = data.statut || "PLANIFIER"
    form.zone_ids = (data.zones || []).map((z) => z.id)
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Erreur lors du chargement de la campagne."
  } finally {
    loading.value = false
  }
})

const modifierCampagne = async () => {
  submitting.value = true
  feedback.message = ""
  try {
await campaignStore.updateCampaign(route.params.id, {
      nom: form.nom,
      description: form.description,
      date_debut: form.date_debut,
      date_fin: form.date_fin,
      zone_ids: form.zone_ids,
      statut: form.statut,
    })
    feedback.type = "success"
    feedback.message = "Campagne modifiée avec succès !"
    setTimeout(() => {
      router.push("/chef-projet/campagnes")
    }, 800)
  } catch (err) {
    feedback.type = "error"
    feedback.message = campaignStore.error || "Erreur lors de la modification de la campagne."
  } finally {
    submitting.value = false
  }
}
</script>

