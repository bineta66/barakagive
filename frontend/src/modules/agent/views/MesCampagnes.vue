<template>
  <div class="mes-campagnes">

    <!-- ═══════════════════════════════════════════════════════
         HEADER
    ═══════════════════════════════════════════════════════ -->
    <div class="mc-header">
      <div class="mc-header__left">
        <p class="mc-header__eyebrow">Agent terrain</p>
        <h1 class="mc-header__title">Mes campagnes</h1>
        <p class="mc-header__subtitle">
          Campagnes assignées par le chef de projet.
        </p>
      </div>

      <div class="mc-header__right">
        <span class="mc-header__count">
          {{ filteredCampaigns.length }} campagne(s)
        </span>
      </div>
    </div>



    <!-- ═══════════════════════════════════════════════════════
         BARRE DE RECHERCHE
    ═══════════════════════════════════════════════════════ -->
    <div class="mc-search">
      <Search :size="16" class="mc-search__icon" />
      <input
        id="mc-search-input"
        v-model="search"
        type="search"
        placeholder="Rechercher une campagne, un projet…"
        class="mc-search__input"
      />
    </div>

    <!-- ═══════════════════════════════════════════════════════
         ÉTAT
    ═══════════════════════════════════════════════════════ -->
    <AlertMessage v-if="error" type="error" :message="error" />

    <LoadingSpinner v-if="loading" message="Chargement des campagnes…" />

    <!-- ═══════════════════════════════════════════════════════
         GRILLE DE CAMPAGNES
    ═══════════════════════════════════════════════════════ -->
    <div v-if="!loading" class="mc-grid">
      <article
        v-for="campagne in filteredCampaigns"
        :key="campagne.id"
        class="mc-card"
      >
        <!-- Card header gradient -->
        <div class="mc-card__header">
          <div class="mc-card__circle" />
          <div class="mc-card__circle mc-card__circle--sm" />

          <p class="mc-card__projet">
            {{ campagne.projet?.name || campagne.projet || "Projet" }}
          </p>

          <h2 class="mc-card__nom">{{ campagne.nom }}</h2>

          <span class="mc-card__statut" :class="statutClass(campagne.statut)">
            {{ statutLabel(campagne.statut) }}
          </span>
          <span class="mc-card__type">{{ campagne.type }}</span>
        </div>

        <!-- Card body -->
        <div class="mc-card__body">
          <!-- Infos -->
          <div class="mc-card__infos">
            <div class="mc-info">
              <MapPin :size="13" class="mc-info__icon" />
              <div>
                <span class="mc-info__label">Zone assignée</span>
                <span class="mc-info__value">
                  {{ campagne.zone || campagne.zones?.[0]?.nom || "—" }}
                </span>
              </div>
            </div>

            <div class="mc-info">
              <Users :size="13" class="mc-info__icon" />
              <div>
                <span class="mc-info__label">Collectes</span>
                <span class="mc-info__value">
                  {{ campagne.collectes || 0 }} / {{ campagne.objectif_total || campagne.objectif || "∞" }}
                </span>
              </div>
            </div>
          </div>

          <!-- Barre de progression -->
          <div v-if="campagne.objectif" class="mc-progress">
            <div class="mc-progress__header">
              <span>Progression</span>
              <span class="mc-progress__pct">{{ progression(campagne) }}%</span>
            </div>
            <div class="mc-progress__track">
              <div
                class="mc-progress__fill"
                :style="`width: ${progression(campagne)}%`"
              />
            </div>
          </div>

          <!-- Footer date -->
          <div class="mc-card__footer">
            <span class="mc-card__date">
              <CalendarDays :size="12" />
              Du {{ formatDate(campagne.date_debut) }} au {{ formatDate(campagne.date_fin) }}
            </span>
            <span class="mc-card__code">
              {{ campagne.code_campagne || "#" + campagne.id }}
            </span>
          </div>

          <!-- Actions -->
          <div class="mc-card__actions">
            <RouterLink
              :to="`/agent/campagnes/${campagne.id}/beneficiaires`"
              class="mc-btn mc-btn--outline"
            >
              <Users :size="14" />
              Bénéficiaires
            </RouterLink>

            <RouterLink
              :to="`/agent/campagnes/${campagne.id}/formulaire`"
              class="mc-btn mc-btn--primary"
            >
              <UserPlus :size="14" />
              Enregistrer
            </RouterLink>
          </div>
        </div>
      </article>
    </div>

    <!-- État vide -->
    <div
      v-if="!loading && filteredCampaigns.length === 0"
      class="mc-empty"
    >
      <div class="mc-empty__icon">
        <Inbox :size="40" />
      </div>
      <h3 class="mc-empty__title">Aucune campagne disponible</h3>
      <p class="mc-empty__text">
        Aucune campagne ne vous est actuellement assignée.
      </p>
    </div>

    <div v-if="campaignStore.pagination.count > 20" class="flex items-center justify-between text-sm text-slate-600">
      <span>{{ campaignStore.pagination.count }} campagne(s) affectée(s)</span>
      <div class="flex gap-2">
        <button class="min-h-11 rounded-xl border px-4 disabled:opacity-40" :disabled="!campaignStore.pagination.previous || loading" @click="changePage(-1)">Précédent</button>
        <button class="min-h-11 rounded-xl border px-4 disabled:opacity-40" :disabled="!campaignStore.pagination.next || loading" @click="changePage(1)">Suivant</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { RouterLink } from "vue-router";
