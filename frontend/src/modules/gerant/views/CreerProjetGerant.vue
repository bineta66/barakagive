<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 p-8 shadow-xs-sm">
      <!-- En-tête -->
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div>
          <h2 class="text-3xl font-bold text-or">Créer un nouveau projet</h2>
          <p class="text-gray-600 text-sm mt-1">
            Configurez les paramètres opérationnels, les critères de vulnérabilité et les responsables de mission.
          </p>
        </div>
        <BoutonSecondary to="/gerant/projets">
          <ArrowLeft :size="16" />
          Retour
        </BoutonSecondary>
      </div>

      <!-- Alert Error -->
      <AlertMessage
        v-if="submitError"
        type="error"
        :message="submitError"
        :dismissible="true"
        @dismiss="submitError = null"
        class="mb-6"
      />

      <form @submit.prevent="submit" class="space-y-8">
        <!-- Section 1: Identification du projet -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">1. Identification du projet</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Nom du projet -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Nom du projet *
              </label>
              <input
                v-model="form.nom"
                type="text"
                placeholder="Ex: Programme d'Urgence et Résilience Communautaire 2026"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                required
              />
              <p class="text-xs text-gray-500 mt-1">
                Intitulé officiel utilisé par les bailleurs et les partenaires.
              </p>
            </div>

            <!-- Description -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Description
              </label>
              <textarea
                v-model="form.description"
                rows="3"
                placeholder="Décrivez succinctement la vision et le cadre opérationnel du projet..."
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm resize-none"
              ></textarea>
            </div>

            <!-- Code projet automatique -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Code projet automatique
              </label>
              <div class="px-4 py-2.5 bg-sky-50 rounded-lg border border-sky-200">
                <span class="text-bleu-nuit font-semibold text-sm">{{ codePreview }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Généré automatiquement par BarakaGive360 à partir de la région de votre organisation.
              </p>
            </div>

            <!-- Chef de projet -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Chef de projet assigné *
              </label>
              <select
                v-model="form.chefProjet"
                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                required
              >
                <option value="">Sélectionner un chef de projet</option>
                <option
                  v-for="c in listeChefsProjet"
                  :key="c.id"
                  :value="c.id"
                >
                  {{ c.first_name || c.last_name ? `${c.first_name} ${c.last_name}` : c.email }} ({{ c.role }})
                </option>
              </select>
            </div>

            <!-- Responsable Finance -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Responsable Finance *
              </label>
              <select
                v-model="form.responsableFinance"
                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                required
              >
                <option value="">Sélectionner un responsable finance</option>
                <option
                  v-for="r in listeResponsablesFinance"
                  :key="r.id"
                  :value="r.id"
                >
                  {{ r.first_name || r.last_name ? `${r.first_name} ${r.last_name}` : r.email }} ({{ r.role }})
                </option>
              </select>
            </div>

            <!-- Objectif humanitaire -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Objectif humanitaire et impact attendu *
              </label>
              <textarea
                v-model="form.objectif"
                rows="3"
                placeholder="Décrivez les cibles de bénéficiaires, les livrables concrets et les résultats escomptés..."
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm resize-none"
                required
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Section 2: Calendrier -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">2. Calendrier d'exécution</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Date de début -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Date de début *
              </label>
              <input
                v-model="form.dateDebut"
                type="date"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                required
              />
            </div>

            <!-- Date de fin -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Date de fin *
              </label>
              <input
                v-model="form.dateFin"
                type="date"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                required
              />
            </div>
          </div>
        </div>

        <!-- Section 3: Critères de vulnérabilité -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">3. Critères de vulnérabilité</h3>

          <div class="space-y-4">
            <label class="block text-sm font-semibold text-gray-700">
              Critères associés *
            </label>

            <!-- Formulaire d'ajout de critère -->
            <div class="grid grid-cols-1 md:grid-cols-12 gap-3">
              <div class="md:col-span-6">
                <input
                  v-model="nouveauCritere.nom"
                  type="text"
                  placeholder="Ex: Revenu très faible"
                  class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                  :disabled="submitting"
                />
              </div>
              <div class="md:col-span-3">
                <input
                  v-model="nouveauCritere.poids"
                  type="number"
                  min="1"
                  max="100"
                  placeholder="Poids (%)"
                  class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                  :disabled="submitting"
                />
              </div>
              <div class="md:col-span-3">
                <BoutonPrimary
                  type="button"
                  :disabled="submitting || !critereValide"
                  @click="ajouterCritere"
                  class="w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Plus :size="16" />
                  Ajouter
                </BoutonPrimary>
              </div>
            </div>

            <!-- Tableau des critères -->
            <div v-if="form.criteres.length" class="border border-gray-200 rounded-lg overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Critère</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Poids</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">Action</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="critere in form.criteres" :key="critere.id">
                    <td class="px-4 py-3 text-sm text-gray-700">{{ critere.nom }}</td>
                    <td class="px-4 py-3 text-sm text-gray-700">{{ critere.poids }}%</td>
                    <td class="px-4 py-3 text-right">
                      <button
                        type="button"
                        @click="supprimerCritere(critere.id)"
                        class="text-red-600 hover:text-red-800 transition"
                        title="Supprimer"
                      >
                        <Trash2 :size="16" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Indicateur de progression -->
            <div v-if="form.criteres.length" class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span class="font-semibold text-gray-700">Total des poids : {{ totalPoids }} / 100</span>
                <span :class="couleurTotalPoids">{{ messageTotalPoids }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5 relative overflow-hidden">
                <div
                  class="h-2.5 rounded-full transition-all duration-300"
                  :style="{
                    width: Math.min(totalPoids, 100) + '%',
                    backgroundColor: totalPoids > 100 ? '#dc2626' : totalPoids === 100 ? '#16a34a' : '#744D03'
                  }"
                ></div>
              </div>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>0</span>
                <span class="font-semibold" :class="totalPoids > 100 ? 'text-red-600' : totalPoids === 100 ? 'text-green-600' : 'text-yellow-600'">{{ totalPoids }}%</span>
                <span>100</span>
              </div>
            </div>

            <p v-if="totalPoids !== 100" class="text-xs text-red-600">
              Les critères de vulnérabilité doivent totaliser exactement 100 points.
            </p>
          </div>
        </div>

        <!-- Boutons d'action -->
        <div class="pt-6 border-t flex justify-end gap-4">
          <BoutonSecondary to="/gerant/projets">
            Annuler
          </BoutonSecondary>
          <BoutonPrimary
            type="submit"
            :disabled="submitting || totalPoids !== 100"
            class="disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus v-if="!submitting" :size="16" />
            <span v-if="submitting">Création en cours...</span>
            <span v-else>Créer et activer le projet</span>
          </BoutonPrimary>
        </div>
      </form>
    </div>

    <CritereVulnerabiliteModal
      :ouvert="critereModalOuvert"
      @fermer="critereModalOuvert = false"
      @cree="onCritereCree"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ArrowLeft, Plus, Trash2 } from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import { useProjectStore } from "@/stores/project.js"
