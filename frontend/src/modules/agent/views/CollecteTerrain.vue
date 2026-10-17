<template>
  <div class="collecte-page">

    <!-- ═══════════════════════════════════════════════════════
         HEADER STICKY
    ═══════════════════════════════════════════════════════ -->
    <div class="ct-header">
      <div class="ct-header__left">
        <RouterLink
          class="ct-back-btn"
          :to="form.campagne_id ? `/agent/campagnes/${form.campagne_id}/beneficiaires` : '/agent/campagnes'"
          aria-label="Retour à la campagne"
        >
          <ArrowLeft :size="18" />
        </RouterLink>
        <div>
          <BreadcrumbNav :items="breadcrumbItems" />
          <p class="ct-header__eyebrow">Collecte terrain</p>
          <h1 class="ct-header__title">{{ campagneNom || "Formulaire" }}</h1>
        </div>
      </div>

    </div>



    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.visible" class="ct-toast" :class="toastClass">
        <component :is="toast.type === 'success' ? CheckCircle2 : toast.type === 'warning' ? AlertTriangle : AlertCircle" :size="18" />
        {{ toast.message }}
      </div>
    </Transition>

    <!-- ═══════════════════════════════════════════════════════
         FORMULAIRE
    ═══════════════════════════════════════════════════════ -->
    <form class="ct-form" @submit.prevent="soumettre" novalidate>

      <!-- ─── Section 1 : Contexte ──────────────────────────── -->
      <section class="ct-section">
        <div class="ct-section__header">
          <div class="ct-section__num">1</div>
          <div>
            <h2 class="ct-section__title">Contexte d'intervention</h2>
            <p class="ct-section__sub">Campagne et zone d'affectation</p>
          </div>
        </div>

        <div class="ct-grid-2">
          <!-- Campagne (pré-sélectionnée si routée) -->
          <div class="ct-field">
            <label for="ct-campagne" class="ct-label">
              Campagne <span class="ct-required">*</span>
            </label>
            <select
              id="ct-campagne"
              v-model="form.campagne_id"
              class="ct-select"
              :class="{ 'ct-input--error': errors.campagne_id }"
              @change="onCampagneChange"
            >
              <option value="">— Sélectionner une campagne —</option>
              <option v-for="c in campaignStore.campaigns" :key="c.id" :value="c.id">
                {{ c.nom }}
              </option>
            </select>
            <p v-if="errors.campagne_id" class="ct-error">{{ errors.campagne_id }}</p>
          </div>

          <!-- Zone -->
          <div class="ct-field">
            <label for="ct-zone" class="ct-label">
              Zone <span class="ct-required">*</span>
            </label>
            <select
              id="ct-zone"
              v-model="form.zone_id"
              class="ct-select"
              :class="{ 'ct-input--error': errors.zone_id }"
              @change="onZoneChange"
            >
              <option value="">— Sélectionner une zone —</option>
              <option v-for="z in zonesDisponibles" :key="z.id" :value="z.id">
                {{ z.nom }}
              </option>
            </select>
            <p v-if="errors.zone_id" class="ct-error">{{ errors.zone_id }}</p>
          </div>
        </div>

        <p class="mt-3 text-xs text-slate-500">La position n’est utilisée que pour associer la collecte au lieu. Elle est demandée uniquement si vous appuyez sur « Détecter ma position ».</p>
        <!-- Chargement du formulaire dynamique -->
        <div v-if="loadingFormulaire" class="ct-loading">
          <Loader2 :size="16" class="animate-spin" />
          Chargement du questionnaire…
        </div>
      </section>

      <!-- ─── Section 2 : Bénéficiaire ─────────────────────── -->
      <section class="ct-section">
        <div class="ct-section__header">
          <div class="ct-section__num">2</div>
          <div>
            <h2 class="ct-section__title">Informations du bénéficiaire</h2>
            <p class="ct-section__sub">Identité et coordonnées</p>
          </div>
        </div>

        <div class="ct-grid-2">
          <!-- Nom -->
          <div class="ct-field">
            <label for="ct-nom" class="ct-label">
              Nom <span class="ct-required">*</span>
            </label>
            <input
              id="ct-nom"
              v-model="form.beneficiary.nom"
              type="text"
              placeholder="Ex : Diallo"
              class="ct-input"
              :class="{ 'ct-input--error': errors.nom }"
            />
            <p v-if="errors.nom" class="ct-error">{{ errors.nom }}</p>
          </div>

          <!-- Prénom -->
          <div class="ct-field">
            <label for="ct-prenom" class="ct-label">
              Prénom <span class="ct-required">*</span>
            </label>
            <input
              id="ct-prenom"
              v-model="form.beneficiary.prenom"
              type="text"
              placeholder="Ex : Aminata"
              class="ct-input"
              :class="{ 'ct-input--error': errors.prenom }"
            />
            <p v-if="errors.prenom" class="ct-error">{{ errors.prenom }}</p>
          </div>

          <!-- Téléphone -->
          <div class="ct-field">
            <label for="ct-tel" class="ct-label">
              Téléphone <span class="ct-required">*</span>
            </label>
            <input
              id="ct-tel"
              v-model="form.beneficiary.telephone"
              type="tel"
              placeholder="+221 77 123 45 67"
              class="ct-input"
              :class="{ 'ct-input--error': errors.telephone }"
            />
            <p v-if="errors.telephone" class="ct-error">{{ errors.telephone }}</p>
          </div>

          <!-- Sexe -->
          <div class="ct-field">
            <label for="ct-sexe" class="ct-label">
              Sexe <span class="ct-required">*</span>
            </label>
            <select
              id="ct-sexe"
              v-model="form.beneficiary.sexe"
              class="ct-select"
              :class="{ 'ct-input--error': errors.sexe }"
            >
              <option value="">— Sélectionner —</option>
              <option value="F">Femme</option>
              <option value="M">Homme</option>
              <option value="AUTRE">Autre</option>
            </select>
            <p v-if="errors.sexe" class="ct-error">{{ errors.sexe }}</p>
          </div>

          <!-- Date de naissance -->
          <div class="ct-field">
            <label for="ct-ddn" class="ct-label">
              Date de naissance <span class="ct-required">*</span>
            </label>
            <input
              id="ct-ddn"
              v-model="form.beneficiary.date_naissance"
              type="date"
              class="ct-input"
              :class="{ 'ct-input--error': errors.date_naissance }"
            />
            <p v-if="errors.date_naissance" class="ct-error">{{ errors.date_naissance }}</p>
          </div>
        </div>
      </section>

      <!-- ─── Section 3 : Questionnaire dynamique ──────────── -->
      <section v-if="questions.length > 0" class="ct-section">
        <div class="ct-section__header">
          <div class="ct-section__num">3</div>
          <div>
            <h2 class="ct-section__title">Questionnaire</h2>
            <p class="ct-section__sub">{{ questions.length }} question(s)</p>
          </div>
        </div>

        <div
          v-for="(q, i) in questions"
          :key="q.id"
          class="ct-question"
          @input="validerReponse(q)"
          @change="validerReponse(q)"
        >
          <label class="ct-label">
            {{ i + 1 }}. {{ q.label || q.texte }}
            <span v-if="q.required || q.obligatoire" class="ct-required">*</span>
          </label>

          <!-- TEXT -->
          <input
            v-if="q.type === 'TEXT' || q.type === 'text'"
            v-model="reponses[q.id]"
            type="text"
            class="ct-input"
            :placeholder="q.placeholder || ''"
          />

          <input
            v-else-if="q.type === 'PHONE' || q.type === 'phone'"
            v-model="reponses[q.id]"
            type="tel"
            inputmode="tel"
            class="ct-input"
            :placeholder="q.placeholder || '+221 77 123 45 67'"
          />

          <input v-else-if="q.type === 'EMAIL'" v-model="reponses[q.id]" type="email" class="ct-input" placeholder="nom@exemple.org" />

          <input
            v-else-if="q.type === 'DATE' || q.type === 'date'"
            v-model="reponses[q.id]"
            type="date"
            class="ct-input"
          />

          <!-- NUMBER -->
          <input
            v-else-if="q.type === 'NUMBER' || q.type === 'number'"
            v-model.number="reponses[q.id]"
            type="number"
            step="any"
            class="ct-input"
          />

          <select
            v-else-if="q.type === 'YES_NO' || q.type === 'yes_no'"
            v-model="reponses[q.id]"
            class="ct-select"
          >
            <option value="">— Choisir —</option>
            <option :value="true">Oui</option>
            <option :value="false">Non</option>
          </select>

          <div v-else-if="q.type === 'RADIO'" class="ct-checkboxes">
            <label v-for="opt in (q.options || [])" :key="opt" class="ct-checkbox"><input type="radio" :name="`q-${q.id}`" :value="opt" v-model="reponses[q.id]">{{ opt }}</label>
          </div>

          <!-- SELECT -->
          <select
            v-else-if="q.type === 'SELECT' || q.type === 'select'"
            v-model="reponses[q.id]"
            class="ct-select"
          >
            <option value="">— Choisir —</option>
            <option v-for="opt in (q.options || q.choices || [])" :key="opt" :value="opt">
              {{ opt }}
            </option>
          </select>

          <!-- CHECKBOX -->
          <div
            v-else-if="q.type === 'CHECKBOX' || q.type === 'checkbox'"
            class="ct-checkboxes"
          >
            <label
              v-for="opt in (q.options || q.choices || [])"
              :key="opt"
              class="ct-checkbox"
            >
              <input
                type="checkbox"
                :value="opt"
                v-model="reponses[q.id]"
              />
              {{ opt }}
            </label>
          </div>

          <div v-else-if="q.type === 'SCALE'" class="flex justify-between gap-2 py-2">
            <label v-for="n in 5" :key="n" class="flex flex-col items-center gap-1 text-sm text-slate-600"><input type="radio" :name="`q-${q.id}`" :value="n" v-model="reponses[q.id]">{{ n }}</label>
          </div>

          <label v-else-if="q.type === 'PHOTO' || q.type === 'FILE'" class="block rounded-lg border border-dashed border-slate-300 p-3 text-sm text-slate-600">
            <span class="mb-2 block">{{ q.type === 'PHOTO' ? 'Ajouter une photo' : 'Joindre un fichier' }}</span><input type="file" :accept="q.type === 'PHOTO' ? 'image/*' : undefined" @change="reponses[q.id] = $event.target.files?.[0]?.name || ''" class="w-full text-xs">
          </label>

          <div v-else-if="q.type === 'GPS' || q.type === 'gps'" class="grid grid-cols-2 gap-2">
            <input v-model="reponses[q.id].latitude" type="number" min="-90" max="90" step="any" class="ct-input" placeholder="Latitude" />
            <input v-model="reponses[q.id].longitude" type="number" min="-180" max="180" step="any" class="ct-input" placeholder="Longitude" />
          </div>

          <!-- TEXTAREA par défaut -->
          <textarea
            v-else
            v-model="reponses[q.id]"
            rows="3"
            class="ct-textarea"
            :placeholder="q.placeholder || ''"
          />

          <p v-if="errors[`q_${q.id}`]" class="ct-error">
            {{ errors[`q_${q.id}`] }}
          </p>
        </div>
      </section>

      <!-- ─── Section 4 : GPS ───────────────────────────────── -->
      <section class="ct-section">
        <div class="ct-section__header">
          <div class="ct-section__num" :class="questions.length > 0 ? '' : 'ct-section__num--3'">
            {{ questions.length > 0 ? 4 : 3 }}
          </div>
          <div>
            <h2 class="ct-section__title">Position GPS</h2>
            <p class="ct-section__sub">Localisation de l'enregistrement</p>
          </div>
        </div>

        <div class="ct-gps">
          <div class="ct-gps__fields">
            <div class="ct-field">
              <label class="ct-label">Latitude</label>
              <input
                :value="form.beneficiary.latitude"
                type="text"
                readonly
                class="ct-input ct-input--readonly"
                :class="{ 'ct-input--error': errors.gps }"
                placeholder="Non détecté"
              />
            </div>
            <div class="ct-field">
              <label class="ct-label">Longitude</label>
              <input
                :value="form.beneficiary.longitude"
                type="text"
                readonly
                class="ct-input ct-input--readonly"
                placeholder="Non détecté"
              />
            </div>
          </div>

          <button type="button" class="ct-gps__btn" @click="detecterGPS" :disabled="gpsLoading">
            <Loader2 v-if="gpsLoading" :size="16" class="animate-spin" />
            <MapPin v-else :size="16" />
            {{ gpsLoading ? "Détection…" : "Détecter ma position" }}
          </button>

          <p class="mt-2 text-xs text-slate-500">La position est utilisée uniquement pour associer la collecte au lieu. L’autorisation est demandée après votre action sur ce bouton.</p>

          <p v-if="errors.gps" class="ct-error">{{ errors.gps }}</p>
          <p v-if="gpsSuccess" class="ct-success">
            <CheckCircle2 :size="13" />
            {{ gpsSource === 'zone' ? 'Coordonnées enregistrées de la zone utilisées.' : 'Position GPS détectée avec succès.' }}
          </p>
        </div>
      </section>

      <!-- ─── Bouton de soumission ──────────────────────────── -->
      <div class="ct-submit-row">
        <button
          type="submit"
          class="ct-submit-btn"
          :class="{ 'ct-submit-btn--offline': !isOnline }"
          :disabled="submitting"
        >
          <Loader2 v-if="submitting" :size="18" class="animate-spin" />
          <Send v-else-if="isOnline" :size="18" />
          <Save v-else :size="18" />
          {{
            submitting
              ? "Enregistrement…"
              : isOnline
              ? "Enregistrer le bénéficiaire"
              : "Sauvegarder localement"
          }}
        </button>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import BreadcrumbNav from "@/components/ui/BreadcrumbNav.vue";
