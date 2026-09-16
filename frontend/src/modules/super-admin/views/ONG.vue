<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Organisations (ONG)</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gérer les organisations humanitaires enregistrées sur la plateforme
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="store.fetchAll"
          class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition"
        >
          Actualiser
        </button>
        <button
          @click="ouvrirModalCreation"
          class="px-4 py-2 bg-or hover:bg-[#6b4203] text-white text-sm font-semibold rounded-lg transition flex items-center gap-2 shadow-xs-sm"
        >
          <Plus :size="16" />
          <span>Nouvelle ONG</span>
        </button>
      </div>
    </div>

    <!-- Alert Message -->
    <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />
    <AlertMessage v-if="messageSucces" type="success" :message="messageSucces" :dismissible="true" @dismiss="messageSucces = ''" />

    <!-- Filters & Search -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher une ONG par nom, acronyme ou email..."
          class="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30 bg-white"
        />
      </div>
      <select
        v-model="filtreStatut"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30 bg-white"
      >
        <option value="tous">Tous les statuts</option>
        <option value="ACTIVE">Actives</option>
        <option value="PENDING">En attente</option>
        <option value="SUSPENDED">Suspendues</option>
      </select>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
      <KpiCard
        titre="ONG totales"
        :valeur="ongs.length"
        :icone="Building2"
        couleur="sky"
      />
      <KpiCard
        titre="ONG actives"
        :valeur="ongsActives.length"
        :icone="Activity"
        couleur="emerald"
      />
      <KpiCard
        titre="En attente"
        :valeur="demandesONG.length"
        :icone="Users"
        couleur="amber"
      />
      <KpiCard
        titre="Régions"
        :valeur="statistiques.regionsCount"
        :icone="FolderKanban"
        couleur="purple"
      />
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des organisations..." />

    <!-- Table -->
    <div v-else class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-xs-sm">
      <EmptyState
        v-if="ongsFiltrees.length === 0"
        titre="Aucune organisation trouvée"
        description="Aucune organisation ne correspond à vos critères de recherche."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Contact
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Localisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Domaine
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="ong in ongsFiltrees" :key="ong.id" class="hover:bg-slate-50/70 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 bg-slate-100 text-or font-bold rounded-lg flex items-center justify-center border border-slate-200">
                    {{ ong.acronym ? ong.acronym.slice(0, 3).toUpperCase() : (ong.name ? ong.name.slice(0, 2).toUpperCase() : 'ONG') }}
                  </div>
                  <div>
                    <div class="text-sm font-semibold text-slate-900">
                      {{ ong.name }}
                    </div>
                    <div v-if="ong.acronym" class="text-xs text-slate-500 font-medium">
                      {{ ong.acronym }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-slate-700">{{ ong.email }}</div>
                <div class="text-xs text-slate-500">{{ ong.phone }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                <span>{{ ong.country }}</span>
                <span v-if="ong.region" class="text-xs text-slate-400 block">{{ ong.region }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                <span class="inline-block max-w-[180px] truncate text-xs font-medium bg-slate-100 text-slate-700 px-2 py-1 rounded">
                  {{ ong.intervention_domain || "Humanitaire" }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                  :class="
                    ong.status === 'ACTIVE'
                      ? 'text-emerald-700 bg-emerald-50 border border-emerald-200'
                      : ong.status === 'PENDING'
                      ? 'text-amber-700 bg-amber-50 border border-amber-200'
                      : 'text-slate-700 bg-slate-100'
                  "
                >
                  {{ ong.status === 'ACTIVE' ? 'Active' : ong.status === 'PENDING' ? 'En attente' : 'Suspendue' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  type="button"
                  @click="afficherDetail(ong)"
                  class="text-xs font-semibold text-bleu-nuit hover:text-or px-2.5 py-1.5 rounded border border-slate-200 hover:border-or transition"
                >
                  Détails
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Détail ONG -->
    <div
      v-if="ongSelectionnee"
      class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    >
      <div class="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-xs-sm">
        <div class="flex items-center justify-between border-b pb-4">
          <div>
            <h2 class="text-xl font-bold text-slate-900">{{ ongSelectionnee.name }}</h2>
            <p v-if="ongSelectionnee.acronym" class="text-xs font-semibold text-or">
              {{ ongSelectionnee.acronym }}
            </p>
          </div>
          <button @click="ongSelectionnee = null" class="text-slate-400 hover:text-slate-600 p-1">
            etc.
          </button>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block">Email</span>
            <span class="text-slate-800 font-medium">{{ ongSelectionnee.email }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block">Téléphone</span>
            <span class="text-slate-800 font-medium">{{ ongSelectionnee.phone }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block">Pays / Région</span>
            <span class="text-slate-800 font-medium">{{ ongSelectionnee.country }} ({{ ongSelectionnee.region || '-' }})</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block">Adresse</span>
            <span class="text-slate-800 font-medium">{{ ongSelectionnee.address || '-' }}</span>
          </div>
          <div class="col-span-2">
            <span class="text-xs text-slate-400 uppercase font-semibold block">Domaine d'intervention</span>
            <span class="text-slate-800 font-medium">{{ ongSelectionnee.intervention_domain || '-' }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block">Statut</span>
            <span class="font-bold" :class="ongSelectionnee.status === 'ACTIVE' ? 'text-emerald-600' : 'text-amber-600'">
              {{ ongSelectionnee.status === 'ACTIVE' ? 'Active' : 'En attente' }}
            </span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block">Date d'enregistrement</span>
            <span class="text-slate-800 font-medium">
              {{ ongSelectionnee.created_at ? new Date(ongSelectionnee.created_at).toLocaleDateString('fr-FR') : '-' }}
            </span>
          </div>
        </div>

        <div class="pt-4 border-t flex justify-end">
          <button
            @click="ongSelectionnee = null"
            class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Création ONG -->
    <div
      v-if="modalCreationOuvert"
      class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto"
    >
      <div class="bg-white border border-slate-200 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-xs-sm my-8">
        <div class="flex items-center justify-between border-b pb-4">
          <div>
            <h2 class="text-xl font-bold text-slate-900">Enregistrer une nouvelle ONG</h2>
            <p class="text-xs text-slate-500">
              L'organisation sera enregistrée et son premier gérant recevra une invitation d'activation.
            </p>
          </div>
          <button @click="modalCreationOuvert = false" class="text-slate-400 hover:text-slate-600 p-1">
            etc.
          </button>
        </div>

        <form @submit.prevent="soumettreCreationONG" class="space-y-4">
          <h3 class="text-xs font-bold uppercase text-or tracking-wider border-b pb-1">
            1. Informations de l'ONG
          </h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Nom complet de l'ONG *</label>
              <input
                v-model="formONG.name"
                type="text"
                required
                placeholder="Ex: Secours Solidarité Sahel"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Acronyme</label>
              <input
                v-model="formONG.acronym"
                type="text"
                placeholder="Ex: 3S"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Email officiel *</label>
              <input
                v-model="formONG.email"
                type="email"
                required
                placeholder="contact@ong.org"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Téléphone *</label>
              <input
                v-model="formONG.phone"
                type="tel"
                required
                placeholder="+221 33 800 00 00"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Pays *</label>
              <input
                v-model="formONG.country"
                type="text"
                required
                placeholder="Sénégal"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Région *</label>
              <input
                v-model="formONG.region"
                type="text"
                required
                placeholder="Dakar"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Adresse</label>
              <input
                v-model="formONG.address"
                type="text"
                required
                placeholder="Point E, Rue 3, Dakar"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Domaine d'intervention *</label>
              <input
                v-model="formONG.intervention_domain"
                type="text"
                required
                placeholder="Ex: Sécurité alimentaire, Eau & Assainissement"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Logo de l'ONG</label>
              <input
                type="file"
                accept="image/*"
                @change="formONG.logo = $event.target.files?.[0] || null"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold file:text-slate-700"
              />
              <p class="mt-1 text-xs text-slate-400">PNG, JPG ou WEBP. Facultatif.</p>
            </div>
          </div>

          <h3 class="text-xs font-bold uppercase text-or tracking-wider border-b pb-1 pt-3">
            2. Premier Gérant (Responsable ONG)
          </h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Prénom du Gérant *</label>
              <input
                v-model="formONG.manager_first_name"
                type="text"
                required
                placeholder="Amadou"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Nom du Gérant *</label>
              <input
                v-model="formONG.manager_last_name"
                type="text"
                required
                placeholder="Diallo"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Email du Gérant *</label>
              <input
                v-model="formONG.manager_email"
                type="email"
                required
                placeholder="gerant@ong.org"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Téléphone du Gérant *</label>
              <input
                v-model="formONG.manager_phone"
                type="tel"
                required
                placeholder="+221 77 000 00 00"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
          </div>

          <div class="pt-4 border-t flex justify-end gap-3">
            <button
              type="button"
              @click="modalCreationOuvert = false"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="envoiEnCours"
              class="px-5 py-2 bg-or hover:bg-[#6b4203] text-white text-sm font-semibold rounded-lg transition disabled:opacity-60"
            >
              {{ envoiEnCours ? "Enregistrement..." : "Créer l'ONG" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue"
import { storeToRefs } from "pinia"
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js"
import {
  Building2,
  Activity,
  Users,
  FolderKanban,
  Search,
  Plus,
} from "lucide-vue-next"
import KpiCard from "@/components/ui/KpiCard.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const store = useSuperAdminStore()
const { ongs, demandesONG, ongsActives, statistiques, loading, error } = storeToRefs(store)

const search = ref("")
const filtreStatut = ref("tous")
const ongSelectionnee = ref(null)
const modalCreationOuvert = ref(false)
const envoiEnCours = ref(false)
const messageSucces = ref("")

const formONG = reactive({
  name: "",
  acronym: "",
  email: "",
  phone: "",
  country: "Sénégal",
  region: "",
  address: "",
  intervention_domain: "",
  logo: null,
  manager_first_name: "",
  manager_last_name: "",
  manager_email: "",
  manager_phone: "",
})

onMounted(() => {
  store.fetchAll()
})

const ongsFiltrees = computed(() => {
  let result = ongs.value
  if (search.value) {
    const q = search.value.toLowerCase()
    result = result.filter((o) =>
      (o.name && o.name.toLowerCase().includes(q)) ||
      (o.acronym && o.acronym.toLowerCase().includes(q)) ||
      (o.email && o.email.toLowerCase().includes(q))
    )
  }
  if (filtreStatut.value !== "tous") {
    result = result.filter((o) => o.status === filtreStatut.value)
  }
  return result
})

const afficherDetail = (ong) => {
  ongSelectionnee.value = ong
}

const ouvrirModalCreation = () => {
  modalCreationOuvert.value = true
}

const soumettreCreationONG = async () => {
  envoiEnCours.value = true
  messageSucces.value = ""
  try {
    const res = await store.createONG(formONG)
    messageSucces.value = `L'ONG ${formONG.name} a été enregistrée avec succès. Un email d'activation a été envoyé au gérant.`
    modalCreationOuvert.value = false
    // Réinitialiser le formulaire
    Object.assign(formONG, {
      name: "",
      acronym: "",
      email: "",
      phone: "",
      country: "Sénégal",
      region: "",
      address: "",
      intervention_domain: "",
      logo: null,
      manager_first_name: "",
      manager_last_name: "",
      manager_email: "",
      manager_phone: "",
    })
  } catch (err) {
    // Error is set in store.error
  } finally {
    envoiEnCours.value = false
  }
}
</script>