import { useOrganizationStore } from "@/stores/organization.js"
import { useAuthStore } from "@/stores/auth.js"
import { getErrorMessage } from "@/services/api.js"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import CritereVulnerabiliteModal from "@/modules/gerant/components/projets/CritereVulnerabiliteModal.vue"

const router = useRouter()
const store = useGerantStore()
const projectStore = useProjectStore()
const orgStore = useOrganizationStore()
const authStore = useAuthStore()

const submitting = ref(false)
const submitError = ref(null)

const listeChefsProjet = computed(() => {
  const filtered = store.users.filter((u) => u.role === "CHEF_PROJET")
  return filtered.length > 0 ? filtered : store.users
})

const listeResponsablesFinance = computed(() => {
  const filtered = store.users.filter((u) => u.role === "FINANCE")
  return filtered.length > 0 ? filtered : store.users
})

const orgRegion = computed(() => {
  const id = authStore.organizationId
  if (!id) return null
  const org = orgStore.organizations.find((o) => o.id === id)
  return org?.region ?? null
})

const codePreview = computed(() => {
  const year = new Date().getFullYear()
  const prefix = ((orgRegion.value || "REG").slice(0, 3).toUpperCase()) || "REG"
  return `PRJ-${year}-${prefix}-001`
})

const now = new Date()
const today = now.toISOString().split("T")[0]
const dateFinDefaut = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000)
  .toISOString()
  .split("T")[0]