import {
  ArrowLeft,
  Wifi,
  WifiOff,
  MapPin,
  Send,
  Save,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
} from "lucide-vue-next";



import { useCampaignStore } from "@/stores/campaign";
import api from "@/services/api.js";
import { useBeneficiaryStore } from "@/stores/beneficiary";
import { useOnlineStatus } from "@/composables/useOnlineStatus";
import { offlineStorage } from "@/services/offlineStorage";

const route = useRoute();
const router = useRouter();

const campaignStore = useCampaignStore();
const beneficiaryStore = useBeneficiaryStore();
const { isOnline } = useOnlineStatus();

// ── État du formulaire ────────────────────────────────────────────────────
const form = reactive({
  campagne_id: "",
  zone_id: "",
  formulaire_id: null,
  beneficiary: {
    nom: "",
    prenom: "",
    telephone: "",
    sexe: "",
    date_naissance: "",
    latitude: "",
    longitude: "",
  },
});

const reponses = reactive({});
const errors = reactive({});

const questions = ref([]);
const loadingFormulaire = ref(false);
const submitting = ref(false);
const gpsLoading = ref(false);
const gpsSuccess = ref(false);
const gpsSource = ref("device"); // 'device' | 'zone'
const campagneNom = ref("");
const breadcrumbItems = computed(() => [
  { label: "Mes campagnes", to: "/agent/campagnes" },
  ...(form.campagne_id
    ? [{ label: campagneNom.value || "Campagne", to: `/agent/campagnes/${form.campagne_id}/beneficiaires` }]
    : []),
  { label: "Collecte terrain" },
]);

