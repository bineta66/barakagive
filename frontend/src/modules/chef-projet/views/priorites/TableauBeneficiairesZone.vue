<template>
  <div class="p-6 space-y-6 bg-slate-50 min-h-screen">
    <!-- En-tête & Navigation -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <div class="flex items-start gap-4">
        <button
          @click="goBack"
          class="mt-1 p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors shadow-xs"
          title="Retour à la carte des priorités"
        >
          <ArrowLeft :size="20" />
        </button>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-2xl font-bold text-slate-900">
              Bénéficiaires — {{ zoneInfo?.nom || zoneName || "Zone" }}
            </h1>
            <span
              v-if="zoneInfo"
              class="px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider"
              :class="niveauBadgeClass(zoneInfo.score_moyen)"
            >
              {{ zoneInfo.niveau || niveauFromScore(zoneInfo.score_moyen) }}
            </span>
          </div>
          <p class="text-sm text-slate-500 mt-1 flex items-center gap-2 flex-wrap">
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

      <!-- Actions header -->
      <div class="flex items-center gap-3">
        <button
          @click="fetchData"
          class="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors"
          title="Rafraîchir"
        >
          <RefreshCw :size="18" :class="{ 'animate-spin': loading }" />
        </button>
        <button
          @click="goBack"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm transition-colors"
        >
          <MapPinned :size="16" />
          Carte des priorités
        </button>
      </div>
    </div>

    <!-- KPIs Zone -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Bénéficiaires</p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black text-slate-900">{{ beneficiaires.length }}</p>
          <span class="p-2 rounded-xl bg-blue-50 text-blue-600">
            <Users :size="20" />
          </span>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Score Moyen Zone</p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black" :class="scoreColorClass(zoneInfo?.score_moyen || 0)">
            {{ zoneInfo?.score_moyen ?? 0 }}<span class="text-sm font-bold text-slate-400"> /100</span>
          </p>
          <span class="p-2 rounded-xl bg-amber-50 text-amber-600">
            <Activity :size="20" />
          </span>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Bénéficiaires Prioritaires</p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black text-red-600">{{ countPrioritaires }}</p>
          <span class="p-2 rounded-xl bg-red-50 text-red-600">
            <AlertTriangle :size="20" />
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-1">Score vulnérabilité ≥ 60</p>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Critères Projet Évalués</p>
        <div class="flex items-baseline justify-between mt-2">
          <p class="text-3xl font-black text-indigo-600">{{ criteresProjet.length }}</p>
          <span class="p-2 rounded-xl bg-indigo-50 text-indigo-600">
            <CheckSquare :size="20" />
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-1">Critères d'éligibilité actifs</p>
      </div>
    </div>

    <!-- Barre de recherche & Filtres -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="relative w-full md:w-96">
        <Search :size="18" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher par nom, téléphone, quartier..."
          class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-or/30 focus:border-or transition-all"
        />
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto flex-wrap">
        <!-- Filtre par niveau -->
        <select
          v-model="filterNiveau"
          class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-or/30"
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
          class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-or/30"
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
    <div v-if="loading" class="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-or mx-auto mb-3"></div>
      <p class="text-sm font-medium text-slate-600">Chargement des données des bénéficiaires...</p>
    </div>

    <!-- Erreur -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
      <p class="text-sm text-red-600 font-semibold">{{ error }}</p>
      <button
        @click="fetchData"
        class="mt-3 px-4 py-2 bg-red-600 text-white text-xs font-semibold rounded-lg hover:bg-red-700 transition-colors"
      >
        Réessayer
      </button>
    </div>

    <!-- Aucun bénéficiaire trouvé -->
    <div v-else-if="filteredBeneficiaires.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
      <Users :size="40" class="mx-auto text-slate-300 mb-3" />
      <p class="text-base font-semibold text-slate-700">Aucun bénéficiaire ne correspond aux critères</p>
      <p class="text-sm text-slate-400 mt-1">Modifiez vos filtres ou effectuez une nouvelle recherche.</p>
    </div>

    <!-- Tableau des Bénéficiaires -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="bg-slate-50/80 border-b border-slate-200 text-slate-600 text-xs uppercase tracking-wider font-semibold">
              <th class="py-3.5 px-5">Rang</th>
              <th class="py-3.5 px-5">Bénéficiaire</th>
              <th class="py-3.5 px-5">Infos personnelles</th>
              <th class="py-3.5 px-5">Score & Vulnérabilité</th>
              <th class="py-3.5 px-5">Critères validés</th>
              <th class="py-3.5 px-5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="(b, index) in filteredBeneficiaires"
              :key="b.id"
              class="hover:bg-blue-50/40 transition-colors group cursor-pointer"
              @click="openDetail(b)"
            >
              <!-- Rang -->
              <td class="py-4 px-5">
                <span
                  class="w-7 h-7 rounded-full inline-flex items-center justify-center text-xs font-black text-white"
                  :class="scoreBgClass(b.score)"
                >
                  {{ index + 1 }}
                </span>
              </td>

              <!-- Nom & Bénéficiaire -->
              <td class="py-4 px-5">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0"
                    :class="scoreAvatarClass(b.score)"
                  >
                    {{ initials(b) }}
                  </div>
                  <div>
                    <h4 class="font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                      {{ b.nom_complet }}
                    </h4>
                    <p class="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                      <Phone :size="12" class="text-slate-400" />
                      {{ b.telephone || "Téléphone non renseigné" }}
                    </p>
                  </div>
                </div>
              </td>

              <!-- Infos Personnelles -->
              <td class="py-4 px-5">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2 py-0.5 rounded text-[11px] font-bold"
                      :class="b.sexe === 'F' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'"
                    >
                      {{ b.sexe === 'F' ? 'Femme' : b.sexe === 'M' ? 'Homme' : '—' }}
                    </span>
                    <span class="text-xs text-slate-700 font-medium">
                      {{ b.age ? b.age + ' ans' : 'Âge non renseigné' }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-500">
                    Quartier / Dép : <span class="text-slate-700 font-medium">{{ b.quartier || "—" }}</span>
                  </p>
                </div>
              </td>

              <!-- Score & Vulnérabilité -->
              <td class="py-4 px-5">
                <div class="space-y-1.5 min-w-[140px]">
                  <div class="flex items-center justify-between gap-2">
                    <span class="text-base font-black" :class="scoreColorClass(b.score)">
                      {{ b.score }}<span class="text-xs text-slate-400 font-semibold"> /100</span>
                    </span>
                    <span
                      class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider"
                      :class="niveauBadgeClass(b.score)"
                    >
                      {{ b.niveau || niveauFromScore(b.score) }}
                    </span>
                  </div>
                  <div class="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-500"
                      :class="scoreBarClass(b.score)"
                      :style="{ width: b.score + '%' }"
                    />
                  </div>
                </div>
              </td>

              <!-- Critères validés -->
              <td class="py-4 px-5">
                <div class="flex flex-wrap gap-1.5 max-w-md">
                  <template v-if="b.criteres && b.criteres.length">
                    <span
                      v-for="(c, cIdx) in b.criteres"
                      :key="cIdx"
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium"
                      :class="c.obtenu ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-500 border border-slate-200'"
                      :title="`${c.nom} : ${c.reponse} (${c.points}/${c.poids_max} pts)`"
                    >
                      <CheckCircle2 v-if="c.obtenu" :size="11" class="text-emerald-600 flex-shrink-0" />
                      <XCircle v-else :size="11" class="text-slate-400 flex-shrink-0" />
                      <span class="truncate max-w-[120px]">{{ c.nom }}</span>
                      <strong v-if="c.obtenu" class="text-emerald-800 font-bold">+{{ c.points }}</strong>
                    </span>
                  </template>
                  <span v-else class="text-xs text-slate-400 italic">Aucun critère renseigné</span>
                </div>
              </td>

              <!-- Actions -->
              <td class="py-4 px-5 text-right">
                <button
                  @click.stop="openDetail(b)"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-semibold text-xs transition-colors shadow-2xs"
                >
                  <Eye :size="14" />
                  <span>Fiche</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer du tableau -->
      <div class="px-5 py-3 bg-slate-50/60 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
        <span>Affichage de {{ filteredBeneficiaires.length }} bénéficiaire(s) sur {{ beneficiaires.length }}</span>
        <span>Trié par : {{ sortLabel }}</span>
      </div>
    </div>

    <!-- MODAL : FICHE DÉTAILLÉE DU BÉNÉFICIAIRE -->
    <Transition name="fade">
      <div
        v-if="selectedBeneficiaire"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
        @click.self="closeDetail"
      >
        <div class="bg-white rounded-3xl border border-slate-200 shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-scale-up">
          <!-- Modal Header -->
          <div class="p-6 border-b border-slate-100 flex items-start justify-between bg-slate-50/60">
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
                  <span>{{ selectedBeneficiaire.sexe === 'F' ? 'Femme' : 'Homme' }}</span>
                  <span>•</span>
                  <span>{{ selectedBeneficiaire.age ? selectedBeneficiaire.age + ' ans' : 'Âge non renseigné' }}</span>
                  <span>•</span>
                  <span>{{ selectedBeneficiaire.quartier || zoneInfo?.nom }}</span>
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <div class="flex flex-col items-end">
                <span class="text-2xl font-black" :class="scoreColorClass(selectedBeneficiaire.score)">
                  {{ selectedBeneficiaire.score }}<span class="text-xs text-slate-400 font-semibold"> /100</span>
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
              <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                Informations Personnelles
              </h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Téléphone</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">{{ selectedBeneficiaire.telephone || "—" }}</p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Date de Naissance</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">{{ selectedBeneficiaire.date_naissance || "—" }}</p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Quartier / Dép.</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">{{ selectedBeneficiaire.quartier || "—" }}</p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Zone</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">{{ selectedBeneficiaire.zone_nom || zoneInfo?.nom }}</p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Région</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">{{ selectedBeneficiaire.region || zoneInfo?.region }}</p>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p class="text-[11px] text-slate-400 font-semibold">Date d'inscription</p>
                  <p class="text-sm font-bold text-slate-800 mt-0.5">
                    {{ selectedBeneficiaire.created_at ? formatDate(selectedBeneficiaire.created_at) : "—" }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Détail des Critères de Vulnérabilité -->
            <div>
              <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
                <span>Évaluation des critères du projet</span>
                <span class="text-slate-600 font-bold">
                  {{ (selectedBeneficiaire.criteres || []).filter(c => c.obtenu).length }} validé(s) sur {{ (selectedBeneficiaire.criteres || []).length }}
                </span>
              </h4>
              <div class="border border-slate-200 rounded-2xl overflow-hidden divide-y divide-slate-100">
                <div
                  v-for="(critere, idx) in selectedBeneficiaire.criteres || []"
                  :key="idx"
                  class="p-3.5 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  :class="critere.obtenu ? 'bg-emerald-50/30' : ''"
                >
                  <div class="flex items-center gap-3">
                    <span
                      class="w-6 h-6 rounded-full flex items-center justify-center"
                      :class="critere.obtenu ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-400'"
                    >
                      <CheckCircle2 v-if="critere.obtenu" :size="15" />
                      <XCircle v-else :size="15" />
                    </span>
                    <div>
                      <p class="text-sm font-semibold text-slate-800">{{ critere.nom }}</p>
                      <p class="text-xs text-slate-500">
                        Réponse : <strong class="text-slate-700">{{ critere.reponse || "—" }}</strong>
                      </p>
                    </div>
                  </div>

                  <div class="text-right">
                    <span
                      class="text-sm font-bold px-2.5 py-1 rounded-lg"
                      :class="critere.obtenu ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'"
                    >
                      {{ critere.points }} / {{ critere.poids_max }} pts
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Réponses Complètes aux Questions (le cas échéant) -->
            <div v-if="selectedBeneficiaire.responses && selectedBeneficiaire.responses.length">
              <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                Réponses détaillées au formulaire
              </h4>
              <div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-2">
                <div
                  v-for="(resp, rIdx) in selectedBeneficiaire.responses"
                  :key="rIdx"
                  class="flex items-start justify-between py-1.5 border-b border-slate-200/50 last:border-0 text-xs"
                >
                  <span class="text-slate-600 font-medium">{{ resp.question }} :</span>
                  <span class="text-slate-900 font-bold ml-3 text-right">
                    {{ resp.valeur === true ? 'Oui' : resp.valeur === false ? 'Non' : resp.valeur || '—' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
            <button
              @click="closeDetail"
              class="px-5 py-2.5 bg-slate-800 hover:bg-slate-900 text-white font-semibold text-xs rounded-xl transition-colors shadow-sm"
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
import { ref, computed, onMounted } from "vue";
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
  RefreshCw,
  Phone,
  Eye,
  X,
  CheckCircle2,
  XCircle,
} from "lucide-vue-next";

const route = useRoute();
const router = useRouter();

const zoneId = computed(() => route.params.zoneId || route.query.zoneId || route.query.zone || "");
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
const selectedBeneficiaire = ref(null);

const countPrioritaires = computed(() => {
  return beneficiaires.value.filter((b) => (b.score || 0) >= 60).length;
});

const sortLabel = computed(() => {
  switch (sortBy.value) {
    case "score_desc": return "Score décroissant";
    case "score_asc": return "Score croissant";
    case "nom_asc": return "Nom A-Z";
    case "nom_desc": return "Nom Z-A";
    case "age_desc": return "Âge décroissant";
    default: return "Score";
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
    list = list.filter((b) => (b.niveau || niveauFromScore(b.score)) === filterNiveau.value);
  }

  // Tri
  list.sort((a, b) => {
    if (sortBy.value === "score_desc") return (b.score || 0) - (a.score || 0);
    if (sortBy.value === "score_asc") return (a.score || 0) - (b.score || 0);
    if (sortBy.value === "nom_asc") return (a.nom || "").localeCompare(b.nom || "");
    if (sortBy.value === "nom_desc") return (b.nom || "").localeCompare(a.nom || "");
    if (sortBy.value === "age_desc") return (b.age || 0) - (a.age || 0);
    return 0;
  });

  return list;
});

const fetchData = async () => {
  if (!zoneId.value) {
    error.value = "Identifiant de la zone manquant.";
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    const response = await api.get(`/api/beneficiaries/zone/${zoneId.value}/`);
    zoneInfo.value = response.data.zone || null;
    beneficiaires.value = response.data.beneficiaires || [];
    criteresProjet.value = response.data.criteres_projet || [];
    if (beneficiaires.value.length > 0 && beneficiaires.value[0].campagne) {
      campagneNom.value = beneficiaires.value[0].campagne.nom;
    }
  } catch (err) {
    console.error("Erreur chargement bénéficiaires zone:", err);
    error.value = err.response?.data?.detail || "Impossible de charger la liste des bénéficiaires de cette zone.";
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push("/chef-projet/carte-priorites");
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
  if (s >= 80) return "text-red-600";
  if (s >= 60) return "text-orange-600";
  if (s >= 40) return "text-yellow-600";
  return "text-green-600";
}

function scoreBgClass(score) {
  const s = Number(score || 0);
  if (s >= 80) return "bg-red-500";
  if (s >= 60) return "bg-orange-500";
  if (s >= 40) return "bg-yellow-500";
  return "bg-green-500";
}

function scoreAvatarClass(score) {
  const s = Number(score || 0);
  if (s >= 80) return "bg-red-100 text-red-700";
  if (s >= 60) return "bg-orange-100 text-orange-700";
  if (s >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
}

function scoreBarClass(score) {
  const s = Number(score || 0);
  if (s >= 80) return "bg-red-500";
  if (s >= 60) return "bg-orange-500";
  if (s >= 40) return "bg-yellow-500";
  return "bg-green-500";
}

function niveauBadgeClass(score) {
  const s = Number(score || 0);
  if (s >= 80) return "bg-red-100 text-red-700";
  if (s >= 60) return "bg-orange-100 text-orange-700";
  if (s >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
}

function formatDate(iso) {
  if (!iso) return "—";
  return dayjs(iso).format("DD/MM/YYYY");
}

onMounted(() => {
  fetchData();
});
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