import {
  Search,
  MapPin,
  Users,
  UserPlus,
  CalendarDays,
  Inbox,
} from "lucide-vue-next";

import AlertMessage from "@/components/ui/AlertMessage.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";



import { useCampaignStore } from "@/stores/campaign";
import { useOnlineStatus } from "@/composables/useOnlineStatus";

const { isOnline } = useOnlineStatus();

const campaignStore = useCampaignStore();

const search = ref("");
const loading = ref(false);
const error = ref("");
const page = ref(1);
let searchTimer;

// ── Chargement ────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true;
  try {
    await campaignStore.fetchAgentCampaigns();
  } catch {
    error.value = "Impossible de charger vos campagnes.";
  } finally {
    loading.value = false;
  }
});

watch(search, () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(async () => {
    page.value = 1;
    loading.value = true;
    try { await campaignStore.fetchAgentCampaigns({ search: search.value.trim() }); }
    catch { error.value = "Impossible de rechercher dans vos campagnes."; }
    finally { loading.value = false; }
  }, 250);
});

const changePage = async (direction) => {
  page.value += direction;
  loading.value = true;
  try { await campaignStore.fetchAgentCampaigns({ page: page.value, search: search.value.trim() }); }
  catch { error.value = "Impossible de charger cette page de campagnes."; }
  finally { loading.value = false; }
};

// ── Filtrage ──────────────────────────────────────────────────────────────
const filteredCampaigns = computed(() => {
  return campaignStore.campaigns;
});

// ── Helpers ───────────────────────────────────────────────────────────────
const formatDate = (date) =>
  date ? new Date(date).toLocaleDateString("fr-FR") : "—";

const progression = (c) => {
  const objective = c.objectif_total || c.objectif;
  if (!objective) return 0;
  return Math.min(100, Math.round(((c.collectes || 0) / objective) * 100));
};

const statutLabel = (statut) => {
  const labels = {
    EN_COURS: "En cours",
    TERMINE: "Terminée",
    EN_ATTENTE: "Planifiée",
    SUSPENDU: "Suspendue",
  };
  return labels[statut] || statut || "En cours";
};

const statutClass = (statut) => {
  const classes = {
    EN_COURS: "statut--encours",
    TERMINE: "statut--termine",
    EN_ATTENTE: "statut--planifie",
    SUSPENDU: "statut--suspendu",
  };
  return classes[statut] || "statut--encours";
};
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.mes-campagnes {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0;
}