// ── Toast ─────────────────────────────────────────────────────────────────
const toast = reactive({ visible: false, message: "", type: "success" });
let toastTimer = null;

const toastClass = computed(() => ({
  "ct-toast--success": toast.type === "success",
  "ct-toast--warning": toast.type === "warning",
  "ct-toast--error": toast.type === "error",
}));

const afficherToast = (message, type = "success", duration = 4000) => {
  if (toastTimer) clearTimeout(toastTimer);
  toast.message = message;
  toast.type = type;
  toast.visible = true;
  toastTimer = setTimeout(() => { toast.visible = false; }, duration);
};

// ── Zones disponibles pour la campagne sélectionnée ──────────────────────
const zonesDisponibles = computed(() => {
  if (!form.campagne_id) return [];

  // Les campagnes mises en cache proviennent uniquement de l'endpoint agent.
  const allCampaigns = campaignStore.campaigns.length
    ? campaignStore.campaigns
    : offlineStorage.getCachedCampaigns();

  const camp = allCampaigns.find(
    (c) => String(c.id) === String(form.campagne_id)
  );

  const rawZones = camp?.zones || [];

  if (!Array.isArray(rawZones)) return [];
  return rawZones.filter((zone) => zone && typeof zone === "object" && zone.id && zone.nom)
    .map((zone) => ({ id: String(zone.id), nom: zone.nom, latitude: zone.latitude || null, longitude: zone.longitude || null }));
});

