<template>
  <div class="beneficiaires-page">

    <!-- ═══════════════════════════════════════════════════════
         HEADER
    ═══════════════════════════════════════════════════════ -->
    <div class="bp-header">
      <div class="bp-header__left">
        <RouterLink to="/agent/campagnes" class="bp-back-btn" aria-label="Retour à mes campagnes">
          <ArrowLeft :size="18" />
        </RouterLink>
        <div>
          <BreadcrumbNav :items="breadcrumbItems" />
          <p class="bp-header__eyebrow">Collecte terrain</p>
          <h1 class="bp-header__title">Bénéficiaires</h1>
          <p class="bp-header__subtitle">
            {{ campaign?.nom || "Campagne" }}
          </p>
        </div>
      </div>

      <div class="bp-header__right">

        <RouterLink
          :to="`/agent/campagnes/${route.params.id}/formulaire`"
          class="bp-enregistrer-btn"
        >
          <UserPlus :size="16" />
          Enregistrer
        </RouterLink>
      </div>
    </div>



    <!-- ═══════════════════════════════════════════════════════
         STATS RAPIDES
    ═══════════════════════════════════════════════════════ -->
    <div class="bp-stats">
      <div class="bp-stat bp-stat--blue">
        <Users :size="16" />
        <div>
          <span class="bp-stat__value">{{ allItems.length }}</span>
          <span class="bp-stat__label">Total</span>
        </div>
      </div>
      <div class="bp-stat bp-stat--green">
        <CheckCircle :size="16" />
        <div>
          <span class="bp-stat__value">{{ syncedCount }}</span>
          <span class="bp-stat__label">Synchronisés</span>
        </div>
      </div>
      <div class="bp-stat bp-stat--amber">
        <Clock :size="16" />
        <div>
          <span class="bp-stat__value">{{ pendingCount }}</span>
          <span class="bp-stat__label">En attente</span>
        </div>
      </div>
      <div class="bp-stat bp-stat--red">
        <AlertCircle :size="16" />
        <div>
          <span class="bp-stat__value">{{ errorCount }}</span>
          <span class="bp-stat__label">Erreurs</span>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         MESSAGES
    ═══════════════════════════════════════════════════════ -->
    <AlertMessage v-if="error" type="error" :message="error" />
    <LoadingSpinner v-if="loading" message="Chargement des bénéficiaires…" />

    <!-- ═══════════════════════════════════════════════════════
         LISTE — MOBILE
    ═══════════════════════════════════════════════════════ -->
    <div v-if="!loading" class="bp-mobile-list md:hidden">
      <article
        v-for="item in allItems"
        :key="item.local_id || item.id"
        class="bp-mobile-card"
      >
        <div class="bp-mobile-card__top">
          <div>
            <h2 class="bp-mobile-card__nom">
              {{ item.beneficiary?.prenom || item.prenom }}
              {{ item.beneficiary?.nom || item.nom }}
            </h2>
            <p class="bp-mobile-card__tel">
              {{ item.beneficiary?.telephone || item.telephone || "—" }}
            </p>
          </div>
          <SyncBadge :status="item.sync_status" />
        </div>

        <div class="bp-mobile-card__meta">
          <span>Sexe : {{ item.beneficiary?.sexe || item.sexe || "—" }}</span>
          <span>Zone : {{ item.zone_nom || item.zone?.nom || "—" }}</span>
          <span>{{ formatDate(item.timestamp || item.created_at) }}</span>
        </div>
      </article>

      <div v-if="allItems.length === 0" class="bp-empty">
        <Inbox :size="36" />
        <p>Aucun bénéficiaire enregistré pour cette campagne.</p>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         LISTE — DESKTOP
    ═══════════════════════════════════════════════════════ -->
    <div v-if="!loading" class="bp-table-wrapper hidden md:block">
      <table class="bp-table">
        <thead class="bp-table__head">
          <tr>
            <th>Nom</th>
            <th>Téléphone</th>
            <th>Sexe</th>
            <th>Zone</th>
            <th>Date</th>
            <th>Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in allItems"
            :key="item.local_id || item.id"
            class="bp-table__row"
          >
            <td class="bp-table__nom">
              {{ item.beneficiary?.prenom || item.prenom }}
              {{ item.beneficiary?.nom || item.nom }}
            </td>
            <td>{{ item.beneficiary?.telephone || item.telephone || "—" }}</td>
            <td>{{ item.beneficiary?.sexe || item.sexe || "—" }}</td>
            <td>{{ item.zone_nom || item.zone?.nom || "—" }}</td>
            <td>{{ formatDate(item.timestamp || item.created_at) }}</td>
            <td>
              <SyncBadge :status="item.sync_status" />
            </td>
          </tr>

          <tr v-if="allItems.length === 0">
            <td colspan="6" class="bp-table__empty">
              Aucun bénéficiaire enregistré pour cette campagne.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="serverPageCount > 1" class="flex items-center justify-between text-sm">
      <span>Page {{ serverPage }} sur {{ serverPageCount }} · {{ beneficiaryStore.pagination.count }} bénéficiaire(s)</span>
      <div class="flex gap-2">
        <button class="rounded border px-3 py-2 disabled:opacity-40" :disabled="serverPage <= 1" @click="serverPage--">Précédent</button>
        <button class="rounded border px-3 py-2 disabled:opacity-40" :disabled="serverPage >= serverPageCount" @click="serverPage++">Suivant</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  ArrowLeft,
  UserPlus,
  Users,
  CheckCircle,
  Clock,
  AlertCircle,
  Inbox,
} from "lucide-vue-next";

