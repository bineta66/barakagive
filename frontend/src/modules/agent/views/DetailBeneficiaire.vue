<template>
  <div class="space-y-6">
    <!-- Breadcrumb + Header -->
    <div>
      <div class="flex items-center gap-2 mb-1">
        <RouterLink
          :to="`/agent/campagnes/${
            beneficiary?.campagne?.id || ''
          }/beneficiaires`"
          class="text-xs font-semibold text-slate-400 hover:text-bleu-nuit transition flex items-center gap-1"
        >
          <ChevronLeft :size="14" /> Bénéficiaires
        </RouterLink>
        <span class="text-slate-200">›</span>
        <span class="text-xs text-slate-500 font-medium">Détail</span>
      </div>
      <h1 class="text-2xl font-bold text-slate-900">
        {{
          beneficiary
            ? `${beneficiary.prenom} ${beneficiary.nom}`
            : "Chargement..."
        }}
      </h1>
      <p class="text-sm text-slate-500 mt-0.5">Fiche bénéficiaire</p>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="loading" message="Chargement du bénéficiaire..." />

    <!-- Non trouvé -->
    <EmptyState
      v-else-if="!beneficiary"
      titre="Bénéficiaire introuvable"
      description="Ce bénéficiaire n'existe pas ou n'est plus accessible."
    />

    <div v-else class="space-y-6">
      <!-- Carte identité -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6">
        <!-- En-tête de la fiche -->
        <div
          class="flex items-start justify-between gap-4 pb-5 border-b border-slate-100"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-14 h-14 rounded-2xl bg-bleu-nuit/10 flex items-center justify-center flex-shrink-0"
            >
              <span class="text-xl font-extrabold text-bleu-nuit">
                {{ beneficiary.prenom?.[0] || ""
                }}{{ beneficiary.nom?.[0] || "" }}
              </span>
            </div>
            <div>
              <h2 class="text-lg font-bold text-slate-900">
                {{ beneficiary.prenom }} {{ beneficiary.nom }}
              </h2>
              <p class="text-sm text-slate-400 mt-0.5">
                {{ beneficiary.campagne?.nom || "Campagne" }}
              </p>
            </div>
          </div>
          <StatusBadge
            :statut="
              beneficiary.sync_status === 'SYNCED' ? 'ACTIVE' : 'En attente'
            "
          >
            {{
              beneficiary.sync_status === "SYNCED"
                ? "Synchronisé"
                : "En attente"
            }}
          </StatusBadge>
        </div>

        <!-- Grille infos -->
        <div class="mt-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-bold uppercase text-slate-400 mb-1">
              Téléphone
            </p>
            <p class="text-sm font-semibold text-slate-800">
              {{ beneficiary.telephone || "—" }}
            </p>
          </div>

          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-bold uppercase text-slate-400 mb-1">Sexe</p>
            <p class="text-sm font-semibold text-slate-800">
              {{
                beneficiary.sexe === "M"
                  ? "Masculin"
                  : beneficiary.sexe === "F"
                  ? "Féminin"
                  : beneficiary.sexe || "—"
              }}
            </p>
          </div>

          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-bold uppercase text-slate-400 mb-1">
              Date de naissance
            </p>
            <p class="text-sm font-semibold text-slate-800">
              {{ formatDate(beneficiary.date_naissance) }}
            </p>
          </div>

          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-bold uppercase text-slate-400 mb-1">
              Localité / Zone
            </p>
            <p class="text-sm font-semibold text-slate-800">
              {{ beneficiary.zone?.nom || "—" }}
            </p>
          </div>

          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-bold uppercase text-slate-400 mb-1">
              Date d'enregistrement
            </p>
            <p class="text-sm font-semibold text-slate-800">
              {{ formatDate(beneficiary.created_at) }}
            </p>
          </div>

          <div
            v-if="beneficiary.latitude || beneficiary.longitude"
            class="bg-slate-50 rounded-xl p-4"
          >
            <p class="text-xs font-bold uppercase text-slate-400 mb-1">
              Coordonnées GPS
            </p>
            <p class="text-sm font-semibold text-slate-800 font-mono">
              {{ beneficiary.latitude || "—" }},
              {{ beneficiary.longitude || "—" }}
            </p>
          </div>
        </div>
      </div>

      <!-- Score métier de vulnérabilité (si disponible) -->
      <div
        v-if="
          beneficiary.score_vulnerabilite !== undefined &&
          beneficiary.score_vulnerabilite !== null
        "
        class="bg-white border border-slate-200/60 rounded-xl p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-semibold text-slate-900">
            Score de vulnérabilité
          </h3>
          <span
            class="px-3 py-1 rounded-full text-xs font-bold"
            :class="scoreClass(beneficiary.score_vulnerabilite)"
          >
            {{ beneficiary.score_vulnerabilite }}/100
          </span>
        </div>
        <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="scoreBarClass(beneficiary.score_vulnerabilite)"
            :style="`width: ${beneficiary.score_vulnerabilite}%`"
          ></div>
        </div>
        <p class="text-xs text-slate-400 mt-2">
          {{ scoreLabel(beneficiary.score_vulnerabilite) }}
        </p>
      </div>

      <section class="bg-white border border-slate-200/60 rounded-xl p-5 space-y-5">
        <div>
          <h3 class="text-base font-semibold text-slate-900">Actions humanitaires</h3>
          <p class="text-xs text-slate-500 mt-1">Historique des aides enregistrées pour ce bénéficiaire.</p>
        </div>

        <LoadingSpinner v-if="actionsLoading" message="Chargement des actions..." />
        <p v-else-if="!actions.length" class="text-sm text-slate-500">Aucune aide enregistrée pour le moment.</p>
        <ul v-else class="divide-y divide-slate-100">
          <li v-for="action in actions" :key="action.id" class="py-3 flex flex-wrap justify-between gap-2">
            <div>
              <p class="text-sm font-semibold text-slate-800">{{ action.type_aide }} · {{ action.quantite }}</p>
              <p class="text-xs text-slate-500">{{ formatDate(action.date_action) }} · {{ action.agent?.full_name }}</p>
              <p v-if="action.resultat" class="text-sm text-slate-600 mt-1">{{ action.resultat }}</p>
            </div>
            <StatusBadge :statut="action.statut">{{ action.statut === "REALISEE" ? "Réalisée" : "Annulée" }}</StatusBadge>
          </li>
        </ul>

        <form class="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-100 pt-5" @submit.prevent="enregistrerAction">
          <FormField label="Type d'aide" required>
            <select v-model="nouvelleAction.type_aide" required class="border border-slate-300 bg-white">
              <option value="" disabled>Sélectionner une aide</option>
              <option value="ALIMENTAIRE">Aide alimentaire</option>
              <option value="SANTE">Santé</option>
              <option value="VETEMENTS">Vêtements</option>
              <option value="FOURNITURES">Fournitures</option>
              <option value="URGENCE">Aide d'urgence</option>
              <option value="AUTRE">Autre</option>
            </select>
          </FormField>
          <FormField label="Date" required>
            <input v-model="nouvelleAction.date_action" type="date" required class="border border-slate-300" />
          </FormField>
          <FormField label="Quantité" required>
            <input v-model="nouvelleAction.quantite" type="number" min="0.01" step="0.01" required class="border border-slate-300" />
          </FormField>
          <FormField label="Résultat / commentaire">
            <input v-model="nouvelleAction.resultat" type="text" maxlength="2000" class="border border-slate-300" />
          </FormField>
          <p v-if="actionError" class="md:col-span-2 text-sm text-red-600">{{ actionError }}</p>
          <div class="md:col-span-2">
            <BoutonPrimary type="submit" :disabled="actionSaving">
              {{ actionSaving ? "Enregistrement..." : "Enregistrer l'aide" }}
            </BoutonPrimary>
          </div>
        </form>
      </section>

      <!-- Réponses du formulaire -->
      <div
        v-if="beneficiary.responses?.length"
        class="bg-white border border-slate-200/60 rounded-xl overflow-hidden"
      >
        <div class="px-5 py-4 border-b border-slate-100">
          <h3 class="text-base font-semibold text-slate-900">
            Réponses au formulaire
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">
            {{ beneficiary.responses.length }} réponse(s)
          </p>
        </div>
        <div class="divide-y divide-slate-100">
          <div
            v-for="response in beneficiary.responses"
            :key="response.id"
            class="flex items-start justify-between gap-4 px-5 py-3.5 hover:bg-slate-50/70 transition"
          >
            <dt class="text-sm text-slate-500 flex-1">
              {{ response.question?.label }}
            </dt>
            <dd class="text-sm font-semibold text-slate-800 text-right">
              {{
                response.value_text ||
                response.value_number ||
                (response.value_boolean !== null &&
                response.value_boolean !== undefined
                  ? response.value_boolean
                    ? "Oui"
                    : "Non"
                  : null) ||
                response.value_date ||
                "—"
              }}
            </dd>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ChevronLeft } from "lucide-vue-next";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import FormField from "@/components/ui/FormField.vue";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import { useBeneficiaryStore } from "@/stores/beneficiary.js";

const route = useRoute();
const store = useBeneficiaryStore();

const beneficiary = ref(null);
const loading = ref(true);
const actions = ref([]);
const actionsLoading = ref(false);
const actionSaving = ref(false);
const actionError = ref("");
const nouvelleAction = ref({ type_aide: "", date_action: new Date().toISOString().slice(0, 10), quantite: 1, resultat: "" });

const chargerActions = async (id) => {
  actionsLoading.value = true;
  try {
    actions.value = await store.fetchHumanitarianActions(id);
  } catch {
    actionError.value = "Impossible de charger l'historique des aides.";
  } finally {
    actionsLoading.value = false;
  }
};

const enregistrerAction = async () => {
  if (!beneficiary.value) return;
  actionSaving.value = true;
  actionError.value = "";
  try {
    await store.createHumanitarianAction(beneficiary.value.id, nouvelleAction.value);
    await chargerActions(beneficiary.value.id);
    nouvelleAction.value = { type_aide: "", date_action: new Date().toISOString().slice(0, 10), quantite: 1, resultat: "" };
  } catch (error) {
    actionError.value = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || "Impossible d'enregistrer cette aide.";
  } finally {
    actionSaving.value = false;
  }
};

const formatDate = (value) =>
  value
    ? new Date(value).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      })
    : "—";

const scoreClass = (score) => {
  if (score >= 70) return "bg-red-100 text-red-700";
  if (score >= 40) return "bg-amber-100 text-amber-700";
  return "bg-emerald-100 text-emerald-700";
};

const scoreBarClass = (score) => {
  if (score >= 70) return "bg-red-500";
  if (score >= 40) return "bg-amber-500";
  return "bg-emerald-500";
};

const scoreLabel = (score) => {
  if (score >= 70) return "Vulnérabilité élevée — priorité d'intervention";
  if (score >= 40) return "Vulnérabilité modérée — suivi recommandé";
  return "Vulnérabilité faible";
};

onMounted(async () => {
  try {
    beneficiary.value = await store.fetchBeneficiary(route.params.id);
    await chargerActions(route.params.id);
  } finally {
    loading.value = false;
  }
});
</script>