// ── Remplissage des coordonnées GPS à partir de la zone ou région ──────────
const remplirGPSDepuisZone = () => {
  const selectedZone = zonesDisponibles.value.find(
    (z) => String(z.id) === String(form.zone_id) || String(z.nom) === String(form.zone_id)
  );

  if (selectedZone && selectedZone.latitude && selectedZone.longitude && String(selectedZone.latitude) !== "0") {
    form.beneficiary.latitude = String(selectedZone.latitude);
    form.beneficiary.longitude = String(selectedZone.longitude);
    gpsSuccess.value = true;
    gpsSource.value = "zone";
    delete errors.gps;
    return true;
  }

  errors.gps = "Aucune coordonnée n’est enregistrée pour cette zone. Autorisez la géolocalisation ou contactez votre responsable.";
  return false;
};

// ── Changement de zone sélectionnée ────────────────────────────────────────
const onZoneChange = () => {
  if (!form.zone_id) return;

  // En mode hors connexion OU si les champs GPS sont encore vides :
  // Remplir automatiquement la latitude et longitude depuis la zone ou sa région
  if (!isOnline.value || !form.beneficiary.latitude || !form.beneficiary.longitude) {
    remplirGPSDepuisZone();
  }
};

// ── Initialisation ────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const camps = await campaignStore.fetchAgentCampaigns();
    if (camps && camps.length) offlineStorage.saveCachedCampaigns(camps);
  } catch {
    // Si hors connexion dès le départ, charger le cache
    const cachedCamps = offlineStorage.getCachedCampaigns();
    if (cachedCamps.length) campaignStore.campaigns = cachedCamps;
  }

  // Pré-sélectionner la campagne depuis la route
  const campagneId = route.params.id || route.query.campagne;
  if (campagneId) {
    form.campagne_id = String(campagneId);
    await onCampagneChange();

    // La page Mes zones transmet l'identifiant de la zone à utiliser pour cette collecte.
    const requestedZoneId = route.query.zone_id || route.query.zone;
    if (requestedZoneId) {
      const matchingZone = zonesDisponibles.value.find(
        (zone) => String(zone.id) === String(requestedZoneId)
      );
      if (matchingZone) {
        form.zone_id = String(matchingZone.id);
        onZoneChange();
      }
    }
  }

});

