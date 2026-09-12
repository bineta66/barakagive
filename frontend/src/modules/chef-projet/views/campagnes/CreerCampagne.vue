<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 inline-flex flex-col justify-start items-start p-8">
    <div class="self-stretch mb-6">
      <h2 class="text-3xl font-bold text-amber-800">Créer une nouvelle campagne</h2>
      <p class="text-gray-600 text-sm mt-1">Configurez les paramètres de base et les zones de déploiement.</p>
    </div>

    <div class="self-stretch flex flex-col justify-start items-start gap-6">
      <!-- Section 1 -->
      <div class="self-stretch border-b border-gray-100 pb-8">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-amber-800">1. Identification</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Nom de la campagne *</label>
            <input
              v-model="form.nom"
              type="text"
              placeholder="Ex : Distribution Alimentaire d'Urgence Hivernage 2026"
              class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 focus:ring-2 focus:ring-amber-700 outline-none"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Projet humanitaire rattaché *</label>
            <select
              v-model="form.projet"
              class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 focus:ring-2 focus:ring-amber-700 outline-none"
            >
              <option value="">Sélectionner un projet parent...</option>
              <option value="1">Projet A</option>
              <option value="2">Projet B</option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Code campagne</label>
            <div class="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 font-semibold text-blue-900">
              {{ form.code }}
            </div>
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Description courte *</label>
            <textarea
              v-model="form.description"
              rows="4"
              placeholder="Décrivez succinctement l'objectif de la campagne..."
              class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 focus:ring-2 focus:ring-amber-700 outline-none"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Section 2 -->
      <div class="self-stretch border-b border-gray-100 pb-8">
        <div class="flex items-center gap-3 mb-6">
         
          <h3 class="text-xl font-bold text-amber-800">2. Zones d'intervention</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Régions *</label>
            <div class="relative">
              <button
                type="button"
                @click="showRegionDropdown = !showRegionDropdown"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 text-left flex justify-between items-center focus:ring-2 focus:ring-amber-700 outline-none"
              >
                <span :class="form.zones.length ? 'text-gray-800' : 'text-gray-400'">
                  {{ form.zones.length ? `${form.zones.length} région(s) sélectionnée(s)` : 'Sélectionner des régions...' }}
                </span>
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>
              <div v-if="showRegionDropdown" class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                <div v-for="region in regions" :key="region" class="px-4 py-2 hover:bg-gray-50 cursor-pointer flex items-center gap-2" @click="toggleRegion(region)">
                  <div class="w-4 h-4 border rounded flex items-center justify-center" :class="form.zones.includes(region) ? 'bg-sky-900 border-sky-900' : 'border-gray-300'">
                    <svg v-if="form.zones.includes(region)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  <span class="text-sm text-gray-700">{{ region }}</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Zones concernées *</label>
            <div class="relative">
              <button
                type="button"
                @click="showZoneDropdown = !showZoneDropdown"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 text-left flex justify-between items-center focus:ring-2 focus:ring-amber-700 outline-none"
              >
                <span :class="form.zonesPrioritaires.length ? 'text-gray-800' : 'text-gray-400'">
                  {{ form.zonesPrioritaires.length ? `${form.zonesPrioritaires.length} zone(s) sélectionnée(s)` : 'Sélectionner des zones...' }}
                </span>
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>
              <div v-if="showZoneDropdown" class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg">
                <div class="p-2 border-b border-gray-200">
                  <input
                    v-model="zoneSearch"
                    type="text"
                    placeholder="Rechercher..."
                    class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-700 outline-none"
                    @click.stop
                  />
                </div>
                <div class="max-h-48 overflow-y-auto">
                  <div v-for="zone in filteredZones" :key="zone" class="px-4 py-2 hover:bg-gray-50 cursor-pointer flex items-center gap-2" @click="toggleZone(zone)">
                    <div class="w-4 h-4 border rounded flex items-center justify-center" :class="form.zonesPrioritaires.includes(zone) ? 'bg-sky-900 border-sky-900' : 'border-gray-300'">
                      <svg v-if="form.zonesPrioritaires.includes(zone)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                    <span class="text-sm text-gray-700">{{ zone }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 3 -->
      <div class="self-stretch">
        <div class="flex items-center gap-3 mb-6">
          
          <h3 class="text-xl font-bold text-amber-800">3. Calendrier</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Date de début *</label>
            <input
              v-model="form.dateDebut"
              type="date"
              class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Date de fin *</label>
            <input
              v-model="form.dateFin"
              type="date"
              class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="self-stretch bg-gray-50 border-t border-gray-100 mt-8 p-6 flex justify-between items-center">
      <div class="flex items-center gap-2 text-xs text-gray-600">
        <div class="w-3 h-3.5 bg-gray-800 relative"></div>
        <span>Vérification automatique des données conforme OCHA.</span>
      </div>

      <div class="flex gap-4">
        <BoutonSecondary type="button">
          Annuler
        </BoutonSecondary>
        <BoutonPrimary type="submit">
          <div class="w-4 h-4 bg-white rounded"></div>
          Créer et activer la campagne
        </BoutonPrimary>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue"
