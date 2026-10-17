<template>
  <div class="sync-page">

    <!-- ═══════════════════════════════════════════════════════
         HEADER
    ═══════════════════════════════════════════════════════ -->
    <div class="sp-header">
      <div>
        <p class="sp-header__eyebrow">Agent terrain</p>
        <h1 class="sp-header__title">Synchronisation</h1>
        <p class="sp-header__subtitle">
          Données locales et état de synchronisation avec le serveur.
        </p>
      </div>

      <div class="sp-header__right">
        <!-- Badge connexion -->
        <div class="sp-connexion-badge" :class="isOnline ? 'badge--online' : 'badge--offline'">
          <span class="sp-connexion-dot" :class="isOnline ? 'dot--online' : 'dot--offline'" />
          {{ isOnline ? "🟢 En ligne" : "🔴 Hors connexion" }}
        </div>
      </div>
    </div>



    <!-- Barre de progression sync en cours -->
    <div v-if="isSyncing" class="sp-sync-progress">
      <div class="sp-sync-progress__bar">
        <div class="sp-sync-progress__fill" />
      </div>
      <span class="sp-sync-progress__label">
        <Loader2 :size="13" class="animate-spin" /> Synchronisation en cours…
      </span>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         STATISTIQUES
    ═══════════════════════════════════════════════════════ -->
    <div class="sp-stats">
      <div class="sp-stat sp-stat--amber">
        <div class="sp-stat__icon">
          <Clock :size="20" />
        </div>
        <div class="sp-stat__body">
          <span class="sp-stat__value">{{ stats.pending }}</span>
          <span class="sp-stat__label">En attente</span>
        </div>
      </div>

      <div class="sp-stat sp-stat--green">
        <div class="sp-stat__icon">
          <CheckCircle :size="20" />
        </div>
        <div class="sp-stat__body">
          <span class="sp-stat__value">{{ stats.synced }}</span>
          <span class="sp-stat__label">Synchronisés</span>
        </div>
      </div>

      <div class="sp-stat sp-stat--red">
        <div class="sp-stat__icon">
          <AlertCircle :size="20" />
        </div>
        <div class="sp-stat__body">
          <span class="sp-stat__value">{{ stats.failed + stats.conflict }}</span>
          <span class="sp-stat__label">Erreurs</span>
        </div>
      </div>

      <div class="sp-stat sp-stat--slate">
        <div class="sp-stat__icon">
          <Database :size="20" />
        </div>
        <div class="sp-stat__body">
          <span class="sp-stat__value">{{ stats.total }}</span>
          <span class="sp-stat__label">Total</span>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         TABLEAU DES DONNÉES LOCALES
    ═══════════════════════════════════════════════════════ -->
    <div class="sp-table-card">
      <div class="sp-table-card__header">
        <div>
          <h2 class="sp-table-card__title">Données locales</h2>
          <p class="sp-table-card__subtitle">
            Formulaires enregistrés sur cet appareil
          </p>
        </div>

        <button
          v-if="(stats.pending > 0 || stats.failed > 0) && isOnline"
          class="sp-sync-btn"
          :disabled="isSyncing"
          @click="lancerSync"
        >
          <Loader2 v-if="isSyncing" :size="14" class="animate-spin" />
          <RefreshCw v-else :size="14" />
          {{ isSyncing ? "En cours…" : (stats.failed > 0 && stats.pending === 0 ? "Réessayer la synchronisation" : "Synchroniser") }}
        </button>
      </div>

      <!-- Table desktop -->
      <div class="sp-table-wrapper">
        <table class="sp-table">
          <thead class="sp-table__head">
            <tr>
              <th>Date</th>
              <th>Bénéficiaire</th>
              <th>Campagne</th>
              <th>Zone</th>
              <th>Statut / Motif</th>
              <th class="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in allItems"
              :key="item.local_id"
              class="sp-table__row"
            >
              <td class="sp-table__date">
                {{ formatDate(item.timestamp) }}
              </td>
              <td class="sp-table__nom">
                <div>{{ item.beneficiary?.prenom }} {{ item.beneficiary?.nom }}</div>
                <div v-if="item.beneficiary?.telephone" class="sp-benef-phone">
                  📞 {{ item.beneficiary.telephone }}
                </div>
              </td>
              <td>{{ item.campagne_nom || "—" }}</td>
              <td>{{ item.zone_nom || "—" }}</td>
              <td>
                <StatusBadge :status="item.sync_status" />
                <div
                  v-if="item.error_message"
                  class="sp-error-reason"
                  :title="item.error_message"
                >
                  ⚠️ {{ item.error_message }}
                </div>
              </td>
              <td class="sp-table__action">
                <button
                  class="sp-delete-btn"
                  title="Supprimer"
                  @click="confirmerSuppression(item)"
                >
                  <Trash2 :size="14" />
                </button>
              </td>
            </tr>

            <tr v-if="allItems.length === 0">
              <td colspan="6" class="sp-table__empty">
                <div class="sp-empty">
                  <div class="sp-empty__icon">
                    <Database :size="32" />
                  </div>
                  <p class="sp-empty__title">Aucune donnée locale</p>
                  <p class="sp-empty__text">
                    Tous les bénéficiaires ont été synchronisés avec le serveur.
                  </p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         MODALE DE CONFIRMATION SUPPRESSION
    ═══════════════════════════════════════════════════════ -->
    <Transition name="modal">
      <div v-if="modalSuppression" class="sp-modal-overlay" @click.self="modalSuppression = null">
        <div class="sp-modal">
          <div class="sp-modal__icon">
            <Trash2 :size="24" />
          </div>
          <h3 class="sp-modal__title">Confirmer la suppression</h3>
          <p class="sp-modal__text">
            Voulez-vous supprimer le bénéficiaire
            <strong>
              {{ modalSuppression.beneficiary?.prenom }}
              {{ modalSuppression.beneficiary?.nom }}
            </strong>
            de la mémoire locale ?
            <br />
            <span class="sp-modal__warning">
              Cette action est irréversible.
            </span>
          </p>
          <div class="sp-modal__actions">
            <button class="sp-modal__cancel" @click="modalSuppression = null">
              Annuler
            </button>
            <button class="sp-modal__confirm" @click="supprimerItem">
              Supprimer
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineComponent, h } from "vue";
import {
  Wifi,
  WifiOff,
  CheckCircle,
  AlertCircle,
  Clock,
  Database,
  RefreshCw,
  Trash2,
  Loader2,
} from "lucide-vue-next";

