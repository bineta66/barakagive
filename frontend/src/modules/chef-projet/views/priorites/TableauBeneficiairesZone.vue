<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4">
      <div class="flex items-start gap-4">
        <button
          @click="goBack"
          class="mt-1 p-2 rounded-lg text-slate-400 hover:text-bleu-nuit hover:bg-slate-100 transition-colors"
          title="Retour à la carte des priorités"
        >
          <ArrowLeft :size="24" />
        </button>
        <div>
          <div class="flex items-center gap-3 flex-wrap">
            <h1 class="text-4xl font-bold text-bleu-nuit">
              Bénéficiaires — {{ zoneInfo?.nom || zoneName || "Zone" }}
            </h1>
            <span
              v-if="zoneInfo"
              class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mt-1 border"
              :class="niveauBadgeClass(zoneInfo.score_moyen)"
            >
              {{ zoneInfo.niveau || niveauFromScore(zoneInfo.score_moyen) }}
            </span>
          </div>
          <p class="text-sm text-gray-500 mt-2 flex items-center gap-2 flex-wrap">
            <span class="inline-flex items-center gap-1">
              <MapPin :size="14" class="text-slate-400" />
              {{ zoneInfo?.region || regionName || "Sénégal" }}
              <template v-if="zoneInfo?.departement && zoneInfo.departement !== zoneInfo.nom">
                · {{ zoneInfo.departement }}
              </template>
            </span>
            <span>•</span>
            <span>Campagne : <strong class="text-slate-700">{{ campagneNom }}</strong></span>
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button
          @click="goBack"
          class="flex items-center gap-2 px-4 py-2.5 bg-bleu-nuit text-white text-sm font-semibold rounded-lg hover:bg-[#01111eff] transition shadow-xs"
        >
          <MapPinned :size="16" />
          Carte des priorités
        </button>
      </div>
    </div>

    <!-- KPIs Zone -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <p
          class="text-xs font-semibold uppercase tracking-wider text-slate-400"
        >
          Total Bénéficiaires
        </p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black text-slate-900">
            {{ beneficiaires.length }}
          </p>
          <span class="p-2 rounded-xl bg-bleu-accent/10 text-bleu-accent">
            <Users :size="20" />
          </span>
        </div>
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <p
          class="text-xs font-semibold uppercase tracking-wider text-slate-400"
        >
          Score Moyen Zone
        </p>
        <div class="flex items-baseline justify-between mt-2">
          <p
            class="text-3xl font-black"
            :class="scoreColorClass(zoneInfo?.score_moyen || 0)"
          >
            {{ zoneInfo?.score_moyen ?? 0
            }}<span class="text-sm font-bold text-slate-400"> /100</span>
          </p>
          <span class="p-2 rounded-xl bg-bleu-nuit/10 text-bleu-nuit">
            <Activity :size="20" />
          </span>
        </div>
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <p
          class="text-xs font-semibold uppercase tracking-wider text-slate-400"
        >
          Bénéficiaires Prioritaires
        </p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black text-rose-baraka">
            {{ countPrioritaires }}
          </p>
          <span class="p-2 rounded-xl bg-rose-baraka/10 text-rose-baraka">
            <AlertTriangle :size="20" />
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-1">Score vulnérabilité ≥ 60</p>
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <p
          class="text-xs font-semibold uppercase tracking-wider text-slate-400"
        >
          Critères Projet Évalués
        </p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black text-bleu-nuit">
            {{ criteresProjet.length }}
          </p>
          <span class="p-2 rounded-xl bg-bleu-accent/10 text-bleu-accent">
            <CheckSquare :size="20" />
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-1">Critères d'éligibilité actifs</p>
      </div>
    </div>

    <!-- Barre de recherche & Filtres -->
    <div
      class="bg-white border border-slate-200/60 rounded-xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between"
    >
      <div class="relative w-full md:w-96">
        <Search
          :size="18"
          class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher par nom, téléphone, quartier..."
          class="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 focus:border-bleu-nuit transition-all"
        />
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto flex-wrap">
        <!-- Filtre par niveau -->
        <select
          v-model="filterNiveau"
          class="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        >
          <option value="">Tous les niveaux</option>
          <option value="Très élevée">Très élevée (≥ 80)</option>
          <option value="Élevée">Élevée (60–79)</option>
          <option value="Moyenne">Moyenne (40–59)</option>
          <option value="Faible">Faible (< 40)</option>
        </select>

        <!-- Tri -->
        <select
          v-model="sortBy"
          class="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        >
          <option value="score_desc">Score : Plus vulnérable d'abord</option>
          <option value="score_asc">Score : Moins vulnérable d'abord</option>
          <option value="nom_asc">Nom : A à Z</option>
          <option value="nom_desc">Nom : Z à A</option>
          <option value="age_desc">Âge : Plus âgé d'abord</option>
        </select>
      </div>
    </div>

    <!-- État de chargement -->
    <div
      v-if="loading"
      class="bg-white border border-slate-200/60 rounded-xl p-12 text-center"
    >
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-bleu-nuit mx-auto mb-3"
      ></div>
      <p class="text-sm font-medium text-slate-600">
        Chargement des données des bénéficiaires...
      </p>
    </div>

    <!-- Erreur -->
    <div
      v-else-if="error"
      class="bg-rose-baraka/10 border border-rose-baraka/20 rounded-2xl p-6 text-center"
    >
      <p class="text-sm text-rose-baraka font-semibold">{{ error }}</p>
      <button
        @click="fetchData"
        class="mt-3 px-4 py-2 bg-rose-baraka text-white text-xs font-semibold rounded-lg hover:bg-rose-baraka/90 transition-colors"
      >
        Réessayer
      </button>
    </div>

    <!-- Aucun bénéficiaire trouvé -->
    <div
      v-else-if="filteredBeneficiaires.length === 0"
      class="bg-white border border-slate-200/60 rounded-xl p-12 text-center"
    >
      <Users :size="40" class="mx-auto text-slate-300 mb-3" />
      <p class="text-base font-semibold text-slate-700">
        Aucun bénéficiaire ne correspond aux critères
      </p>
      <p class="text-sm text-slate-400 mt-1">
        Modifiez vos filtres ou effectuez une nouvelle recherche.
      </p>
    </div>

    <!-- Cartes des bénéficiaires -->
    <div v-else class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <article
          v-for="(b, index) in paginatedBeneficiaires"
          :key="b.id"
          class="bg-white border border-slate-200/60 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
          @click="openDetail(b)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0" :class="scoreAvatarClass(b.score)">
                {{ initials(b) }}
              </div>
              <div class="min-w-0">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Bénéficiaire {{ (currentPage - 1) * itemsPerPage + index + 1 }}</p>
                <h3 class="font-bold text-lg text-bleu-nuit truncate">{{ b.nom_complet }}</h3>
                <p class="text-sm text-slate-500 flex items-center gap-1.5 mt-0.5"><Phone :size="13" />{{ b.telephone || "Téléphone non renseigné" }}</p>
              </div>
            </div>
            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide flex-shrink-0" :class="niveauBadgeClass(b.score)">
              {{ b.niveau || niveauFromScore(b.score) }}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-3 mt-5">
            <div class="rounded-xl bg-slate-50 p-3">
              <p class="text-[11px] uppercase font-semibold tracking-wide text-slate-400">Score de vulnérabilité</p>
              <p class="mt-1 text-xl font-black" :class="scoreColorClass(b.score)">{{ b.score }}<span class="text-xs text-slate-400 font-semibold"> /100</span></p>
              <div class="h-1.5 mt-2 bg-slate-200 rounded-full overflow-hidden"><div class="h-full rounded-full" :class="scoreBarClass(b.score)" :style="{ width: `${Math.min(Number(b.score) || 0, 100)}%` }" /></div>
            </div>
            <div class="rounded-xl bg-slate-50 p-3">
              <p class="text-[11px] uppercase font-semibold tracking-wide text-slate-400">Informations</p>
              <p class="mt-1 text-sm font-semibold text-slate-700">{{ b.sexe === 'F' ? 'Femme' : b.sexe === 'M' ? 'Homme' : '—' }}<span class="font-normal text-slate-500"> · {{ b.age ? `${b.age} ans` : 'Âge —' }}</span></p>
              <p class="text-xs text-slate-500 truncate mt-1">{{ b.quartier || 'Quartier non renseigné' }}</p>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
            <span class="text-xs text-slate-500">{{ b.criteres?.filter(c => c.obtenu).length || 0 }} critère(s) validé(s) sur {{ b.criteres?.length || 0 }}</span>
            <button @click.stop="openDetail(b)" class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-bleu-nuit hover:bg-[#0a2540] text-white font-semibold text-xs transition"><Eye :size="14" />Voir la fiche</button>
          </div>
        </article>
      </div>

      <div class="bg-white border border-slate-200/70 rounded-xl px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p class="text-xs text-slate-500">Affichage de {{ (currentPage - 1) * itemsPerPage + 1 }} à {{ Math.min(currentPage * itemsPerPage, filteredBeneficiaires.length) }} sur {{ filteredBeneficiaires.length }} bénéficiaire(s) · Tri : {{ sortLabel }}</p>
        <div class="flex items-center gap-2">
          <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm font-semibold text-bleu-nuit hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed">Précédent</button>
          <span class="min-w-20 text-center text-sm font-semibold text-slate-700">{{ currentPage }} / {{ pageCount }}</span>
          <button @click="currentPage++" :disabled="currentPage >= pageCount" class="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm font-semibold text-bleu-nuit hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed">Suivant</button>
        </div>
      </div>
    </div>

    <!-- MODAL : FICHE DÉTAILLÉE DU BÉNÉFICIAIRE -->
    <Transition name="fade">
      <div
        v-if="selectedBeneficiaire"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
        @click.self="closeDetail"
      >
        <div
          class="bg-white rounded-3xl border border-slate-200 shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-scale-up"
        >
          <!-- Modal Header -->
          <div
            class="p-6 border-b border-slate-100 flex items-start justify-between bg-white"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-14 h-14 rounded-2xl flex items-center justify-center font-black text-xl shadow-xs"
                :class="scoreAvatarClass(selectedBeneficiaire.score)"
              >
                {{ initials(selectedBeneficiaire) }}
              </div>
              <div>
                <h3 class="text-xl font-bold text-slate-900">
                  {{ selectedBeneficiaire.nom_complet }}
                </h3>
                <p class="text-xs text-slate-500 mt-1 flex items-center gap-2">
                  <span>{{
                    selectedBeneficiaire.sexe === "F" ? "Femme" : "Homme"
                  }}</span>
                  <span>•</span>
                  <span>{{
                    selectedBeneficiaire.age
                      ? selectedBeneficiaire.age + " ans"
                      : "Âge non renseigné"
                  }}</span>
                  <span>•</span>
                  <span>{{
                    selectedBeneficiaire.quartier || zoneInfo?.nom
                  }}</span>
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <div class="flex flex-col items-end">
                <span
                  class="text-2xl font-black"
                  :class="scoreColorClass(selectedBeneficiaire.score)"
                >
                  {{ selectedBeneficiaire.score
                  }}<span class="text-xs text-slate-400 font-semibold">
                    /100</span
                  >
                </span>
                <span
                  class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider mt-0.5"
                  :class="niveauBadgeClass(selectedBeneficiaire.score)"
                >
                  {{ selectedBeneficiaire.niveau }}
                </span>
              </div>
              <button
                @click="closeDetail"
                class="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors ml-2"
              >
                <X :size="20" />
              </button>
            </div>
          </div>

          <!-- Modal Body -->
          <div class="p-6 overflow-y-auto space-y-6 flex-1">
            <!-- Informations Personnelles -->
            <div>
              <h4
                class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3"
              >
                Informations Personnelles
              </h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">
                    Téléphone
                  </p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{ selectedBeneficiaire.telephone || "—" }}
                  </p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">
                    Date de Naissance
                  </p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{ selectedBeneficiaire.date_naissance || "—" }}
                  </p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">
                    Quartier / Dép.
                  </p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{ selectedBeneficiaire.quartier || "—" }}
                  </p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Zone</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{ selectedBeneficiaire.zone_nom || zoneInfo?.nom }}
                  </p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Région</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{ selectedBeneficiaire.region || zoneInfo?.region }}
                  </p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">
                    Date d'inscription
                  </p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{
                      selectedBeneficiaire.created_at
                        ? formatDate(selectedBeneficiaire.created_at)
                        : "—"
                    }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Détail des Critères de Vulnérabilité -->
            <div>
              <h4
                class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between"
              >
                <span>Évaluation des critères du projet</span>
                <span class="text-slate-600 font-bold">
                  {{
                    (selectedBeneficiaire.criteres || []).filter(
                      (c) => c.obtenu
                    ).length
                  }}
                  validé(s) sur
                  {{ (selectedBeneficiaire.criteres || []).length }}
                </span>
              </h4>
              <div
                class="border border-slate-200 rounded-2xl overflow-hidden divide-y divide-slate-100"
              >
                <div
                  v-for="(critere, idx) in selectedBeneficiaire.criteres || []"
                  :key="idx"
                  class="p-3.5 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  :class="critere.obtenu ? 'bg-bleu-nuit/[0.04]' : ''"
                >
                  <div class="flex items-center gap-3">
                    <span
                      class="w-6 h-6 rounded-full flex items-center justify-center"
                      :class="
                        critere.obtenu
                          ? 'bg-bleu-nuit/10 text-bleu-nuit'
                          : 'bg-slate-100 text-slate-400'
                      "
                    >
                      <CheckCircle2 v-if="critere.obtenu" :size="15" />
                      <XCircle v-else :size="15" />
                    </span>
                    <div>
                      <p class="text-sm font-semibold text-slate-800">
                        {{ critere.nom }}
                      </p>
                      <p class="text-xs text-slate-500">
                        Réponse :
                        <strong class="text-slate-700">{{
                          critere.reponse || "—"
                        }}</strong>
                      </p>
                    </div>
                  </div>

                  <div class="text-right">
                    <span
                      class="text-sm font-bold px-2.5 py-1 rounded-lg"
                      :class="
                        critere.obtenu
                          ? 'bg-bleu-nuit/10 text-bleu-nuit'
                          : 'bg-slate-100 text-slate-500'
                      "
                    >
                      {{ critere.points }} / {{ critere.poids_max }} pts
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Réponses Complètes aux Questions (le cas échéant) -->
            <div
              v-if="
                selectedBeneficiaire.responses &&
                selectedBeneficiaire.responses.length
              "
            >
              <h4
                class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3"
              >
                Réponses détaillées au formulaire
              </h4>
              <div
                class="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-2"
              >
                <div
                  v-for="(resp, rIdx) in selectedBeneficiaire.responses"
                  :key="rIdx"
                  class="flex items-start justify-between py-1.5 border-b border-slate-200/50 last:border-0 text-xs"
                >
                  <span class="text-slate-600 font-medium"
                    >{{ resp.question }} :</span
                  >
                  <span class="text-slate-900 font-bold ml-3 text-right">
                    {{
                      resp.valeur === true
                        ? "Oui"
                        : resp.valeur === false
                        ? "Non"
                        : resp.valeur || "—"
                    }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Modal Footer -->
          <div
            class="p-4 bg-slate-50 border-t border-slate-100 flex justify-end"
          >
            <button
              @click="closeDetail"
              class="px-5 py-2.5 bg-bleu-nuit hover:bg-[#0a2540] text-white font-semibold text-sm rounded-lg transition"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api.js";
import dayjs from "dayjs";
import {
  ArrowLeft,
  MapPinned,
  MapPin,
  Users,
  Activity,
  AlertTriangle,
  CheckSquare,
  Search,
  Phone,
  Eye,
  X,
  CheckCircle2,
  XCircle,
} from "lucide-vue-next";
import { useAutoRefresh } from "@/composables/useAutoRefresh.js";

const route = useRoute();
const router = useRouter();

const zoneId = computed(
  () => route.params.zoneId || route.query.zoneId || route.query.zone || ""
);
const zoneName = computed(() => route.query.nom || "");
const regionName = computed(() => route.query.region || "");

const loading = ref(false);
const error = ref(null);
const zoneInfo = ref(null);
const beneficiaires = ref([]);
const criteresProjet = ref([]);
const campagneNom = ref("Campagne active");

const searchQuery = ref("");
const filterNiveau = ref("");
const sortBy = ref("score_desc");
const itemsPerPage = 4;
const currentPage = ref(1);
const selectedBeneficiaire = ref(null);

const countPrioritaires = computed(() => {
  return beneficiaires.value.filter((b) => (b.score || 0) >= 60).length;
});

const sortLabel = computed(() => {
  switch (sortBy.value) {
    case "score_desc":
      return "Score décroissant";
    case "score_asc":
      return "Score croissant";
    case "nom_asc":
      return "Nom A-Z";
    case "nom_desc":
      return "Nom Z-A";
    case "age_desc":
      return "Âge décroissant";
    default:
      return "Score";
  }
});

const filteredBeneficiaires = computed(() => {
  let list = [...beneficiaires.value];

  // Recherche textuelle
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim();
    list = list.filter((b) => {
      const nom = (b.nom_complet || `${b.prenom} ${b.nom}`).toLowerCase();
      const tel = (b.telephone || "").toLowerCase();
      const quartier = (b.quartier || "").toLowerCase();
      return nom.includes(q) || tel.includes(q) || quartier.includes(q);
    });
  }

  // Filtre par niveau
  if (filterNiveau.value) {
    list = list.filter(
      (b) => (b.niveau || niveauFromScore(b.score)) === filterNiveau.value
    );
  }

  // Tri
  list.sort((a, b) => {
    if (sortBy.value === "score_desc") return (b.score || 0) - (a.score || 0);
    if (sortBy.value === "score_asc") return (a.score || 0) - (b.score || 0);
    if (sortBy.value === "nom_asc")
      return (a.nom || "").localeCompare(b.nom || "");
    if (sortBy.value === "nom_desc")
      return (b.nom || "").localeCompare(a.nom || "");
    if (sortBy.value === "age_desc") return (b.age || 0) - (a.age || 0);
    return 0;
  });

  return list;
});