import AlertMessage from "@/components/ui/AlertMessage.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import BreadcrumbNav from "@/components/ui/BreadcrumbNav.vue";



import { useCampaignStore } from "@/stores/campaign";
import { useBeneficiaryStore } from "@/stores/beneficiary";
import { offlineStorage } from "@/services/offlineStorage";

const route = useRoute();
const campaignStore = useCampaignStore();
const beneficiaryStore = useBeneficiaryStore();

const loading = ref(false);
const error = ref("");
const localItems = ref([]);
const serverPage = ref(1);
const serverPageCount = computed(() => Math.max(1, Math.ceil(beneficiaryStore.pagination.count / 20)));
watch(serverPage, (page) => {
  beneficiaryStore.fetchBeneficiaries({
    page,
    page_size: 20,
    campaign_id: route.params.id,
  }).catch(() => {});
});

// ── Badge de synchronisation inline ──────────────────────────────────────
const SyncBadge = defineComponent({
  props: { status: String },
  setup(props) {
    const BADGES = {
      PENDING:  { label: "En attente",    cls: "badge--pending" },
      SYNCING:  { label: "Synchronisation", cls: "badge--syncing" },
      SYNCED:   { label: "Synchronisé",   cls: "badge--synced" },
      FAILED:   { label: "Erreur",        cls: "badge--failed" },
      CONFLICT: { label: "Conflit",       cls: "badge--conflict" },
    };
    return () => {
      const b = BADGES[props.status] || BADGES.SYNCED;
      return h("span", { class: ["sync-badge", b.cls] }, b.label);
    };
  },
});

// ── Données ───────────────────────────────────────────────────────────────
const campaign = computed(() =>
  campaignStore.currentCampaign || campaignStore.campaigns.find(
    (c) => String(c.id) === String(route.params.id)
  )
);
const breadcrumbItems = computed(() => [
  { label: "Mes campagnes", to: "/agent/campagnes" },
  { label: campaign.value?.nom ? `Bénéficiaires — ${campaign.value.nom}` : "Bénéficiaires" },
]);

// Fusionner données serveur + IndexedDB
const serverItems = computed(() =>
  beneficiaryStore.beneficiaries
    .filter((b) => String(b.campagne?.id || b.campagne) === String(route.params.id))
    .map((b) => ({ ...b, sync_status: b.sync_status || "SYNCED" }))
);

const allItems = computed(() => {
  // Items locaux enrichis + items serveur (non dupliqués)
  const localIds = new Set(localItems.value.map((i) => i.local_id));
  const serverOnly = serverItems.value.filter(
    (b) => !localIds.has(b.local_id)
  );
  return [...localItems.value, ...serverOnly];
});

// ── Compteurs ──────────────────────────────────────────────────────────────
const pendingCount = computed(() => allItems.value.filter(i => i.sync_status === "PENDING").length);
const syncedCount  = computed(() => allItems.value.filter(i => i.sync_status === "SYNCED").length);
const errorCount   = computed(() => allItems.value.filter(
  i => i.sync_status === "FAILED" || i.sync_status === "CONFLICT"
).length);