import { useOnlineStatus } from "@/composables/useOnlineStatus";
import { useSync } from "@/composables/useSync";
import { offlineStorage } from "@/services/offlineStorage";

const { isOnline } = useOnlineStatus();
const { syncAll, isSyncing, updateStats } = useSync();

// ── Badge de statut inline ────────────────────────────────────────────────
const StatusBadge = defineComponent({
  props: { status: String },
  setup(props) {
    const BADGES = {
      PENDING:  { label: "En attente",    cls: "sb--pending" },
      SYNCING:  { label: "Synchronisation", cls: "sb--syncing" },
      SYNCED:   { label: "Synchronisé",   cls: "sb--synced" },
      FAILED:   { label: "Erreur",        cls: "sb--failed" },
      CONFLICT: { label: "Conflit",       cls: "sb--conflict" },
    };
    return () => {
      const b = BADGES[props.status] || BADGES.PENDING;
      return h("span", { class: ["sp-status-badge", b.cls] }, b.label);
    };
  },
});

// ── Données ───────────────────────────────────────────────────────────────
const allItems = ref([]);
const stats = ref({
  pending: 0, syncing: 0, synced: 0,
  failed: 0, conflict: 0, total: 0,
});
const modalSuppression = ref(null);

// ── Chargement ────────────────────────────────────────────────────────────
const charger = async () => {
  allItems.value = await offlineStorage.getAll();
  stats.value = await offlineStorage.getStats();
};

onMounted(charger);

// ── Auto-refresh quand connexion revient ──────────────────────────────────
watch(isOnline, async (online) => {
  if (online && (stats.value.pending > 0 || stats.value.failed > 0)) {
    await lancerSync();
  }
});

// ── Synchronisation manuelle ──────────────────────────────────────────────
const lancerSync = async () => {
  await syncAll(true);
  await charger();
};

// ── Suppression ───────────────────────────────────────────────────────────
const confirmerSuppression = (item) => {
  modalSuppression.value = item;
};

const supprimerItem = async () => {
  if (!modalSuppression.value) return;
  await offlineStorage.delete(modalSuppression.value.local_id);
  modalSuppression.value = null;
  await charger();
  await updateStats();
};

// ── Helpers ───────────────────────────────────────────────────────────────
const formatDate = (d) => {
  if (!d) return "—";
  return new Date(d).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
};
</script>

<style scoped>
.sp-error-reason {
  font-size: 11px;
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 4px 8px;
  margin-top: 6px;
  max-width: 320px;
  word-break: break-word;
  line-height: 1.35;
}

.sp-benef-phone {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

/* ── Layout ──────────────────────────────────────────────────────────────── */
.sync-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.sp-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.sp-header__eyebrow {
  font-size: 11px;
  font-weight: 700;
  color: #744D03;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 4px;
}

.sp-header__title {
  font-size: 24px;
  font-weight: 800;
  color: #021427;
  margin: 0;
}

.sp-header__subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0;
}

.sp-header__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sp-connexion-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  border: 1.5px solid transparent;
}