const pageCount = computed(() =>
  Math.max(1, Math.ceil(filteredBeneficiaires.value.length / itemsPerPage))
);
const paginatedBeneficiaires = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredBeneficiaires.value.slice(start, start + itemsPerPage);
});

watch([searchQuery, filterNiveau, sortBy], () => {
  currentPage.value = 1;
});
watch(pageCount, (count) => {
  if (currentPage.value > count) currentPage.value = count;
});

const fetchData = async () => {
  if (!zoneId.value) {
    error.value = "Identifiant de la zone manquant.";
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    const response = await api.get(`/api/beneficiaries/zone/${zoneId.value}/`, {
      params: route.query.project_id ? { project_id: route.query.project_id } : {},
    });
    zoneInfo.value = response.data.zone || null;
    beneficiaires.value = response.data.beneficiaires || [];
    criteresProjet.value = response.data.criteres_projet || [];
    if (beneficiaires.value.length > 0 && beneficiaires.value[0].campagne) {
      campagneNom.value = beneficiaires.value[0].campagne.nom;
    }
  } catch (err) {
    console.error("Erreur chargement bénéficiaires zone:", err);
    error.value =
      err.response?.data?.detail ||
      "Impossible de charger la liste des bénéficiaires de cette zone.";
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push({ name: "dashboard" });
};

const openDetail = (b) => {
  selectedBeneficiaire.value = b;
};

const closeDetail = () => {
  selectedBeneficiaire.value = null;
};

function initials(b) {
  const p = b.prenom || "";
  const n = b.nom || "";
  return ((p[0] || "") + (n[0] || "")).toUpperCase() || "?";
}

function niveauFromScore(score) {
  const s = Number(score || 0);
  if (s >= 80) return "Très élevée";
  if (s >= 60) return "Élevée";
  if (s >= 40) return "Moyenne";
  return "Faible";
}

function scoreColorClass(score) {
  const s = Number(score || 0);
  return s >= 60 ? "text-rose-baraka" : "text-bleu-nuit";
}

function scoreBgClass(score) {
  const s = Number(score || 0);
  return s >= 60 ? "bg-rose-baraka" : "bg-bleu-nuit";
}

function scoreAvatarClass(score) {
  const s = Number(score || 0);
  return s >= 60 ? "bg-rose-baraka/10 text-rose-baraka" : "bg-bleu-nuit/10 text-bleu-nuit";
}

function scoreBarClass(score) {
  const s = Number(score || 0);
  return s >= 60 ? "bg-rose-baraka" : "bg-bleu-nuit";
}

function niveauBadgeClass(score) {
  const s = Number(score || 0);
  return s >= 60 ? "bg-rose-baraka/10 text-rose-baraka" : "bg-bleu-nuit/10 text-bleu-nuit";
}

function formatDate(iso) {
  if (!iso) return "—";
  return dayjs(iso).format("DD/MM/YYYY");
}

useAutoRefresh(fetchData, 60_000);
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-scale-up {
  animation: scaleUp 0.2s ease-out forwards;
}
</style>