import { useRouter } from "vue-router"
import { campagnesMock } from "@/data/campagnesMock.js"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"

const router = useRouter()

const regions = ["Dakar", "Thiès", "Kaolack", "Saint-Louis", "Fatick", "Ziguinchor", "Tambacounda", "Kolda", "Matam", "Kaffrine", "Kédougou", "Sédhiou", "Louga"]

const zones = [
  "Pikine Est", "Guédiawaye", "Kaolack Nord", "Ndiaffate", "Thiès Ouest", "Mboro", "Tivaouane", "Mbour", "Rufisque", "Bargny",
  "Dakar Plateau", "Medina", "Fann", "Mermoz", "Yoff", "Ngor", "Ouakam", "Parcelles Assainies", "Cambérène", "Grand Yoff",
  "Keur Massar", "Biscuiterie", "Dieuppeul", "Derklé", "Hann Bel Air", "Sicap Liberté", "Amitié", "Cité Keur Gorgui", "Almadies", "Ngor Virage",
  "Thiès Ville", "Médina Baye", "Khombole", "Mékhé", "Tivaouane Ville", "Mboro Ville", "Pout", "Sindia", "Bambey", "Diourbel",
  "Kaolack Ville", "Nioro du Rip", "Koungheul", "Koussanar", "Sokone", "Keur Socé", "Ndoffène", "Thiouthioune", "Ndiaffatou", "Kara",
  "Saint-Louis Ville", "Richard Toll", "Podor", "Dagana", "Matam Ville", "Agnam Civol", "Agnam Thiodaye", "Bokidiawé", "Dabia", "Ouro Sogui",
  "Ziguinchor Ville", "Oussouye", "Casamance", "Bignona", "Sédhiou Ville", "Kolda Ville", "Kaffrine Ville", "Kédougou Ville", "Louga Ville", "Tambacounda Ville",
  "Fatick Ville", "Foundiougne", "Passy", "Djifer", "Bipallet", "Sokone Delta", "Niodior", "Foundioune", "Djinon", "Palmarin",
  "Rufisque Est", "Rufisque Ouest", "Bargny Guedj", "Sébikotane", "Bambylor", "Tivaouane Peulh", "Thiès Sud", "Thiès Nord", "Pikine Ouest", "Guédiawaye Nord"
]

const showRegionDropdown = ref(false)
const showZoneDropdown = ref(false)
const zoneSearch = ref("")

const filteredZones = computed(() => {
  if (!zoneSearch.value) return zones
  const search = zoneSearch.value.toLowerCase()
  return zones.filter(zone => zone.toLowerCase().includes(search))
})

const form = reactive({
  nom: "",
  projet: "",
  code: "CMP-2026-DKR-09",
  description: "",
  zones: [],
  zonesPrioritaires: [],
  dateDebut: "",
  dateFin: "",
})

const toggleRegion = (region) => {
  const index = form.zones.indexOf(region)
  if (index > -1) {
    form.zones.splice(index, 1)
  } else {
    form.zones.push(region)
  }
}

const toggleZone = (zone) => {
  const index = form.zonesPrioritaires.indexOf(zone)
  if (index > -1) {
    form.zonesPrioritaires.splice(index, 1)
  } else {
    form.zonesPrioritaires.push(zone)
  }
}

const creerCampagne = () => {
  const nouvelleCampagne = {
    id: Date.now(),
    code: form.code,
    ...form,
  }

  campagnesMock.value.push(nouvelleCampagne)
  alert("Campagne créée avec succès !")
  router.push("/chef-projet/campagnes")
}
</script>
