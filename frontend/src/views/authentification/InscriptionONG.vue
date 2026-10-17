<template>
  <main class="min-h-screen bg-white">
    <div class="grid min-h-screen lg:grid-cols-2">
      <section
        class="relative hidden overflow-hidden bg-bleu-nuit lg:flex lg:flex-col lg:justify-end lg:pb-20"
      >
        <img
          src="@/assets/images/imagelogo.png"
          alt="Une équipe BarakaGive"
          class="absolute inset-0 h-full w-full object-cover opacity-60"
        />
        <div class="absolute inset-0 bg-bleu-nuit/60"></div>
        <div class="relative z-10 px-12 text-white">
          <p
            class="mb-3 text-sm font-bold uppercase tracking-[0.2em] text-white/70"
          >
            BarakaGive
          </p>
          <h1 class="max-w-lg text-4xl font-bold leading-tight">
            Rejoignez BarakaGive avec votre ONG
          </h1>
          <p class="mt-4 max-w-lg text-slate-200">
            Créez votre organisation en 3 étapes. Aucun mot de passe n'est
            demandé pendant l'inscription.
          </p>
        </div>
      </section>

      <section
        class="flex min-h-screen items-start justify-center bg-white px-6 py-10 sm:px-10 lg:overflow-y-auto lg:px-16"
      >
        <div class="w-full max-w-2xl">
          <div class="mb-8 flex items-center gap-3">
            <img
              src="@/assets/images/logologin.png"
              alt="Logo BarakaGive"
              class="h-12 w-12 object-contain"
            />
            <div>
              <p class="text-xl font-bold text-bleu-nuit">BarakaGive</p>
              <p class="text-xs text-slate-500">Inscription ONG</p>
            </div>
          </div>

          <div class="mb-8">
            <div class="flex items-center gap-3">
              <div
                v-for="step in steps"
                :key="step.key"
                class="flex items-center gap-2"
              >
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold"
                  :class="
                    step.key <= currentStep
                      ? 'bg-bleu-nuit text-white'
                      : 'bg-slate-200 text-slate-600'
                  "
                >
                  {{ step.key }}
                </div>
                <span
                  class="hidden text-sm font-semibold sm:inline"
                  :class="
                    step.key <= currentStep
                      ? 'text-slate-900'
                      : 'text-slate-500'
                  "
                >
                  {{ step.label }}
                </span>
              </div>
              <div
                v-if="currentStep < 3"
                class="mx-3 h-px flex-1 bg-slate-200"
              ></div>
            </div>
          </div>

          <AlertMessage
            v-if="errorMessage"
            type="error"
            :message="errorMessage"
            :dismissible="true"
            @dismiss="errorMessage = ''"
            class="mb-6"
          />
          <AlertMessage
            v-if="successMessage"
            type="success"
            :message="successMessage"
            class="mb-6"
          />

          <div v-if="!successMessage" class="space-y-6">
            <div v-if="currentStep === 1">
              <h2 class="text-xl font-bold text-bleu-nuit mb-1">
                Informations de l'ONG
              </h2>
              <p class="text-sm text-slate-600 mb-6">
                Renseignez les informations officielles de votre organisation.
              </p>
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Nom de l'ONG *</label
                  >
                  <input
                    v-model="form.name"
                    type="text"
                    placeholder="Secours Solidarité Sahel"
                    maxlength="120"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e1.name
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p v-if="e1.name" class="mt-1 text-xs text-red-600">
                    {{ e1.name }}
                  </p>
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Acronyme</label
                  >
                  <input
                    v-model="form.acronym"
                    type="text"
                    placeholder="3S"
                    maxlength="50"
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/20"
                  />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Email officiel *</label
                  >
                  <input
                    v-model="form.email"
                    type="email"
                    placeholder="contact@ong.org"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e1.email
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p v-if="e1.email" class="mt-1 text-xs text-red-600">
                    {{ e1.email }}
                  </p>
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Téléphone *</label
                  >
                  <input
                    v-model="form.phone"
                    type="text"
                    placeholder="77 000 00 00"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e1.phone
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p v-if="e1.phone" class="mt-1 text-xs text-red-600">
                    {{ e1.phone }}
                  </p>
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Pays *</label
                  >
                  <input
                    v-model="form.country"
                    type="text"
                    placeholder="Sénégal"
                    maxlength="100"
                    required
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/20"
                  />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Région *</label
                  >
                  <input
                    v-model="form.region"
                    type="text"
                    placeholder="Dakar"
                    maxlength="100"
                    required
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/20"
                  />
                </div>
                <div class="sm:col-span-2">
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Adresse *</label
                  >
                  <input
                    v-model="form.address"
                    type="text"
                    placeholder="Point E, Dakar"
                    maxlength="255"
                    required
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/20"
                  />
                </div>
                <div class="sm:col-span-2">
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Domaine d'intervention *</label
                  >
                  <input
                    v-model="form.intervention_domain"
                    type="text"
                    placeholder="Education, santé, solidarité..."
                    maxlength="150"
                    required
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/20"
                  />
                </div>
              </div>
              <div class="mt-6 flex justify-end">
                <button
                  type="button"
                  @click="nextStep"
                  class="h-11 rounded-lg bg-bleu-nuit px-6 text-sm font-semibold text-white hover:bg-[#0a2540]"
                >
                  Suivant
                </button>
              </div>
            </div>

            <div v-if="currentStep === 2">
              <h2 class="text-xl font-bold text-bleu-nuit mb-1">
                Documents de vérification
              </h2>
              <p class="text-sm text-slate-600 mb-6">
                Ces documents permettront au Super Admin de vérifier que votre
                organisation est légalement reconnue.
              </p>
              <div class="space-y-4">
                <div class="rounded-lg border border-slate-200 p-4">
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Récépissé de l'ONG (PDF) *</label
                  >
                  <input
                    type="file"
                    accept="application/pdf"
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold"
                    @change="(e) => onFileChange(e, 'receipt')"
                  />
                  <p v-if="fileErrors.receipt" class="mt-1 text-xs text-red-600">{{ fileErrors.receipt }}</p>
                  <div v-if="files.receipt" class="mt-2 text-xs text-slate-600">
                    {{ files.receipt.name }} -
                    {{ formatSize(files.receipt.size) }}
                    <button
                      type="button"
                      class="ml-2 text-red-600 underline"
                      @click="files.receipt = null"
                    >
                      Remplacer
                    </button>
                  </div>
                </div>
                <div class="rounded-lg border border-slate-200 p-4">
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >NINEA ou Registre (PDF) *</label
                  >
                  <input
                    type="file"
                    accept="application/pdf"
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold"
                    @change="(e) => onFileChange(e, 'ninea')"
                  />
                  <p v-if="fileErrors.ninea" class="mt-1 text-xs text-red-600">{{ fileErrors.ninea }}</p>
                  <div v-if="files.ninea" class="mt-2 text-xs text-slate-600">
                    {{ files.ninea.name }} - {{ formatSize(files.ninea.size) }}
                    <button
                      type="button"
                      class="ml-2 text-red-600 underline"
                      @click="files.ninea = null"
                    >
                      Remplacer
                    </button>
                  </div>
                </div>
                <div class="rounded-lg border border-slate-200 p-4">
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Statuts de l'association (PDF) *</label
                  >
                  <input
                    type="file"
                    accept="application/pdf"
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold"
                    @change="(e) => onFileChange(e, 'statutes')"
                  />
                  <p v-if="fileErrors.statutes" class="mt-1 text-xs text-red-600">{{ fileErrors.statutes }}</p>
                  <div
                    v-if="files.statutes"
                    class="mt-2 text-xs text-slate-600"
                  >
                    {{ files.statutes.name }} -
                    {{ formatSize(files.statutes.size) }}
                    <button
                      type="button"
                      class="ml-2 text-red-600 underline"
                      @click="files.statutes = null"
                    >
                      Remplacer
                    </button>
                  </div>
                </div>
              </div>
              <div class="mt-6 flex justify-between">
                <button
                  type="button"
                  @click="currentStep -= 1"
                  class="h-11 rounded-lg border border-slate-300 px-6 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Précédent
                </button>
                <button
                  type="button"
                  @click="nextStep"
                  class="h-11 rounded-lg bg-bleu-nuit px-6 text-sm font-semibold text-white hover:bg-[#0a2540]"
                >
                  Suivant
                </button>
              </div>
            </div>

            <div v-if="currentStep === 3">
              <h2 class="text-xl font-bold text-bleu-nuit mb-1">
                Informations du Gérant
              </h2>
              <p class="text-sm text-slate-600 mb-6">
                Ces informations serviront à créer le compte principal de l'ONG.
              </p>
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Prénom *</label
                  >
                  <input
                    v-model="form.manager_first_name"
                    type="text"
                    placeholder="Amadou"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e3.manager_first_name
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p
                    v-if="e3.manager_first_name"
                    class="mt-1 text-xs text-red-600"
                  >
                    {{ e3.manager_first_name }}
                  </p>
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Nom *</label
                  >
                  <input
                    v-model="form.manager_last_name"
                    type="text"
                    placeholder="Diallo"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e3.manager_last_name
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p
                    v-if="e3.manager_last_name"
                    class="mt-1 text-xs text-red-600"
                  >
                    {{ e3.manager_last_name }}
                  </p>
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Email du Gérant *</label
                  >
                  <input
                    v-model="form.manager_email"
                    type="email"
                    placeholder="gerant@ong.org"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e3.manager_email
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p v-if="e3.manager_email" class="mt-1 text-xs text-red-600">
                    {{ e3.manager_email }}
                  </p>
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700"
                    >Téléphone *</label
                  >
                  <input
                    v-model="form.manager_phone"
                    type="text"
                    placeholder="77 000 00 00"
                    required
                    class="w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:ring-2 transition"
                    :class="
                      e3.manager_phone
                        ? 'border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:ring-bleu-nuit/20'
                    "
                  />
                  <p v-if="e3.manager_phone" class="mt-1 text-xs text-red-600">
                    {{ e3.manager_phone }}
                  </p>
                </div>
              </div>

              <div
                class="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700"
              >
                <p class="font-semibold mb-2">Que se passe-t-il ensuite ?</p>
                <ol class="list-decimal list-inside space-y-1">
                  <li>Votre demande sera envoyée au Super Admin.</li>
                  <li>Vos documents seront vérifiés.</li>
                  <li>
                    Vous recevrez un email d'activation après approbation.
                  </li>
                  <li>
                    Votre essai gratuit de 30 jours commencera lors de votre
                    première connexion.
                  </li>
                </ol>
              </div>

              <div class="mt-6 flex justify-between">
                <button
                  type="button"
                  @click="currentStep -= 1"
                  class="h-11 rounded-lg border border-slate-300 px-6 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Précédent
                </button>
                <button
                  type="button"
                  @click="submitRegistration"
                  :disabled="loading"
                  class="h-11 rounded-lg bg-bleu-nuit px-6 text-sm font-semibold text-white hover:bg-[#0a2540] disabled:opacity-60"
                >
                  {{ loading ? "Inscription en cours..." : "Créer mon ONG" }}
                </button>
              </div>
            </div>
          </div>

          <div
            v-else
            class="mt-8 rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900"
          >
            <h3 class="text-lg font-bold">Demande envoyée avec succès</h3>
            <p class="mt-2 text-sm leading-6">
              Votre dossier est en attente de validation par le Super Admin.
              Nous vous enverrons un email dès que votre ONG sera approuvée.
            </p>
            <RouterLink
              to="/connexion"
              class="mt-5 inline-block font-bold text-emerald-800 underline"
            >
              Retour à la connexion
            </RouterLink>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import api, { getErrorMessage } from "@/services/api.js";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const currentStep = ref(1);