// ── Réagir au basculement en mode hors connexion ──────────────────────────
watch(isOnline, (online) => {
  if (!online && form.zone_id) {
    remplirGPSDepuisZone();
  }
});

// ── Changement de campagne → charger formulaire dynamique ─────────────────
const onCampagneChange = async () => {
  questions.value = [];
  form.formulaire_id = null;
  form.zone_id = "";
  gpsSuccess.value = false;
  Object.keys(reponses).forEach(k => delete reponses[k]);
  Object.keys(errors).forEach(k => delete errors[k]);

  if (!form.campagne_id) return;

  const allCampaigns = campaignStore.campaigns.length
    ? campaignStore.campaigns
    : offlineStorage.getCachedCampaigns();

  const camp = allCampaigns.find(
    (c) => String(c.id) === String(form.campagne_id)
  );
  campagneNom.value = camp?.nom || "";

  // Pré-sélectionner la première zone et remplir le GPS
  if (zonesDisponibles.value.length) {
    form.zone_id = zonesDisponibles.value[0].id;
    onZoneChange();
  }

  // Charger le formulaire dynamique de la campagne
  loadingFormulaire.value = true;
  try {
    let full = null;
    if (isOnline.value) {
      const { data } = await api.get(`/api/agent/campagnes/${form.campagne_id}/formulaire/`);
      full = data;
      offlineStorage.saveCachedForm(form.campagne_id, full);
    } else {
      full = offlineStorage.getCachedForm(form.campagne_id);
    }

    if (full) {
      form.formulaire_id = full.id;
      questions.value = full.fields || full.questions || [];

      // Initialiser les réponses
      questions.value.forEach((q) => {
        if (q.type === "CHECKBOX" || q.type === "checkbox") reponses[q.id] = [];
        else if (q.type === "GPS" || q.type === "gps") reponses[q.id] = { latitude: "", longitude: "" };
        else reponses[q.id] = "";
      });
    } else {
      afficherToast("Aucun formulaire publié n’est disponible pour cette campagne.", "error");
    }
  } catch {
    const cachedForm = offlineStorage.getCachedForm(form.campagne_id);
    if (cachedForm) {
      form.formulaire_id = cachedForm.id;
      questions.value = cachedForm.fields || cachedForm.questions || [];
      questions.value.forEach((q) => {
        if (q.type === "CHECKBOX" || q.type === "checkbox") reponses[q.id] = [];
        else if (q.type === "GPS" || q.type === "gps") reponses[q.id] = { latitude: "", longitude: "" };
        else reponses[q.id] = "";
      });
    } else {
      afficherToast("Impossible de charger le formulaire publié de cette campagne.", "error");
    }
  } finally {
    loadingFormulaire.value = false;
  }
};

// ── Détection GPS ─────────────────────────────────────────────────────────
const detecterGPS = () => {
  // En mode hors connexion, priorité immédiate aux coordonnées de la zone sélectionnée
  if (!isOnline.value && form.zone_id) {
    const filled = remplirGPSDepuisZone();
    if (filled) return;
  }

  if (!navigator.geolocation) {
    remplirGPSDepuisZone();
    return;
  }

  gpsLoading.value = true;
  gpsSuccess.value = false;

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      form.beneficiary.latitude = pos.coords.latitude.toFixed(6);
      form.beneficiary.longitude = pos.coords.longitude.toFixed(6);
      gpsLoading.value = false;
      gpsSuccess.value = true;
      gpsSource.value = "device";
      delete errors.gps;
    },
    () => {
      gpsLoading.value = false;
      // Fallback automatique sur les coordonnées de la zone
      const filled = remplirGPSDepuisZone();
      if (!filled) {
        errors.gps = "Position GPS introuvable. Veuillez sélectionner une zone pour pré-remplir les coordonnées.";
      }
    },
    { timeout: 6000, enableHighAccuracy: true }
  );
};