.badge--online  { background: #f0fdf4; border-color: #86efac; color: #15803d; }
.badge--offline { background: #fef2f2; border-color: #fca5a5; color: #dc2626; }

/* ── Bannière ────────────────────────────────────────────────────────────── */
.sp-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 16px;
  border: 1.5px solid transparent;
  font-size: 13px;
}

.sp-banner strong {
  display: block;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}

.sp-banner__text {
  margin: 0;
  font-size: 12px;
  opacity: 0.85;
}

.sp-banner--online  { background: #f0fdf4; border-color: #86efac; color: #15803d; }
.sp-banner--offline { background: #fff7ed; border-color: #fdba74; color: #9a3412; }

.sp-banner__icon {
  flex-shrink: 0;
  margin-top: 2px;
}

/* ── Progress bar sync ───────────────────────────────────────────────────── */
.sp-sync-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #2563eb;
}

.sp-sync-progress__bar {
  flex: 1;
  height: 4px;
  background: #dbeafe;
  border-radius: 999px;
  overflow: hidden;
}

.sp-sync-progress__fill {
  height: 100%;
  background: #2563eb;
  border-radius: 999px;
  animation: progress-indeterminate 1.5s ease infinite;
  width: 40%;
}

.sp-sync-progress__label {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

@keyframes progress-indeterminate {
  0%   { margin-left: -40%; width: 40%; }
  100% { margin-left: 100%; width: 40%; }
}

/* ── Statistiques ────────────────────────────────────────────────────────── */
.sp-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (min-width: 768px) {
  .sp-stats {
    grid-template-columns: repeat(4, 1fr);
  }
}

.sp-stat {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 16px;
  border: 1.5px solid transparent;
}

.sp-stat--amber  { background: #fffbeb; border-color: #fcd34d; color: #b45309; }
.sp-stat--green  { background: #f0fdf4; border-color: #86efac; color: #15803d; }
.sp-stat--red    { background: #fef2f2; border-color: #fca5a5; color: #dc2626; }
.sp-stat--slate  { background: #f8fafc; border-color: #e2e8f0; color: #475569; }

.sp-stat__icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(255,255,255,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sp-stat__value {
  display: block;
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.sp-stat__label {
  display: block;
  font-size: 11px;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── Table card ──────────────────────────────────────────────────────────── */
.sp-table-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  overflow: hidden;
}

.sp-table-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 20px;
  border-bottom: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

.sp-table-card__title {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.sp-table-card__subtitle {
  font-size: 12px;
  color: #94a3b8;
  margin: 2px 0 0;
}

.sp-sync-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 10px;
  background: #021427;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.sp-sync-btn:hover:not(:disabled) {
  background: #0a2540;
}

.sp-sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Table ───────────────────────────────────────────────────────────────── */
.sp-table-wrapper {
  overflow-x: auto;
}

.sp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.sp-table__head {
  background: #f8fafc;
}

.sp-table__head th {
  padding: 11px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.sp-table__row {
  border-top: 1px solid #f1f5f9;
  transition: background 0.15s;
}

.sp-table__row:hover {
  background: #fafafa;
}

.sp-table__row td {
  padding: 12px 16px;
  color: #334155;
  vertical-align: middle;
}

.sp-table__date {
  font-size: 12px;
  color: #94a3b8 !important;
  white-space: nowrap;
}

.sp-table__nom {
  font-weight: 600;
  color: #1e293b !important;
}

.sp-table__action {
  text-align: right !important;
}

.sp-delete-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid #fee2e2;
  background: #fff;
  color: #dc2626;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.sp-delete-btn:hover {
  background: #fef2f2;
  border-color: #fca5a5;
}

.sp-table__empty {
  padding: 0;
}

/* ── Empty state ─────────────────────────────────────────────────────────── */
.sp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 60px 20px;
  text-align: center;
}

.sp-empty__icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.sp-empty__title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.sp-empty__text {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  max-width: 280px;
}

/* ── Badges de statut ────────────────────────────────────────────────────── */
:deep(.sp-status-badge) {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

:deep(.sb--pending)  { background: #fffbeb; color: #b45309; border: 1px solid #fcd34d; }
:deep(.sb--syncing)  { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
:deep(.sb--synced)   { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
:deep(.sb--failed)   { background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }
:deep(.sb--conflict) { background: #fdf2f8; color: #9d174d; border: 1px solid #f9a8d4; }

/* ── Modale ──────────────────────────────────────────────────────────────── */
.sp-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.sp-modal {
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  max-width: 380px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.sp-modal__icon {
  width: 56px;
  height: 56px;
  background: #fef2f2;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dc2626;
}

.sp-modal__title {
  font-size: 17px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.sp-modal__text {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.sp-modal__warning {
  color: #dc2626;
  font-weight: 600;
}

.sp-modal__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  width: 100%;
}

.sp-modal__cancel {
  padding: 10px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.sp-modal__cancel:hover {
  border-color: #94a3b8;
}

.sp-modal__confirm {
  padding: 10px;
  border: none;
  border-radius: 10px;
  background: #dc2626;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.sp-modal__confirm:hover {
  background: #b91c1c;
}

/* Transitions modale */
.modal-enter-active, .modal-leave-active {
  transition: all 0.25s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
.modal-enter-from .sp-modal, .modal-leave-to .sp-modal {
  transform: scale(0.95) translateY(10px);
}
</style>
