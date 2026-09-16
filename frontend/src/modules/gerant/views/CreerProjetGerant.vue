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

          <div class="space-y-3">
            <label class="block text-sm font-semibold text-gray-700">
              Critères associés *
            </label>

            <!-- Multi-select contrôlé -->
            <div class="relative" ref="critereDropdownRef">
              <button
                type="button"
                @click="critereOuvert = !critereOuvert"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 text-left focus:ring-2 focus:ring-or/30 outline-none text-sm flex items-center justify-between gap-2"
              >
                <span class="truncate">
                  {{
                    form.criteria.length
                      ? `${form.criteria.length} critère(s) sélectionné(s)`
                      : "Sélectionner des critères"
                  }}
                </span>
                <ChevronDown :size="16" class="text-gray-500 shrink-0" />
              </button>

              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-show="critereOuvert"
                  class="absolute z-20 mt-2 w-full bg-white border border-gray-200 rounded-lg shadow-xs-sm max-h-72 overflow-y-auto"
                  @click.stop
                >
                  <div class="p-3 border-b border-gray-100 sticky top-0 bg-white">
                    <input
                      v-model="critereSearch"
                      type="text"
                      placeholder="Rechercher un critère..."
                      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
                    />
                  </div>
                  <div class="py-1">
                    <label
                      v-for="c in criteresFiltres"
                      :key="c.id"
                      class="flex items-center gap-3 px-3 py-2 hover:bg-slate-50 cursor-pointer"
                      @click.stop
                    >
                      <input
                        type="checkbox"
                        :value="c.id"
                        :checked="critereSelectionne(c)"
                        @change="toggleCritere(c)"
                        class="w-4 h-4 rounded text-bleu-nuit focus:ring-or/30"
                      />
                      <span class="text-sm text-gray-700">{{ c.name }}</span>
                    </label>
                    <p
                      v-if="criteresFiltres.length === 0"
                      class="px-3 py-2 text-sm text-gray-500"
                    >
                      Aucun critère correspondant.
                    </p>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Tags des critères sélectionnés -->
            <div
              v-if="form.criteria.length"
              class="flex flex-wrap gap-2 mt-2"
            >
              <span
                v-for="id in form.criteria"
                :key="id"
                class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full text-xs"
              >
                {{ critereLabel(id) }}
                <button
                  type="button"
                  @click="retirerCritere(id)"
                  class="hover:text-bleu-nuit transition"
                  title="Retirer ce critère"
                >
                  <X :size="12" />
                </button>
              </span>
            </div>

            <!-- Action: Ajouter un critère inexistant -->
            <div class="flex items-center gap-3 pt-1">
              <BoutonTertiary type="button" @click="critereModalOuvert = true">
                <Plus :size="16" />
                Ajouter un critère
              </BoutonTertiary>
              <span class="text-xs text-gray-500">
                Le critère n'existe pas ? Créez-le rapidement.
              </span>
            </div>
          </div>
        </div>

        <!-- Boutons d'action -->
        <div class="pt-6 border-t flex justify-end gap-4">
          <BoutonSecondary to="/gerant/projets">
            Annuler
          </BoutonSecondary>
          <BoutonPrimary
            type="submit"
            :disabled="submitting"
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
import { ref, computed, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import { ArrowLeft, Plus, ChevronDown, X } from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import { useProjectStore } from "@/stores/project.js"
import { useOrganizationStore } from "@/stores/organization.js"
import { useAuthStore } from "@/stores/auth.js"
import { getErrorMessage } from "@/services/api.js"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"
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

const criteres = computed(() => projectStore.criteria)

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
  criteria: [],
})

const critereOuvert = ref(false)
const critereDropdownRef = ref(null)
const critereSearch = ref("")
const critereModalOuvert = ref(false)

const criteresFiltres = computed(() => {
  const q = critereSearch.value.toLowerCase().trim()
  if (!q) return criteres.value
  return criteres.value.filter((c) => c.name.toLowerCase().includes(q))
})

const critereSelectionne = (c) => form.value.criteria.includes(c.id)

const toggleCritere = (c) => {
  const i = form.value.criteria.indexOf(c.id)
  if (i === -1) {
    form.value.criteria.push(c.id)
  } else {
    form.value.criteria.splice(i, 1)
  }
}

const retirerCritere = (id) => {
  const i = form.value.criteria.indexOf(id)
  if (i !== -1) form.value.criteria.splice(i, 1)
}

const critereLabel = (id) => {
  const c = criteres.value.find((c) => c.id === id)
  return c?.name || String(id)
}

const onCritereCree = (created) => {
  if (!form.value.criteria.includes(created.id)) {
    form.value.criteria.push(created.id)
  }
}

const onDocumentClick = (e) => {
  if (
    critereOuvert.value &&
    critereDropdownRef.value &&
    !critereDropdownRef.value.contains(e.target)
  ) {
    critereOuvert.value = false
  }
}

const submit = async () => {
  submitError.value = null

  if (form.value.criteria.length === 0) {
    submitError.value = "Sélectionnez au moins un critère de vulnérabilité."
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
      criteria_ids: form.value.criteria,
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
  document.addEventListener("mousedown", onDocumentClick)
  await Promise.all([
    store.fetchUsers().catch(() => {}),
    orgStore.fetchOrganizations().catch(() => {}),
    projectStore.fetchCriteria().catch(() => {}),
  ])
  if (listeChefsProjet.value.length > 0 && !form.value.chefProjet) {
    form.value.chefProjet = listeChefsProjet.value[0].id
  }
  if (listeResponsablesFinance.value.length > 0 && !form.value.responsableFinance) {
    form.value.responsableFinance = listeResponsablesFinance.value[0].id
  }
})

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onDocumentClick)
})
</script>