// ── Validations ───────────────────────────────────────────────────────────
const valider = () => {
  Object.keys(errors).forEach(k => delete errors[k]);
  let ok = true;

  if (!form.campagne_id) {
    errors.campagne_id = "Veuillez sélectionner une campagne.";
    ok = false;
  }
  if (!form.formulaire_id) {
    errors.campagne_id = "Aucun formulaire publié n’est disponible pour cette campagne.";
    ok = false;
  }

  if (!form.zone_id) {
    errors.zone_id = "Veuillez sélectionner une zone.";
    ok = false;
  } else {
    // Vérifier que la zone sélectionnée est valide
    const zonesIds = zonesDisponibles.value.map(z => String(z.id));
    const zonesNoms = zonesDisponibles.value.map(z => String(z.nom).toLowerCase().trim());
    const currentZoneVal = String(form.zone_id).toLowerCase().trim();
    if (!zonesIds.includes(String(form.zone_id)) && !zonesNoms.includes(currentZoneVal)) {
      errors.zone_id = "Cette zone n'appartient pas à la campagne sélectionnée.";
      ok = false;
    }
  }

  const nom = form.beneficiary.nom.trim();
  if (!nom) {
    errors.nom = "Le nom est obligatoire.";
    ok = false;
  } else if (!/^[a-zA-ZÀ-ÿ\s'\-]{2,50}$/.test(nom)) {
    errors.nom = "Le nom doit contenir uniquement des lettres, espaces, tirets ou apostrophes (2 à 50 caractères).";
    ok = false;
  }

  const prenom = form.beneficiary.prenom.trim();
  if (!prenom) {
    errors.prenom = "Le prénom est obligatoire.";
    ok = false;
  } else if (!/^[a-zA-ZÀ-ÿ\s'\-]{2,50}$/.test(prenom)) {
    errors.prenom = "Le prénom doit contenir uniquement des lettres, espaces, tirets ou apostrophes (2 à 50 caractères).";
    ok = false;
  }

  const tel = form.beneficiary.telephone.trim().replace(/[\s-]/g, "");
  const telephoneLocal = tel.replace(/^(\+?221)/, "");
  if (!tel) {
    errors.telephone = "Le téléphone est obligatoire.";
    ok = false;
  } else if (!/^(70|75|76|77|78)\d{7}$/.test(telephoneLocal)) {
    errors.telephone = "Numéro sénégalais invalide (ex : 77 123 45 67).";
    ok = false;
  }

  if (!form.beneficiary.sexe) {
    errors.sexe = "Le sexe est obligatoire.";
    ok = false;
  }

  if (!form.beneficiary.date_naissance) {
    errors.date_naissance = "La date de naissance est obligatoire.";
    ok = false;
  } else if (form.beneficiary.date_naissance >= new Date().toISOString().slice(0, 10)) {
    errors.date_naissance = "La date de naissance doit être dans le passé.";
    ok = false;
  }

  for (const question of questions.value) {
    if (!validerReponse(question)) ok = false;
  }

  if (!form.beneficiary.latitude || !form.beneficiary.longitude) {
    remplirGPSDepuisZone();
    if (!form.beneficiary.latitude || !form.beneficiary.longitude) {
      errors.gps = "Détectez votre position avant d’enregistrer la collecte.";
      ok = false;
    }
  }

  return ok;
};

const validerReponse = (question) => {
  const key = `q_${question.id}`;
  const value = reponses[question.id];
  const required = question.obligatoire || question.required;
  const empty = value === null || value === undefined || value === "" || (Array.isArray(value) && value.length === 0);
  let message = "";

  if (empty && required) message = "Ce champ est obligatoire.";
  else if (!empty && ["NUMBER", "number"].includes(question.type) && !Number.isFinite(Number(value))) message = "Veuillez saisir un nombre valide.";
  else if (!empty && ["EMAIL", "email"].includes(question.type) && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value).trim())) message = "Veuillez saisir une adresse e-mail valide.";
  else if (!empty && ["PHONE", "phone"].includes(question.type) && !/^(\+221\s?)?(70|75|76|77|78)\s?\d{3}\s?\d{2}\s?\d{2}$/.test(String(value).trim())) message = "Veuillez saisir un numéro de téléphone valide.";
  else if (!empty && ["DATE", "date"].includes(question.type)) {
    const parsedDate = new Date(`${value}T00:00:00Z`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || Number.isNaN(parsedDate.getTime()) || parsedDate.toISOString().slice(0, 10) !== value) message = "Veuillez saisir une date valide.";
  }
  else if (!empty && ["SELECT", "select"].includes(question.type) && !(question.options || question.choices || []).includes(value)) message = "Veuillez choisir une option valide.";
  else if (!empty && ["RADIO", "radio"].includes(question.type) && !(question.options || question.choices || []).includes(value)) message = "Veuillez choisir une option valide.";
  else if (!empty && ["YES_NO", "yes_no"].includes(question.type) && typeof value !== "boolean") message = "Veuillez choisir oui ou non.";
  else if (!empty && ["SCALE", "scale"].includes(question.type) && ![1, 2, 3, 4, 5].includes(Number(value))) message = "Veuillez choisir une valeur de 1 à 5.";
  else if (!empty && ["CHECKBOX", "checkbox"].includes(question.type) && (!Array.isArray(value) || value.some((option) => !(question.options || question.choices || []).includes(option)))) message = "Veuillez sélectionner des choix valides.";
  else if (!empty && ["GPS", "gps"].includes(question.type)) {
    if (!String(value?.latitude ?? "").trim() || !String(value?.longitude ?? "").trim()) {
      message = required ? "Ce champ est obligatoire." : "";
    }
    const latitude = Number(value?.latitude);
    const longitude = Number(value?.longitude);
    if (!message && (!Number.isFinite(latitude) || latitude < -90 || latitude > 90 || !Number.isFinite(longitude) || longitude < -180 || longitude > 180)) message = "Veuillez saisir des coordonnées GPS valides.";
  }

  if (message) errors[key] = message;
  else delete errors[key];
  return !message;
};

