<template>
  <div class="space-y-6">
    <!-- Header -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
    >
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Organisations (ONG)</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gérer les organisations humanitaires enregistrées sur la plateforme
        </p>
      </div>
      <div class="flex items-center gap-3"></div>
    </div>

    <!-- Alert Message -->
    <AlertMessage
      v-if="error"
      type="error"
      :message="error"
      :dismissible="true"
      @dismiss="error = null"
    />
    <AlertMessage
      v-if="messageSucces"
      type="success"
      :message="messageSucces"
      :dismissible="true"
      @dismiss="messageSucces = ''"
    />

    <!-- Filters & Search -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search
          :size="18"
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher une ONG par nom, acronyme ou email..."
          class="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
        />
      </div>
      <select
        v-model="filtreStatut"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="tous">Tous les statuts</option>
        <option value="ACTIVE">Actives</option>
        <option value="PENDING">En attente</option>
        <option value="SUSPENDED">Suspendues</option>
      </select>
      <select
        v-model="filtreRegion"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="toutes">Toutes les régions</option>
        <option v-for="region in regionsUniques" :key="region" :value="region">
          {{ region }}
        </option>
      </select>
      <select
        v-model="filtreDomaine"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="tous">Tous les domaines</option>
        <option
          v-for="domaine in domainesUniques"
          :key="domaine"
          :value="domaine"
        >
          {{ domaine }}
        </option>
      </select>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
      <KpiCard
        titre="ONG totales"
        :valeur="ongs.length"
        :icone="Building2"
        couleur="bleu-nuit"
      />
      <KpiCard
        titre="ONG actives"
        :valeur="ongsActives.length"
        :icone="Activity"
        couleur="bleu-accent"
      />
      <KpiCard
        titre="En attente"
        :valeur="demandesONG.length"
        :icone="Users"
        couleur="rose-baraka"
      />
      <KpiCard
        titre="Régions"
        :valeur="statistiques.regionsCount"
        :icone="FolderKanban"
        couleur="bleu-nuit"
      />
    </div>

    <!-- Carte du Sénégal -->
    <div
      class="bg-white border border-slate-200/60 rounded-xl p-4 shadow-xs-sm"
    >
      <h2 class="text-lg font-semibold text-slate-900 mb-4">
        Localisation des ONG au Sénégal
      </h2>
      <div class="h-[500px] rounded-lg overflow-hidden border border-slate-200">
        <CarteSenegalONG
          :ongs="ongsFiltrees"
          :filtre-region="filtreRegion"
          :filtre-domaine="filtreDomaine"
        />
      </div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des organisations..." />

    <!-- Table -->
    <div
      v-else
      class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-xs-sm"
    >
      <EmptyState
        v-if="ongsFiltrees.length === 0"
        titre="Aucune organisation trouvée"
        description="Aucune organisation ne correspond à vos critères de recherche."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-100">
            <tr>
              <th
                class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider"
              >
                Organisation
              </th>
              <th
                class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider"
              >
                Contact
              </th>
              <th
                class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider"
              >
                Localisation
              </th>
              <th
                class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider"
              >
                Domaine
              </th>
              <th
                class="text-left px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider"
              >
                Statut
              </th>
              <th
                class="text-right px-4 py-3 text-xs font-semibold text-bleu-nuit uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="ong in ongsFiltrees"
              :key="ong.id"
              class="hover:bg-slate-50/70 transition"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 bg-slate-100 text-bleu-nuit font-bold rounded-lg flex items-center justify-center border border-slate-200"
                  >
                    {{
                      ong.acronym
                        ? ong.acronym.slice(0, 3).toUpperCase()
                        : ong.name
                        ? ong.name.slice(0, 2).toUpperCase()
                        : "ONG"
                    }}
                  </div>
                  <div>
                    <div class="text-sm font-semibold text-slate-900">
                      {{ ong.name }}
                    </div>
                    <div
                      v-if="ong.acronym"
                      class="text-xs text-slate-500 font-medium"
                    >
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
                <span v-if="ong.region" class="text-xs text-slate-400 block">{{
                  ong.region
                }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                <span
                  class="inline-block max-w-[180px] truncate text-xs font-medium bg-slate-100 text-slate-700 px-2 py-1 rounded"
                >
                  {{ ong.intervention_domain || "Humanitaire" }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                  :class="
                    ong.status === 'ACTIVE'
                      ? 'text-bleu-accent bg-bleu-accent/15 border border-bleu-accent/30'
                      : ong.status === 'PENDING'
                      ? 'text-bleu-nuit bg-bleu-nuit/10 border border-slate-200'
                      : 'text-slate-700 bg-slate-100'
                  "
                >
                  {{
                    ong.status === "ACTIVE"
                      ? "Active"
                      : ong.status === "PENDING"
                      ? "En attente"
                      : "Suspendue"
                  }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  type="button"
                  @click="afficherDetail(ong)"
                  class="text-xs font-semibold text-bleu-nuit hover:text-bleu-nuit px-2.5 py-1.5 rounded border border-slate-200 hover:border-bleu-nuit transition"
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
      <div
        class="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-xs-sm"
      >
        <div class="flex items-center justify-between border-b pb-4">
          <div>
            <h2 class="text-xl font-bold text-slate-900">
              {{ ongSelectionnee.name }}
            </h2>
            <p
              v-if="ongSelectionnee.acronym"
              class="text-xs font-semibold text-bleu-nuit"
            >
              {{ ongSelectionnee.acronym }}
            </p>
          </div>
          <button
            @click="ongSelectionnee = null"
            class="text-slate-400 hover:text-slate-600 p-1"
          >
            etc.
          </button>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Email</span
            >
            <span class="text-slate-800 font-medium">{{
              ongSelectionnee.email
            }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Téléphone</span
            >
            <span class="text-slate-800 font-medium">{{
              ongSelectionnee.phone
            }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Pays / Région</span
            >
            <span class="text-slate-800 font-medium"
              >{{ ongSelectionnee.country }} ({{
                ongSelectionnee.region || "-"
              }})</span
            >
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Adresse</span
            >
            <span class="text-slate-800 font-medium">{{
              ongSelectionnee.address || "-"
            }}</span>
          </div>
          <div class="col-span-2">
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Domaine d'intervention</span
            >
            <span class="text-slate-800 font-medium">{{
              ongSelectionnee.intervention_domain || "-"
            }}</span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Statut</span
            >
            <span
              class="font-bold"
              :class="
                ongSelectionnee.status === 'ACTIVE'
                  ? 'text-bleu-accent'
                  : 'text-bleu-nuit'
              "
            >
              {{
                ongSelectionnee.status === "ACTIVE" ? "Active" : "En attente"
              }}
            </span>
          </div>
          <div>
            <span class="text-xs text-slate-400 uppercase font-semibold block"
              >Date d'enregistrement</span
            >
            <span class="text-slate-800 font-medium">
              {{
                ongSelectionnee.created_at
                  ? new Date(ongSelectionnee.created_at).toLocaleDateString(
                      "fr-FR"
                    )
                  : "-"
              }}
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
      <div
        class="bg-white border border-slate-200 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-xs-sm my-8"
      >
        <div class="flex items-center justify-between border-b pb-4">
          <div>
            <h2 class="text-xl font-bold text-slate-900">
              Enregistrer une nouvelle ONG
            </h2>
            <p class="text-xs text-slate-500">
              L'organisation sera enregistrée et son premier gérant recevra une
              invitation d'activation.
            </p>
          </div>
          <button
            @click="modalCreationOuvert = false"
            class="text-slate-400 hover:text-slate-600 p-1"
          >
            etc.
          </button>
        </div>

        <form @submit.prevent="soumettreCreationONG" class="space-y-4">
          <p v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
          <p v-if="erreurValidationONG" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ erreurValidationONG }}</p>
          <h3
            class="text-xs font-bold uppercase text-bleu-nuit tracking-wider border-b pb-1"
          >
            1. Informations de l'ONG
          </h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Nom complet de l'ONG *</label
              >
              <input
                v-model="formONG.name"
                type="text"
                required
                placeholder="Ex: Secours Solidarité Sahel"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Acronyme</label
              >
              <input
                v-model="formONG.acronym"
                type="text"
                placeholder="Ex: 3S"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Email officiel *</label
              >
              <input
                v-model="formONG.email"
                type="email"
                required
                placeholder="contact@ong.org"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Téléphone *</label
              >
              <input
                v-model="formONG.phone"
                type="tel"
                required
                placeholder="+221 77 000 00 00"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Pays *</label
              >
              <input
                v-model="formONG.country"
                type="text"
                required
                placeholder="Sénégal"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Région *</label
              >
              <input
                v-model="formONG.region"
                type="text"
                required
                placeholder="Dakar"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Adresse</label
              >
              <input
                v-model="formONG.address"
                type="text"
                required
                placeholder="Point E, Rue 3, Dakar"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Domaine d'intervention *</label
              >
              <input
                v-model="formONG.intervention_domain"
                type="text"
                required
                placeholder="Ex: Sécurité alimentaire, Eau & Assainissement"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Logo de l'ONG</label
              >
              <input
                type="file"
                accept="image/png,image/jpeg,.png,.jpg,.jpeg"
                @change="selectionnerLogo($event)"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold file:text-slate-700"
              />
              <p class="mt-1 text-xs text-slate-400">
                PNG ou JPG, 5 Mo maximum. Facultatif.
              </p>
              <p v-if="erreurLogo" class="mt-1 text-xs text-red-600">{{ erreurLogo }}</p>
            </div>
            <div v-for="document in documentsRequis" :key="document.key">
              <label class="block text-xs font-semibold text-slate-700 mb-1">
                {{ document.label }} *
              </label>
              <input
                type="file"
                accept="application/pdf,.pdf"
                required
                @change="selectionnerDocument(document.key, $event)"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
              />
              <p class="mt-1 text-xs text-slate-400">PDF uniquement, 5 Mo maximum.</p>
              <p v-if="erreursDocuments[document.key]" class="mt-1 text-xs text-red-600">
                {{ erreursDocuments[document.key] }}
              </p>
            </div>
          </div>

          <h3
            class="text-xs font-bold uppercase text-bleu-nuit tracking-wider border-b pb-1 pt-3"
          >
            2. Premier Gérant (Responsable ONG)
          </h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Prénom du Gérant *</label
              >
              <input
                v-model="formONG.manager_first_name"
                type="text"
                required
                placeholder="Amadou"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Nom du Gérant *</label
              >
              <input
                v-model="formONG.manager_last_name"
                type="text"
                required
                placeholder="Diallo"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Email du Gérant *</label
              >
              <input
                v-model="formONG.manager_email"
                type="email"
                required
                placeholder="gerant@ong.org"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1"
                >Téléphone du Gérant *</label
              >
              <input
                v-model="formONG.manager_phone"
                type="tel"
                required
                placeholder="+221 77 000 00 00"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
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
              class="px-5 py-2 bg-bleu-nuit hover:bg-[#0a2540] text-white text-sm font-semibold rounded-lg transition disabled:opacity-60"
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
import { ref, computed, reactive } from "vue";
import { storeToRefs } from "pinia";
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js";
import { useAutoRefresh } from "@/composables/useAutoRefresh.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";
import {
  Building2,
  Activity,
  Users,
  FolderKanban,
  Search,
  Plus,
} from "lucide-vue-next";
import KpiCard from "@/components/ui/KpiCard.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import CarteSenegalONG from "@/components/ui/CarteSenegalONG.vue";

const store = useSuperAdminStore();
const { ongs, demandesONG, ongsActives, statistiques, loading, error } =
  storeToRefs(store);

const search = ref("");
const filtreStatut = ref("tous");
const filtreRegion = ref("toutes");
const filtreDomaine = ref("tous");
const ongSelectionnee = ref(null);
const modalCreationOuvert = ref(false);
const envoiEnCours = ref(false);
const messageSucces = ref("");
const erreurLogo = ref("");
const erreurValidationONG = ref("");
const { validate: validateONG } = useFormValidation();
const documentsRequis = [
  { key: "document_receipt", label: "Récépissé de l'ONG" },
  { key: "document_ninea", label: "NINEA" },
  { key: "document_statutes", label: "Statuts de l'ONG" },
];
const erreursDocuments = reactive({
  document_receipt: "",
  document_ninea: "",
  document_statutes: "",
});

// Régions uniques pour le filtre
const regionsUniques = computed(() => {
  const regions = new Set(ongs.value.map((o) => o.region).filter(Boolean));
  return Array.from(regions).sort();
});

// Domaines uniques pour le filtre
const domainesUniques = computed(() => {
  const domaines = new Set(
    ongs.value.map((o) => o.intervention_domain).filter(Boolean)
  );
  return Array.from(domaines).sort();
});

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
  document_receipt: null,
  document_ninea: null,
  document_statutes: null,
  manager_first_name: "",
  manager_last_name: "",
  manager_email: "",
  manager_phone: "",
});

useAutoRefresh(() => store.fetchAll());
const ongsFiltrees = computed(() => {
  let result = ongs.value;
  if (search.value) {
    const q = search.value.toLowerCase();
    result = result.filter(
      (o) =>
        (o.name && o.name.toLowerCase().includes(q)) ||
        (o.acronym && o.acronym.toLowerCase().includes(q)) ||
        (o.email && o.email.toLowerCase().includes(q))
    );
  }
  if (filtreStatut.value !== "tous") {
    result = result.filter((o) => o.status === filtreStatut.value);
  }
  // Filtrer par région
  if (filtreRegion.value !== "toutes") {
    result = result.filter(
      (o) =>
        o.region &&
        o.region.toLowerCase().includes(filtreRegion.value.toLowerCase())
    );
  }
  // Filtrer par domaine
  if (filtreDomaine.value !== "tous") {
    result = result.filter(
      (o) =>
        o.intervention_domain &&
        o.intervention_domain
          .toLowerCase()
          .includes(filtreDomaine.value.toLowerCase())
    );
  }
  return result;
});

const afficherDetail = (ong) => {
  ongSelectionnee.value = ong;
};

const ouvrirModalCreation = () => {
  modalCreationOuvert.value = true;
};

const selectionnerDocument = async (field, event) => {
  const file = event.target.files?.[0] || null;
  formONG[field] = null;
  erreursDocuments[field] = "";
  if (!file) {
    erreursDocuments[field] = "Ce document est obligatoire.";
    return;
  }
  const isPdf = file.type === "application/pdf" && /\.pdf$/i.test(file.name);
  if (!isPdf) erreursDocuments[field] = "Le fichier doit être au format PDF.";
  else if (file.size === 0) erreursDocuments[field] = "Le fichier est vide.";
  else if (file.size > 5 * 1024 * 1024) erreursDocuments[field] = "La taille ne doit pas dépasser 5 Mo.";
  else {
    const signature = new Uint8Array(await file.slice(0, 5).arrayBuffer());
    if (String.fromCharCode(...signature) !== "%PDF-") {
      erreursDocuments[field] = "Le contenu du fichier n'est pas un PDF valide.";
    } else {
      formONG[field] = file;
    }
  }
  if (erreursDocuments[field]) event.target.value = "";
};

const selectionnerLogo = async (event) => {
  const file = event.target.files?.[0] || null;
  formONG.logo = null;
  erreurLogo.value = "";
  if (!file) return;
  if (!["image/png", "image/jpeg"].includes(file.type) || !/\.(png|jpe?g)$/i.test(file.name)) {
    erreurLogo.value = "Le logo doit être au format PNG ou JPG.";
  } else if (file.size === 0) {
    erreurLogo.value = "Le fichier est vide.";
  } else if (file.size > 5 * 1024 * 1024) {
    erreurLogo.value = "La taille ne doit pas dépasser 5 Mo.";
  } else {
    const bytes = new Uint8Array(await file.slice(0, 8).arrayBuffer());
    const png = [137, 80, 78, 71, 13, 10, 26, 10].every((byte, i) => bytes[i] === byte);
    const jpeg = bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
    if (!png && !jpeg) erreurLogo.value = "Le contenu du logo ne correspond pas à son format.";
    else formONG.logo = file;
  }
  if (erreurLogo.value) event.target.value = "";
};

const soumettreCreationONG = async () => {
  erreurValidationONG.value = "";
  const valid = validateONG({
    name: [rules.nomLong, formONG.name],
    email: [rules.email, formONG.email],
    phone: [rules.phone, formONG.phone],
    country: [(value) => rules.required(value) || rules.maxLength(100)(value), formONG.country],
    region: [(value) => rules.required(value) || rules.maxLength(100)(value), formONG.region],
    address: [(value) => rules.required(value) || rules.maxLength(255)(value), formONG.address],
    intervention_domain: [(value) => rules.required(value) || rules.maxLength(150)(value), formONG.intervention_domain],
    manager_first_name: [rules.nom, formONG.manager_first_name],
    manager_last_name: [rules.nom, formONG.manager_last_name],
    manager_email: [rules.email, formONG.manager_email],
    manager_phone: [rules.phone, formONG.manager_phone],
    acronym: [rules.maxLength(50), formONG.acronym],
  });
  if (!valid) {
    erreurValidationONG.value = "Vérifiez les noms, les coordonnées et les champs obligatoires avant de créer l’ONG.";
    return;
  }
  if (documentsRequis.some(({ key }) => !formONG[key] || erreursDocuments[key])) {
    erreurValidationONG.value = "Joignez les trois documents PDF obligatoires.";
    documentsRequis.forEach(({ key }) => {
      if (!formONG[key]) erreursDocuments[key] = "Ce document est obligatoire.";
    });
    return;
  }
  envoiEnCours.value = true;
  messageSucces.value = "";
  try {
    const res = await store.createONG(formONG);
    messageSucces.value = `L'ONG ${formONG.name} a été enregistrée avec succès. Un email d'activation a été envoyé au gérant.`;
    erreurValidationONG.value = "";
    modalCreationOuvert.value = false;
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
      document_receipt: null,
      document_ninea: null,
      document_statutes: null,
      manager_first_name: "",
      manager_last_name: "",
      manager_email: "",
      manager_phone: "",
    });
    Object.keys(erreursDocuments).forEach((key) => (erreursDocuments[key] = ""));
  } catch (err) {
    // Error is set in store.error
  } finally {
    envoiEnCours.value = false;
  }
};
</script>

