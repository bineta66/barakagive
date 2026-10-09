<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Abonnements</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gérez les abonnements des organisations et leurs renouvellements.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Filtre statut -->
        <select
          v-model="filtreStatut"
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
        >
          <option value="tous">Tous les statuts</option>
          <option value="ACTIVE">Actifs</option>
          <option value="TRIAL">En essai</option>
          <option value="EXPIRED">Expirés</option>
          <option value="CANCELLED">Suspendus</option>
        </select>
        <!-- Filtre plan -->
        <select
          v-model="filtrePlan"
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
        >
          <option value="tous">Tous les plans</option>
          <option value="MENSUEL">Mensuel</option>
          <option value="ANNUEL">Annuel</option>
        </select>
      </div>
    </div>

    <!-- Alert erreur -->
    <AlertMessage
      v-if="error"
      type="error"
      :message="error"
      :dismissible="true"
      @dismiss="error = null"
    />

    <!-- Loading -->
    <LoadingSpinner
      v-if="loadingAbonnements"
      message="Chargement des abonnements..."
    />

    <div v-else class="space-y-6">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
        <KpiCard
          titre="ONG abonnées"
          :valeur="statsAbonnements.total"
          :icone="Building2"
          couleur="sky"
        />
        <KpiCard
          titre="Abonnements actifs"
          :valeur="statsAbonnements.actifs"
          :icone="CheckCircle"
          couleur="emerald"
        />
        <KpiCard
          titre="Abonnements expirés"
          :valeur="statsAbonnements.expires"
          :icone="CalendarX"
          couleur="red"
        />
        <KpiCard
          titre="Revenus (FCFA)"
          :valeur="formatMontant(statsAbonnements.revenu)"
          :icone="PiggyBank"
          couleur="amber"
        />
      </div>

      <!-- Tableau abonnements -->
      <div
        class="bg-white border border-slate-200/60 rounded-xl overflow-hidden"
      >
        <div
          class="px-5 py-4 flex items-center justify-between border-b border-slate-100"
        >
          <h2 class="text-base font-semibold text-slate-900">
            Liste des abonnements
            <span class="ml-2 text-sm font-normal text-slate-400"
              >({{ abonnementsFiltres.length }})</span
            >
          </h2>
          <!-- Recherche -->
          <div class="relative">
            <Search
              :size="15"
              class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              v-model="recherche"
              type="text"
              placeholder="Rechercher une ONG..."
              class="pl-8 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 w-56"
            />
          </div>
        </div>

        <EmptyState
          v-if="abonnementsFiltres.length === 0"
          titre="Aucun abonnement trouvé"
          description="Aucun abonnement ne correspond aux filtres sélectionnés."
        />

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50">
              <tr>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  ONG
                </th>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  Plan
                </th>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  Montant
                </th>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  Date début
                </th>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  Prochain renouvellement
                </th>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  Statut
                </th>
                <th
                  class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider"
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="ab in abonnementsFiltres"
                :key="ab.id"
                class="hover:bg-slate-50/70 transition"
              >
                <!-- ONG -->
                <td class="px-4 py-3">
                  <div class="text-sm font-semibold text-slate-900">
                    {{ ab.ong_nom }}
                  </div>
                  <div class="text-xs text-slate-400">{{ ab.ong_email }}</div>
                </td>

                <!-- Plan -->
                <td class="px-4 py-3">
                  <span
                    class="inline-block px-2 py-1 text-xs font-medium text-bleu-nuit bg-bleu-nuit/10 rounded-full"
                  >
                    {{ ab.plan }}
                  </span>
                </td>

                <!-- Montant -->
                <td class="px-4 py-3 text-sm font-semibold text-slate-800">
                  {{ formatMontant(Number(ab.prix)) }} FCFA
                </td>

                <!-- Date début -->
                <td class="px-4 py-3 text-sm text-slate-500">
                  {{ formatDate(ab.trial_start || ab.date_creation) }}
                </td>

                <!-- Prochain renouvellement -->
                <td class="px-4 py-3 text-sm text-slate-500">
                  <span
                    v-if="ab.next_payment_date"
                    :class="
                      isExpiringSoon(ab.next_payment_date)
                        ? 'text-amber-600 font-medium'
                        : ''
                    "
                  >
                    {{ formatDate(ab.next_payment_date) }}
                  </span>
                  <span v-else-if="ab.trial_end" class="text-slate-400">
                    Essai → {{ formatDate(ab.trial_end) }}
                  </span>
                  <span v-else class="text-slate-300">—</span>
                </td>

                <!-- Statut -->
                <td class="px-4 py-3">
                  <StatusBadge :statut="ab.statut">{{
                    labelStatut(ab.statut)
                  }}</StatusBadge>
                </td>

                <!-- Actions -->
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <!-- Voir -->
                    <button
                      @click="voirDetail(ab)"
                      class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-bleu-nuit bg-bleu-nuit/10 hover:bg-bleu-nuit/20 rounded-lg transition"
                    >
                      <Eye :size="13" /> Voir
                    </button>

                    <!-- Suspendre (actif seulement) -->
                    <button
                      v-if="ab.statut === 'ACTIVE' || ab.statut === 'TRIAL'"
                      @click="confirmerAction('suspendre', ab)"
                      class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-lg transition"
                    >
                      <PauseCircle :size="13" /> Suspendre
                    </button>

                    <!-- Réactiver (expiré / suspendu) -->
                    <button
                      v-if="
                        ab.statut === 'EXPIRED' || ab.statut === 'CANCELLED'
                      "
                      @click="confirmerAction('reactiver', ab)"
                      class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition"
                    >
                      <PlayCircle :size="13" /> Réactiver
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Plans disponibles -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <h2 class="text-base font-semibold text-slate-900 mb-4">
          Plans disponibles
        </h2>
        <div class="grid md:grid-cols-2 gap-4 max-w-xl">
          <div
            class="border border-slate-200/60 rounded-xl p-5 text-center hover:border-bleu-nuit/40 transition"
          >
            <div
              class="w-10 h-10 bg-bleu-nuit/10 rounded-xl flex items-center justify-center mx-auto mb-3"
            >
              <CreditCard :size="20" class="text-bleu-nuit" />
            </div>
            <h3 class="font-bold text-slate-900 mb-1">Plan Mensuel</h3>
            <p class="text-2xl font-extrabold text-bleu-nuit mb-1">
              50 000
              <span class="text-sm font-semibold text-slate-500">FCFA</span>
            </p>
            <p class="text-xs text-slate-400">
              par mois · renouvellement automatique
            </p>
            <div class="mt-3 pt-3 border-t border-slate-100">
              <span
                class="inline-block px-2 py-0.5 text-xs font-medium text-bleu-nuit bg-bleu-nuit/10 rounded-full"
              >
                {{ statsAbonnements.actifs }} ONG actives
              </span>
            </div>
          </div>

          <div
            class="border border-slate-200/60 rounded-xl p-5 text-center hover:border-bleu-nuit/40 transition opacity-60"
          >
            <div
              class="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-3"
            >
              <CreditCard :size="20" class="text-slate-400" />
            </div>
            <h3 class="font-bold text-slate-900 mb-1">Plan Annuel</h3>
            <p class="text-2xl font-extrabold text-slate-400 mb-1">
              100 000
              <span class="text-sm font-semibold text-slate-400">FCFA</span>
            </p>
            <p class="text-xs text-slate-400">par an · bientôt disponible</p>
            <div class="mt-3 pt-3 border-t border-slate-100">
              <span
                class="inline-block px-2 py-0.5 text-xs font-medium text-slate-500 bg-slate-100 rounded-full"
              >
                Bientôt disponible
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ MODALE DÉTAIL ══════════════════════════════════════ -->
    <Teleport to="body">
      <div
        v-if="modaleDetail"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="modaleDetail = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg">
          <!-- Header modale -->
          <div
            class="flex items-center justify-between px-6 py-4 border-b border-slate-100"
          >
            <div>
              <h3 class="font-bold text-slate-900">Détail abonnement</h3>
              <p class="text-xs text-slate-400 mt-0.5">
                {{ abonnementSelectionne?.ong_nom }}
              </p>
            </div>
            <button
              @click="modaleDetail = false"
              class="text-slate-400 hover:text-slate-600 transition"
            >
              <X :size="20" />
            </button>
          </div>

          <!-- Corps modale -->
          <div v-if="detailLoading" class="p-6 flex justify-center">
            <div
              class="w-6 h-6 border-2 border-bleu-nuit border-t-transparent rounded-full animate-spin"
            ></div>
          </div>

          <div v-else-if="detailData" class="p-6 space-y-4">
            <!-- Infos -->
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div class="bg-slate-50 rounded-lg p-3">
                <p class="text-xs text-slate-400 mb-0.5">Plan</p>
                <p class="font-semibold text-slate-800">
                  {{ detailData.plan }}
                </p>
              </div>
              <div class="bg-slate-50 rounded-lg p-3">
                <p class="text-xs text-slate-400 mb-0.5">Statut</p>
                <StatusBadge :statut="detailData.statut">{{
                  labelStatut(detailData.statut)
                }}</StatusBadge>
              </div>
              <div class="bg-slate-50 rounded-lg p-3">
                <p class="text-xs text-slate-400 mb-0.5">Prix mensuel</p>
                <p class="font-semibold text-slate-800">
                  {{ formatMontant(Number(detailData.prix)) }} FCFA
                </p>
              </div>
              <div class="bg-slate-50 rounded-lg p-3">
                <p class="text-xs text-slate-400 mb-0.5">
                  Prochain renouvellement
                </p>
                <p class="font-semibold text-slate-800">
                  {{
                    detailData.next_payment_date
                      ? formatDate(detailData.next_payment_date)
                      : "—"
                  }}
                </p>
              </div>
            </div>

            <!-- Historique paiements -->
            <div>
              <p class="text-xs font-semibold uppercase text-slate-500 mb-2">
                Historique des paiements
              </p>
              <div
                v-if="detailData.transactions?.length === 0"
                class="text-xs text-slate-400 text-center py-3 bg-slate-50 rounded-lg"
              >
                Aucun paiement enregistré
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="tx in detailData.transactions"
                  :key="tx.id"
                  class="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-lg text-sm"
                >
                  <div>
                    <span class="font-medium text-slate-800"
                      >{{ formatMontant(Number(tx.montant)) }} FCFA</span
                    >
                    <span class="text-xs text-slate-400 ml-2">{{
                      tx.transaction_id
                    }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-slate-400">{{
                      tx.paid_at
                        ? formatDate(tx.paid_at)
                        : formatDate(tx.created_at)
                    }}</span>
                    <StatusBadge
                      :statut="tx.statut === 'SUCCESS' ? 'ACTIVE' : tx.statut"
                    >
                      {{ tx.statut === "SUCCESS" ? "Réussi" : tx.statut }}
                    </StatusBadge>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer modale -->
          <div
            class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3"
          >
            <button
              @click="modaleDetail = false"
              class="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition"
            >
              Fermer
            </button>
            <button
              v-if="
                detailData &&
                (detailData.statut === 'ACTIVE' ||
                  detailData.statut === 'TRIAL')
              "
              @click="
                confirmerAction('suspendre', detailData);
                modaleDetail = false;
              "
              class="px-4 py-2 text-sm font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition"
            >
              Suspendre
            </button>
            <button
              v-if="
                detailData &&
                (detailData.statut === 'EXPIRED' ||
                  detailData.statut === 'CANCELLED')
              "
              @click="
                confirmerAction('reactiver', detailData);
                modaleDetail = false;
              "
              class="px-4 py-2 text-sm font-semibold text-white bg-bleu-nuit rounded-lg hover:bg-[#0a2540] transition"
            >
              Réactiver
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══ MODALE CONFIRMATION ════════════════════════════════ -->
    <Teleport to="body">
      <div
        v-if="modaleConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="modaleConfirm = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4"
            :class="
              actionEnCours === 'suspendre' ? 'bg-amber-50' : 'bg-emerald-50'
            "
          >
            <PauseCircle
              v-if="actionEnCours === 'suspendre'"
              :size="24"
              class="text-amber-600"
            />
            <PlayCircle v-else :size="24" class="text-emerald-600" />
          </div>
          <h3 class="text-center font-bold text-slate-900 mb-2">
            {{
              actionEnCours === "suspendre"
                ? "Suspendre l'abonnement"
                : "Réactiver l'abonnement"
            }}
          </h3>
          <p class="text-center text-sm text-slate-500 mb-6">
            <template v-if="actionEnCours === 'suspendre'">
              Voulez-vous suspendre l'abonnement de
              <strong>{{ cibleAction?.ong_nom }}</strong> ? L'ONG n'aura plus
              accès à la plateforme.
            </template>
            <template v-else>
              Voulez-vous réactiver l'abonnement de
              <strong>{{ cibleAction?.ong_nom }}</strong> ?
            </template>
          </p>
          <div class="flex gap-3">
            <button
              @click="modaleConfirm = false"
              class="flex-1 px-4 py-2.5 text-sm font-semibold text-slate-600 border border-slate-200 rounded-xl hover:bg-slate-50 transition"
            >
              Annuler
            </button>
            <button
              @click="executerAction"
              :disabled="actionLoading"
              class="flex-1 px-4 py-2.5 text-sm font-semibold text-white rounded-xl transition disabled:opacity-60"
              :class="
                actionEnCours === 'suspendre'
                  ? 'bg-amber-600 hover:bg-amber-700'
                  : 'bg-emerald-600 hover:bg-emerald-700'
              "
            >
              <span
                v-if="actionLoading"
                class="flex items-center justify-center gap-2"
              >
                <span
                  class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                ></span>
                En cours...
              </span>
              <span v-else>
                {{ actionEnCours === "suspendre" ? "Suspendre" : "Réactiver" }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { storeToRefs } from "pinia";
import {
  Building2,
  CheckCircle,
  CalendarX,
  PiggyBank,
  CreditCard,
  Eye,
  PauseCircle,
  PlayCircle,
  Search,
  X,
} from "lucide-vue-next";
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js";
import { useAutoRefresh } from "@/composables/useAutoRefresh.js";
import KpiCard from "@/components/ui/KpiCard.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";

const store = useSuperAdminStore();
const { abonnements, loadingAbonnements, statsAbonnements, error } =
  storeToRefs(store);
const {
  formatMontant,
  fetchAbonnements,
  suspendreAbonnement,
  reactiverAbonnement,
  fetchAbonnementDetail,
} = store;

// ── Filtres ──────────────────────────────────────────────────
const filtreStatut = ref("tous");
const filtrePlan = ref("tous");
const recherche = ref("");

const abonnementsFiltres = computed(() => {
  let list = abonnements.value;
  if (filtreStatut.value !== "tous")
    list = list.filter((a) => a.statut === filtreStatut.value);
  if (filtrePlan.value !== "tous")
    list = list.filter((a) => a.plan_code === filtrePlan.value);
  if (recherche.value.trim()) {
    const q = recherche.value.toLowerCase();
    list = list.filter(
      (a) =>
        a.ong_nom?.toLowerCase().includes(q) ||
        a.ong_email?.toLowerCase().includes(q)
    );
  }
  return list;
});

// ── Helpers ──────────────────────────────────────────────────
const formatDate = (iso) => {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

const isExpiringSoon = (dateStr) => {
  if (!dateStr) return false;
  const diff = new Date(dateStr) - new Date();
  return diff > 0 && diff < 1000 * 60 * 60 * 24 * 7; // < 7 jours
};

const labelStatut = (s) => {
  const labels = {
    ACTIVE: "Actif",
    TRIAL: "En essai",
    EXPIRED: "Expiré",
    CANCELLED: "Suspendu",
  };
  return labels[s] || s;
};

// ── Modale Détail ────────────────────────────────────────────
const modaleDetail = ref(false);
const detailLoading = ref(false);
const detailData = ref(null);
const abonnementSelectionne = ref(null);

const voirDetail = async (ab) => {
  abonnementSelectionne.value = ab;
  modaleDetail.value = true;
  detailLoading.value = true;
  try {
    detailData.value = await fetchAbonnementDetail(ab.id);
  } finally {
    detailLoading.value = false;
  }
};

// ── Modale Confirmation ──────────────────────────────────────
const modaleConfirm = ref(false);
const actionEnCours = ref("");
const cibleAction = ref(null);
const actionLoading = ref(false);

const confirmerAction = (action, ab) => {
  actionEnCours.value = action;
  cibleAction.value = ab;
  modaleConfirm.value = true;
};

const executerAction = async () => {
  if (!cibleAction.value) return;
  actionLoading.value = true;
  try {
    if (actionEnCours.value === "suspendre") {
      await suspendreAbonnement(cibleAction.value.id);
    } else {
      await reactiverAbonnement(cibleAction.value.id);
    }
    modaleConfirm.value = false;
  } finally {
    actionLoading.value = false;
  }
};

// ── Init ─────────────────────────────────────────────────────
onMounted(() => fetchAbonnements());
useAutoRefresh(() => fetchAbonnements(), 60000);
</script>