const form = ref({
  nom: "",
  description: "",
  chefProjet: "",
  responsableFinance: "",
  objectif: "",
  dateDebut: today,
  dateFin: dateFinDefaut,
  criteres: [],
})

const critereModalOuvert = ref(false)
const nouveauCritere = ref({ nom: "", poids: "" })

const totalPoids = computed(() => {
  return form.value.criteres.reduce((acc, c) => acc + (parseInt(c.poids, 10) || 0), 0)
})

const couleurTotalPoids = computed(() => {
  if (totalPoids.value > 100) return "text-red-600"
  if (totalPoids.value === 100) return "text-green-600"
  return "text-yellow-600"
})

const messageTotalPoids = computed(() => {
  if (totalPoids.value > 100) return "Dépassement"
  if (totalPoids.value === 100) return "OK"
  return "En cours"
})

const critereValide = computed(() => {
  const nomOk = nouveauCritere.value.nom.trim().length > 0
  const poidsOk = parseInt(nouveauCritere.value.poids, 10) >= 1 && parseInt(nouveauCritere.value.poids, 10) <= 100
  return nomOk && poidsOk
})

const ajouterCritere = async () => {
  if (!critereValide.value) return
  const poidsValue = parseInt(nouveauCritere.value.poids, 10)
  const newTotal = totalPoids.value + poidsValue
  if (newTotal > 100) {
    submitError.value = "La somme des poids ne peut pas dépasser 100."
    return
  }
  const newCritere = {
    id: Date.now(),
    nom: nouveauCritere.value.nom.trim(),
    poids: poidsValue,
  }
  form.value.criteres.push(newCritere)
  nouveauCritere.value = { nom: "", poids: "" }
}

const supprimerCritere = (id) => {
  const i = form.value.criteres.findIndex((c) => c.id === id)
  if (i !== -1) form.value.criteres.splice(i, 1)
}

const onCritereCree = (critere) => {
  if (!form.value.criteres.find((c) => c.nom.toLowerCase() === critere.nom.toLowerCase())) {
    form.value.criteres.push({
      id: Date.now(),
      nom: critere.nom,
      poids: critere.poids,
    })
  }
}

const submit = async () => {
  submitError.value = null

  if (form.value.criteres.length === 0) {
    submitError.value = "Ajoutez au moins un critère de vulnérabilité."
    return
  }

  if (totalPoids.value !== 100) {
    submitError.value = "Les critères de vulnérabilité doivent totaliser exactement 100 points."
    return
  }

  submitting.value = true
  try {
    const payload = {
      name: form.value.nom,
      description: form.value.description,
      region: orgRegion.value || "",
      objectif: form.value.objectif,
      start_date: form.value.dateDebut,
      end_date: form.value.dateFin,
      chef_projet: form.value.chefProjet,
      responsable_finance: form.value.responsableFinance,
      criteres: form.value.criteres.map((c) => ({
        nom: c.nom,
        poids: c.poids,
      })),
    }

    await projectStore.createProject(payload)
    await store.fetchProjets().catch(() => {})
    router.push("/gerant/projets")
  } catch (err) {
    submitError.value = getErrorMessage(err)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchUsers().catch(() => {}),
    orgStore.fetchOrganizations().catch(() => {}),
  ])
  if (listeChefsProjet.value.length > 0 && !form.value.chefProjet) {
    form.value.chefProjet = listeChefsProjet.value[0].id
  }
  if (listeResponsablesFinance.value.length > 0 && !form.value.responsableFinance) {
    form.value.responsableFinance = listeResponsablesFinance.value[0].id
  }
})
</script>