.mc-connexion-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1.5px solid transparent;
}
.mc-connexion-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.badge--online  { background: #f0fdf4; border-color: #86efac; color: #15803d; }
.badge--offline { background: #fef2f2; border-color: #fca5a5; color: #dc2626; }
.dot--online  { background: #22c55e; }
.dot--offline { background: #ef4444; }

/* ── Header ──────────────────────────────────────────────────────────────── */
.mc-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.mc-header__eyebrow {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #744D03;
  margin: 0 0 4px;
}

.mc-header__title {
  font-size: 26px;
  font-weight: 800;
  color: #021427;
  margin: 0;
  line-height: 1.2;
}

.mc-header__subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0;
}

.mc-header__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.mc-header__count {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 700;
  border-radius: 999px;
  background: rgba(2, 20, 39, 0.08);
  color: #021427;
}

/* ── Search ──────────────────────────────────────────────────────────────── */
.mc-search {
  position: relative;
  max-width: 320px;
}

.mc-search__icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.mc-search__input {
  width: 100%;
  padding: 10px 14px 10px 36px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  outline: none;
  background: #fff;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.mc-search__input:focus {
  border-color: #021427;
  box-shadow: 0 0 0 3px rgba(2, 20, 39, 0.08);
}

/* ── Grille ──────────────────────────────────────────────────────────────── */
.mc-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 768px) {
  .mc-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .mc-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* ── Card ────────────────────────────────────────────────────────────────── */
.mc-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: box-shadow 0.25s, transform 0.2s;
}

.mc-card:hover {
  box-shadow: 0 8px 24px rgba(2, 20, 39, 0.12);
  transform: translateY(-2px);
}

/* Card header gradient */
.mc-card__header {
  background: linear-gradient(135deg, #021427 0%, #0a2540 60%, #133B6A 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.mc-card__circle {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  top: -20px;
  right: -20px;
}

.mc-card__circle--sm {
  width: 48px;
  height: 48px;
  top: 40px;
  right: 30px;
  background: rgba(255,255,255,0.04);
}

.mc-card__projet {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #93c5fd;
  margin: 0 0 6px;
  position: relative;
  z-index: 1;
}

.mc-card__nom {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin: 0 60px 0 0;
  line-height: 1.3;
  position: relative;
  z-index: 1;
}

.mc-card__statut {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 10px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  z-index: 1;
}

.statut--encours  { background: rgba(16,185,129,0.2); color: #6ee7b7; }
.statut--termine  { background: rgba(148,163,184,0.2); color: #cbd5e1; }
.statut--planifie { background: rgba(251,191,36,0.2); color: #fde68a; }
.statut--suspendu { background: rgba(239,68,68,0.2); color: #fca5a5; }

/* Card body */
.mc-card__body {
  padding: 16px 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mc-card__infos {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.mc-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #f8fafc;
  border-radius: 10px;
  padding: 10px;
}

.mc-info__icon {
  color: #744D03;
  margin-top: 2px;
  flex-shrink: 0;
}

.mc-info__label {
  display: block;
  font-size: 10px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 2px;
}

.mc-info__value {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

/* Progress bar */
.mc-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mc-progress__header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
}

.mc-progress__pct {
  font-weight: 700;
  color: #021427;
}

.mc-progress__track {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 999px;
  overflow: hidden;
}

.mc-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, #021427, #133B6A);
  border-radius: 999px;
  transition: width 0.5s ease;
}

/* Footer */
.mc-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #94a3b8;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
}

.mc-card__date {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mc-card__code {
  font-family: monospace;
}

/* Actions */
.mc-card__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.mc-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 40px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.mc-btn--outline {
  border: 1.5px solid #e2e8f0;
  color: #334155;
  background: #fff;
}

.mc-btn--outline:hover {
  border-color: #021427;
  color: #021427;
  background: rgba(2,20,39,0.04);
}

.mc-btn--primary {
  background: #021427;
  color: #fff;
}

.mc-btn--primary:hover {
  background: #0a2540;
}

/* Empty state */
.mc-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  gap: 12px;
}

.mc-empty__icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.mc-empty__title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.mc-empty__text {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  max-width: 280px;
}
</style>