// ── Vérification doublon (en ligne seulement) ─────────────────────────────
const verifierDoublon = async () => {
  try {
    const exist = await beneficiaryStore.checkDuplicate?.({
      campagne_id: form.campagne_id,
      zone_id: form.zone_id,
      nom: form.beneficiary.nom,
      prenom: form.beneficiary.prenom,
      telephone: form.beneficiary.telephone,
    });
    if (exist) {
      errors.nom = "Ce bénéficiaire est déjà enregistré dans cette campagne.";
      return false;
    }
    return true;
  } catch {
    return true; // En cas d'erreur, laisser passer
  }
};

// ── Réinitialiser le formulaire ───────────────────────────────────────────
const reinitialiser = () => {
  form.beneficiary.nom = "";
  form.beneficiary.prenom = "";
  form.beneficiary.telephone = "";
  form.beneficiary.sexe = "";
  form.beneficiary.date_naissance = "";
  form.beneficiary.latitude = "";
  form.beneficiary.longitude = "";
  gpsSuccess.value = false;

  Object.keys(reponses).forEach(k => {
    const question = questions.value.find((item) => String(item.id) === String(k));
    if (question?.type === "CHECKBOX" || question?.type === "checkbox") reponses[k] = [];
    else if (question?.type === "GPS" || question?.type === "gps") reponses[k] = { latitude: "", longitude: "" };
    else reponses[k] = "";
  });
  Object.keys(errors).forEach(k => delete errors[k]);

};