const steps = [
  { key: 1, label: "Informations" },
  { key: 2, label: "Documents" },
  { key: 3, label: "Gérant" },
];
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

// ── Validation ────────────────────────────────────────────────────────────────
const { errors: e1, validate: v1 } = useFormValidation(); // étape 1
const { errors: e3, validate: v3 } = useFormValidation(); // étape 3

const form = reactive({
  name: "",
  acronym: "",
  email: "",
  phone: "",
  address: "",
  region: "",
  country: "Sénégal",
  intervention_domain: "",
  manager_first_name: "",
  manager_last_name: "",
  manager_email: "",
  manager_phone: "",
});

const files = reactive({ receipt: null, ninea: null, statutes: null });
const fileErrors = reactive({ receipt: "", ninea: "", statutes: "" });

const formatSize = (bytes) => {
  if (!bytes) return "0 octet";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(2)} Mo` : `${(bytes / 1024).toFixed(2)} Ko`;
};

const onFileChange = (event, key) => {
  const file = event.target.files?.[0] || null;
  fileErrors[key] = "";
  if (!file) {
    files[key] = null;
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    fileErrors[key] = "La taille du fichier ne doit pas dépasser 5 Mo.";
  } else if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) {
    fileErrors[key] = "Le fichier doit être au format PDF.";
  }
  files[key] = fileErrors[key] ? null : file;
  if (fileErrors[key]) event.target.value = "";
};

const validateStep = () => {
  errorMessage.value = "";

  if (currentStep.value === 1) {
    const ok = v1({
      name: [rules.nomLong, form.name],
      acronym: [rules.maxLength(50), form.acronym],
      email: [rules.email, form.email],
      phone: [rules.phone, form.phone],
      country: [rules.required, form.country],
      region: [(value) => rules.required(value) || rules.maxLength(100)(value), form.region],
      address: [(value) => rules.required(value) || rules.maxLength(255)(value), form.address],
      intervention_domain: [(value) => rules.required(value) || rules.maxLength(150)(value), form.intervention_domain],
    });
    if (!ok) {
      errorMessage.value = "Veuillez corriger les champs en rouge.";
      return false;
    }
    return true;
  }

  if (currentStep.value === 2) {
    const fileWithError = Object.values(fileErrors).some(Boolean);
    if (fileWithError) return false;
    if (!files.receipt || !files.ninea || !files.statutes) {
      errorMessage.value = "Veuillez joindre les 3 documents PDF requis.";
      return false;
    }
    // Validation taille max 5 Mo par fichier
    for (const [key, file] of Object.entries(files)) {
      if (file && file.size > 5 * 1024 * 1024) {
        errorMessage.value = `Le fichier "${file.name}" dépasse la taille maximale autorisée (5 Mo).`;
        return false;
      }
      if (file && file.type !== "application/pdf") {
        errorMessage.value = `Le fichier "${file.name}" doit être au format PDF.`;
        return false;
      }
    }
    return true;
  }

  if (currentStep.value === 3) {
    const ok = v3({
      manager_first_name: [rules.nom, form.manager_first_name],
      manager_last_name: [rules.nom, form.manager_last_name],
      manager_email: [rules.email, form.manager_email],
      manager_phone: [rules.phone, form.manager_phone],
    });
    if (!ok) {
      errorMessage.value = "Veuillez corriger les champs en rouge.";
      return false;
    }
    return true;
  }
  return true;
};

const nextStep = () => {
  errorMessage.value = "";
  if (!validateStep()) return;
  if (currentStep.value < 3) currentStep.value += 1;
};

const submitRegistration = async () => {
  errorMessage.value = "";
  if (!validateStep()) return;

  loading.value = true;
  const payload = new FormData();
  Object.entries(form).forEach(([key, value]) => {
    if (value !== null && value !== "") payload.append(key, value);
  });
  Object.entries(files).forEach(([key, file]) => {
    if (file) payload.append(`document_${key}`, file);
  });

  try {
    await api.post("/api/organizations/register/", payload, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    successMessage.value = "Demande envoyée avec succès.";
  } catch (error) {
    errorMessage.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
};
</script>
