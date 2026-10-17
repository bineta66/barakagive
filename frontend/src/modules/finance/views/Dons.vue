<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Dons</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gestion des financements reçus.
        </p>
      </div>
      <BoutonPrimary @click="openCreateDon">
        <Plus class="w-4 h-4" />
        Ajouter don
      </BoutonPrimary>
    </div>

    <!-- KPI -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Total dons</p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ store.dons.length }}
          </h3>
        </div>
        <HandCoins class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Montant total reçu
          </p>
          <h3 class="text-2xl font-bold text-emerald-600 mt-1">
            {{ formatMontant(totalDons) }}
            <span class="text-sm font-normal text-slate-400">FCFA</span>
          </h3>
        </div>
        <TrendingUp class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Donateurs distincts
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ donateursDistincts }}
          </h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Recherche -->
    <div
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex gap-3"
    >
      <div class="relative flex-1">
        <Search
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          :size="16"
        />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher par donateur, campagne ou référence..."
          class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        />
      </div>
      <select
        v-model="filtreMoyen"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="">Tous les moyens</option>
        <option value="VIREMENT">Virement</option>
        <option value="ESPECE">Espèce</option>
        <option value="CHEQUE">Chèque</option>
        <option value="CARTE">Carte</option>
      </select>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="store.loading" message="Chargement des dons..." />

    <!-- Tableau -->
    <div
      v-else
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-hidden"
    >
      <div
        class="px-6 py-4 flex items-center justify-between border-b border-slate-100"
      >
        <h2 class="text-base font-bold text-slate-900">Liste des dons</h2>
        <span class="text-xs text-slate-400"
          >{{ filtered.length }} dons répertoriés</span
        >
      </div>

      <EmptyState
        v-if="filtered.length === 0"
        titre="Aucun don"
        description="Aucun financement reçu n'a encore été enregistré."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead
            class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase"
          >
            <tr>
              <th class="text-left px-6 py-3">Référence</th>
              <th class="text-left px-6 py-3">Donateur</th>
              <th class="text-left px-6 py-3">Campagne</th>
              <th class="text-left px-6 py-3">Montant</th>
              <th class="text-left px-6 py-3">Moyen</th>
              <th class="text-left px-6 py-3">Date</th>
              <th class="text-center px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr
              v-for="don in filtered"
              :key="don.id"
              class="hover:bg-slate-50/50"
            >
              <td class="px-6 py-4 font-mono text-xs text-slate-700">
                {{ don.reference }}
              </td>
              <td class="px-6 py-4 font-semibold text-slate-900">
                {{ don.donateur_nom || "Donateur anonyme" }}
              </td>
              <td class="px-6 py-4 text-slate-600">{{ don.campagne_nom || "—" }}</td>
              <td class="px-6 py-4 font-bold text-emerald-600">
                +{{ formatMontant(don.montant) }} FCFA
              </td>
              <td class="px-6 py-4">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700"
                >
                  {{ don.moyen_paiement }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-500 text-xs">{{ don.date }}</td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button
                    @click="openEdit(don)"
                    class="p-1.5 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition"
                    title="Modifier"
                  >
                    <Pencil :size="15" />
                  </button>
                  <button
                    @click="confirmerSupprimer(don)"
                    class="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition"
                    title="Supprimer"
                  >
                    <Trash2 :size="15" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <DonFormModal
      v-if="modalOpen"
      :ouvert="modalOpen"
      :don="editingDon"
      :erreur-backend="modalError"
      :saving="savingDon"
      @fermer="
        modalOpen = false;
        editingDon = null;
        modalError = '';
      "
      @save="saveDon"
    />

    <!-- Modale confirmation suppression -->
    <Teleport to="body">
      <div
        v-if="donASupprimer"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40"
        @click.self="donASupprimer = null"
      >
        <div class="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
          <div
            class="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mx-auto mb-4"
          >
            <Trash2 :size="22" class="text-red-600" />
          </div>
          <h3 class="text-center font-bold text-slate-900 mb-2">
            Supprimer le don
          </h3>
          <p class="text-center text-sm text-slate-500 mb-6">
            Voulez-vous vraiment supprimer le don
            <strong>{{ donASupprimer.reference }}</strong> de
            <strong>{{ formatMontant(donASupprimer.montant) }} FCFA</strong> ?
            Cette action est irréversible.
          </p>
          <div class="flex gap-3">
            <button
              @click="donASupprimer = null"
              class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Annuler
            </button>
            <button
              @click="supprimerDon"
              :disabled="suppression"
              class="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-60"
            >
              {{ suppression ? "Suppression..." : "Supprimer" }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  Plus,
  HandCoins,
  TrendingUp,
  Users,
  Search,
  Pencil,
  Trash2,
} from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import DonFormModal from "@/modules/finance/components/dons/DonFormModal.vue";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { parseApiError } from "@/modules/finance/utils/parseApiError.js";

const store = useFinanceStore();
const route = useRoute();
const modalOpen = ref(false);
const editingDon = ref(null);
const modalError = ref("");
const savingDon = ref(false);
const search = ref("");
const filtreMoyen = ref("");
const donASupprimer = ref(null);
const suppression = ref(false);

const openCreateDon = () => {
  editingDon.value = null;
  modalOpen.value = true;
};

const openEdit = (don) => {
  editingDon.value = don;
  modalOpen.value = true;
};

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

const totalDons = computed(() =>
  store.dons.reduce((s, d) => s + parseFloat(d.montant || 0), 0)
);
const donateursDistincts = computed(
  () => new Set(store.dons.map((d) => d.donateur_id || d.donateur).filter(Boolean)).size
);
const filtered = computed(() =>
  store.dons.filter((d) => {
    const q = search.value.toLowerCase();
    const matchSearch =
      !q ||
      d.donateur_nom?.toLowerCase().includes(q) ||
      d.campagne_nom?.toLowerCase().includes(q) ||
      d.reference?.toLowerCase().includes(q);
    const matchMoyen =
      !filtreMoyen.value || d.moyen_paiement === filtreMoyen.value;
    return matchSearch && matchMoyen;
  })
);

const saveDon = async (data) => {
  if (savingDon.value) return;
  modalError.value = "";
  savingDon.value = true;
  try {
    if (data.id) {
      await store.updateDonation(data.id, data);
    } else {
      await store.createDonation(data);
    }
    modalOpen.value = false;
    editingDon.value = null;
  } catch (e) {
    modalError.value = parseApiError(e);
  } finally {
    savingDon.value = false;
  }
};

const confirmerSupprimer = (don) => {
  donASupprimer.value = don;
};

const supprimerDon = async () => {
  if (!donASupprimer.value) return;
  suppression.value = true;
  try {
    await store.deleteDonation(donASupprimer.value.id);
    donASupprimer.value = null;
  } catch (e) {
    alert(parseApiError(e));
  } finally {
    suppression.value = false;
  }
};

onMounted(async () => {
  await store.fetchDonations();
  if (route.query.budget) openCreateDon();
});
</script>