// ── Soumission principale ─────────────────────────────────────────────────
const soumettre = async () => {
  if (!valider()) {
    // Scroller vers la première erreur
    const firstError = document.querySelector(".ct-input--error, .ct-select.ct-input--error");
    firstError?.scrollIntoView({ behavior: "smooth", block: "center" });
    return;
  }

  submitting.value = true;

  const camp = campaignStore.campaigns.find(
    (c) => String(c.id) === String(form.campagne_id)
  );
  const zone = zonesDisponibles.value.find(
    (z) => String(z.id) === String(form.zone_id)
  );

  const payload = {
    local_id: crypto.randomUUID(),
    campagne_id: form.campagne_id,
    campagne_nom: camp?.nom || "",
    zone_id: form.zone_id,
    zone_nom: zone?.nom || "",
    formulaire_id: form.formulaire_id,
    beneficiary: { ...form.beneficiary },
    responses: questions.value.map((q) => ({
      question_id: q.id,
      value: reponses[q.id],
    })),
    timestamp: new Date().toISOString(),
  };

  try {
    if (isOnline.value) {
      // ── Mode en ligne : vérifier doublon puis envoyer ──────
      const sanDoublon = await verifierDoublon();
      if (!sanDoublon) {
        submitting.value = false;
        return;
      }

      const result = await beneficiaryStore.submitBeneficiary(payload);

      if (result.offline) {
        // Le store a basculé en hors ligne au dernier moment
        afficherToast("Données enregistrées localement (connexion perdue).", "warning");
      } else {
        afficherToast("Bénéficiaire enregistré avec succès.", "success");
        reinitialiser();
      }
    } else {
      // ── Mode hors ligne : sauvegarder dans IndexedDB ───────
      await offlineStorage.saveBeneficiary(payload);
      afficherToast("Données enregistrées localement. Elles seront envoyées automatiquement dès le retour d'Internet.", "warning", 6000);
      reinitialiser();
    }
  } catch (e) {
    const status = e.response?.status || e.status;
    if (status === 409) {
      errors.nom = "Ce bénéficiaire est déjà inscrit dans cette campagne.";
      afficherToast("Doublon détecté : bénéficiaire déjà enregistré.", "error");
    } else {
      const data = e.response?.data;
      const beneficiaryErrors = data?.beneficiary;
      if (beneficiaryErrors && typeof beneficiaryErrors === "object") {
        Object.entries(beneficiaryErrors).forEach(([field, messages]) => {
          errors[field] = Array.isArray(messages) ? messages.join(" ") : String(messages);
        });
      }
      for (const field of ["campagne_id", "zone_id"]) {
        if (data?.[field]) {
          errors[field === "campagne_id" ? "campagne_id" : "zone_id"] = Array.isArray(data[field])
            ? data[field].join(" ")
            : String(data[field]);
        }
      }
      const message = data?.detail || (data && typeof data === "object"
        ? Object.entries(data).map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join(", ") : value}`).join("\n")
        : e.message);
      afficherToast(message || "Erreur lors de l'enregistrement. Veuillez réessayer.", "error");
    }
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
/* ── Layout global ───────────────────────────────────────────────────────── */
.collecte-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 40px;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.ct-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.ct-header__left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ct-back-btn {
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
}

.ct-back-btn:hover {
  border-color: #021427;
  color: #021427;
}

.ct-header__eyebrow {
  font-size: 11px;
  font-weight: 700;
  color: #00313c;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}

.ct-header__title {
  font-size: 20px;
  font-weight: 800;
  color: #021427;
  margin: 0;
}

/* ── Bannière connexion ──────────────────────────────────────────────────── */
.ct-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  border-radius: 14px;
  padding: 14px 16px;
  border: 1.5px solid transparent;
  font-size: 13px;
  line-height: 1.5;
}

.ct-banner strong {
  display: block;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 2px;
}

.ct-banner__text {
  margin: 0;
  opacity: 0.85;
  font-size: 12px;
}

.ct-banner--online {
  background: #f0fdf4;
  border-color: #86efac;
  color: #15803d;
}

.ct-banner--offline {
  background: #fff7ed;
  border-color: #fdba74;
  color: #9a3412;
}

/* ── Toast ───────────────────────────────────────────────────────────────── */
.ct-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  left: 20px;
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  z-index: 9999;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
}

.ct-toast--success { background: #021427; color: #fff; }
.ct-toast--warning { background: #00313c; color: #fff; }
.ct-toast--error   { background: #dc2626; color: #fff; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from  { opacity: 0; transform: translateY(-16px); }
.toast-leave-to    { opacity: 0; transform: translateY(-8px); }

/* ── Formulaire ──────────────────────────────────────────────────────────── */
.ct-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Sections ────────────────────────────────────────────────────────────── */
.ct-section {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ct-section__header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.ct-section__num {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: #021427;
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ct-section__title {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.ct-section__sub {
  font-size: 12px;
  color: #94a3b8;
  margin: 2px 0 0;
}

/* ── Grilles ─────────────────────────────────────────────────────────────── */
.ct-grid-2 {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 640px) {
  .ct-grid-2 {
    grid-template-columns: 1fr 1fr;
  }
}

/* ── Champs ──────────────────────────────────────────────────────────────── */
.ct-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ct-label {
  font-size: 12px;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.ct-required {
  color: #ef4444;
  margin-left: 2px;
}

.ct-input,
.ct-select,
.ct-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}

.ct-input:focus,
.ct-select:focus,
.ct-textarea:focus {
  border-color: #021427;
  box-shadow: 0 0 0 3px rgba(2, 20, 39, 0.08);
}

.ct-input--error {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.08) !important;
}

.ct-input--readonly {
  background: #f8fafc;
  color: #64748b;
}

.ct-error {
  font-size: 12px;
  color: #dc2626;
  margin: 0;
}

.ct-success {
  font-size: 12px;
  color: #16a34a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ── Questions ───────────────────────────────────────────────────────────── */
.ct-question {
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #fafafa;
}

.ct-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ct-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #334155;
  cursor: pointer;
}

/* ── GPS ─────────────────────────────────────────────────────────────────── */
.ct-gps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ct-gps__fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.ct-gps__btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1.5px solid #021427;
  border-radius: 10px;
  background: #fff;
  color: #021427;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: fit-content;
}

.ct-gps__btn:hover:not(:disabled) {
  background: #021427;
  color: #fff;
}

.ct-gps__btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Loading formulaire ──────────────────────────────────────────────────── */
.ct-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

/* ── Bouton soumission ───────────────────────────────────────────────────── */
.ct-submit-row {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}

.ct-submit-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border: none;
  border-radius: 14px;
  background: #021427;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  justify-content: center;
}

.ct-submit-btn:hover:not(:disabled) {
  background: #0a2540;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(2, 20, 39, 0.2);
}

.ct-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ct-submit-btn--offline {
  background: #00313c;
}

.ct-submit-btn--offline:hover:not(:disabled) {
  background: #00262f;
  box-shadow: 0 6px 20px rgba(0, 49, 60, 0.2);
}

@media (min-width: 640px) {
  .ct-submit-btn {
    width: auto;
  }
}
</style>