// ── Chargement ────────────────────────────────────────────────────────────
const chargerDonnees = async () => {
  loading.value = true;
  try {
    await Promise.all([
      campaignStore.fetchAgentCampaigns(),
      campaignStore.fetchCampaign(route.params.id).catch(() => {}),
      beneficiaryStore.fetchBeneficiaries({
        page: serverPage.value,
        page_size: 20,
        campaign_id: route.params.id,
      }).catch(() => {}),
    ]);
    // Charger les données locales pour cette campagne
    localItems.value = await offlineStorage.getByCampagne(route.params.id);
  } catch {
    error.value = "Impossible de charger les bénéficiaires.";
  } finally {
    loading.value = false;
  }
};

onMounted(chargerDonnees);

// ── Helpers ───────────────────────────────────────────────────────────────
const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }) : "—";
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.beneficiaires-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.bp-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.bp-header__left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.bp-back-btn {
  width: 38px;
  height: 38px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-top: 4px;
}

.bp-back-btn:hover {
  border-color: #00313c;
  color: #00313c;
}

.bp-header__eyebrow {
  font-size: 11px;
  font-weight: 700;
  color: #00313c;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 4px;
}

.bp-header__title {
  font-size: 22px;
  font-weight: 800;
  color: #00313c;
  margin: 0;
}

.bp-header__subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0;
}

.bp-header__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.bp-enregistrer-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #00313c;
  color: #fff;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
}

.bp-enregistrer-btn:hover {
  background: #064652;
  transform: translateY(-1px);
}

/* ── Stats rapides ───────────────────────────────────────────────────────── */
.bp-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (min-width: 640px) {
  .bp-stats {
    grid-template-columns: repeat(4, 1fr);
  }
}

.bp-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: 14px;
  border: 1.5px solid transparent;
}

.bp-stat--blue,
.bp-stat--green,
.bp-stat--amber,
.bp-stat--red {
  background: rgb(255 255 255 / 72%);
  border-color: rgb(0 49 60 / 12%);
  color: #00313c;
  backdrop-filter: blur(18px);
}

.bp-stat--red .bp-stat__value,
.bp-stat--red > svg { color: #d20c4f; }

.bp-stat__value {
  display: block;
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
}

.bp-stat__label {
  display: block;
  font-size: 11px;
  opacity: 0.75;
}

/* ── Mobile cards ────────────────────────────────────────────────────────── */
.bp-mobile-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bp-mobile-card {
  background: rgb(255 255 255 / 72%);
  border: 1px solid rgb(0 49 60 / 12%);
  backdrop-filter: blur(18px);
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bp-mobile-card__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.bp-mobile-card__nom {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.bp-mobile-card__tel {
  font-size: 12px;
  color: #64748b;
  margin: 4px 0 0;
}

.bp-mobile-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 11px;
  color: #94a3b8;
}

/* ── Desktop table ───────────────────────────────────────────────────────── */
.bp-table-wrapper {
  background: rgb(255 255 255 / 72%);
  border: 1px solid rgb(0 49 60 / 12%);
  backdrop-filter: blur(18px);
  border-radius: 18px;
  overflow: hidden;
}

.bp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.bp-table__head {
  background: #f8fafc;
}

.bp-table__head th {
  padding: 12px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.bp-table__row {
  border-top: 1px solid #f1f5f9;
  transition: background 0.15s;
}

.bp-table__row:hover {
  background: #fafafa;
}

.bp-table__row td {
  padding: 13px 16px;
  color: #334155;
  vertical-align: middle;
}

.bp-table__nom {
  font-weight: 600;
  color: #1e293b !important;
}

.bp-table__empty {
  padding: 48px 20px;
  text-align: center;
  color: #94a3b8;
}

/* ── Badge de synchronisation ────────────────────────────────────────────── */
:deep(.sync-badge) {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

:deep(.badge--pending)  { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
:deep(.badge--syncing),
:deep(.badge--synced)   { background: rgb(0 49 60 / 8%); color: #00313c; border: 1px solid rgb(0 49 60 / 18%); }
:deep(.badge--failed),
:deep(.badge--conflict) { background: rgb(210 12 79 / 9%); color: #d20c4f; border: 1px solid rgb(210 12 79 / 24%); }

/* ── Vide ────────────────────────────────────────────────────────────────── */
.bp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 48px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}
</style>
