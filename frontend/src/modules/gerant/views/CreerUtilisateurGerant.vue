<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">
          CrÃ©er un nouvel utilisateur
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Renseignez les informations personnelles, le rÃ´le et les
          autorisations de l'agent humanitaire.
        </p>
      </div>
      <BoutonSecondary to="/gerant/utilisateurs">
        <ArrowLeft :size="16" />
        Retour
      </BoutonSecondary>
    </div>

    <form @submit.prevent="submit" class="space-y-6">
      <!-- Section 1: Informations personnelles -->
      <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4  bg-slate-50 flex items-center gap-2">
          <div class="w-2 h-5 bg-or rounded"></div>
          <h2 class="text-or text-base font-semibold uppercase tracking-wide">
            1. INFORMATIONS PERSONNELLES & IDENTITÃ‰ OPÃ‰RATIONNELLE
          </h2>
          <span class="ml-auto text-xs font-bold text-gray-800">
            SECTION OBLIGATOIRE
          </span>
        </div>

        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- PrÃ©nom -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              PrÃ©nom *
            </label>
            <input
              v-model="form.prenom"
              type="text"
              placeholder="Ex: Moussa"
              class="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
            <p class="text-xs text-gray-500 mt-1">
              IdentitÃ© officielle telle qu'indiquÃ©e sur la CNI/Passeport.
            </p>
          </div>

          <!-- Nom -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Nom *
            </label>
            <input
              v-model="form.nom"
              type="text"
              placeholder="Ex: Diop"
              class="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
            <p class="text-xs text-gray-500 mt-1">
              Nom de famille de l'intervenant.
            </p>
          </div>

          <!-- Email -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Adresse e-mail professionnelle *
            </label>
            <div class="relative">
              <Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                v-model="form.email"
                type="email"
                placeholder="m.diop@ong-partenaire.org"
                class="w-full pl-10 pr-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
                required
              />
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Servira d'identifiant de connexion unique SSO.
            </p>
          </div>

          <!-- TÃ©lÃ©phone -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              TÃ©lÃ©phone / WhatsApp Terrain *
            </label>
            <div class="relative">
              <Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                v-model="form.telephone"
                type="tel"
                placeholder="+221 77 000 00 00"
                class="w-full pl-10 pr-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
                required
              />
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Format international pour alertes SMS et notifications terrain.
            </p>
          </div>

          <!-- Matricule -->
          <div class="md:col-span-2">
            <div class="flex justify-between items-center">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Matricule agent *
              </label>
              <span class="text-xs font-bold text-or">GÃ©nÃ©rÃ© auto</span>
            </div>
            <div class="relative">
              <div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">AGT-</div>
              <input
                v-model="form.matricule"
                type="text"
                readonly
                class="w-full pl-12 pr-3 py-2 bg-slate-50 border border-gray-300 rounded-lg text-gray-800 font-mono uppercase focus:outline-none"
              />
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Format normalisÃ© de l'ERP: AGT-AAAA-XXX
            </p>
          </div>

          <!-- Langue -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Langue d'interface par dÃ©faut *
            </label>
            <select
              v-model="form.langue"
              class="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            >
              <option value="fr">FranÃ§ais (Officiel)</option>
              <option value="wo">Wolof</option>
              <option value="pu">Pulaar</option>
              <option value="sn">SÃ©nÃ©galais (franÃ§ais)</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">
              Impacte les formulaires mobiles et les reÃ§us d'aide.
            </p>
          </div>
        </div>
      </div>

      <!-- Section 2: RÃ´le & Affectation -->
      <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4  bg-slate-50 flex items-center gap-2">
          <div class="w-2 h-5 bg-or rounded"></div>
          <h2 class="text-or text-base font-semibold uppercase tracking-wide">
            2. RÃ”LE & AFFECTATION STRATÃ‰GIQUE
          </h2>
        </div>

        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- RÃ´le opÃ©rationnel -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              RÃ´le opÃ©rationnel attribuÃ© *
            </label>
            <select
              v-model="form.role"
              class="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            >
              <option value="">SÃ©lectionner un rÃ´le...</option>
              <option value="Chef de projet">Chef de projet</option>
              <option value="Responsable Finance">Responsable Finance</option>
              <option value="Agent de terrain">Agent de terrain (Distribution & Collecte)</option>
            </select>
          </div>

          <!-- Statut -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Statut initial du compte *
            </label>
            <div class="flex gap-3">
              <label class="flex items-center gap-2">
                <input
                  type="radio"
                  value="Actif"
                  v-model="form.statut"
                  class="accent-sky-900"
                />
                <span class="text-sm text-gray-800">Actif ImmÃ©diat</span>
              </label>
              <label class="flex items-center gap-2">
                <input
                  type="radio"
                  value="Inactif"
                  v-model="form.statut"
                  class="accent-sky-900"
                />
                <span class="text-sm text-gray-800">En attente d'activation</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 3: Permissions -->
      <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4  bg-slate-50 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-2 h-5 bg-or rounded"></div>
            <h2 class="text-or text-base font-semibold uppercase tracking-wide">
              3. PERMISSIONS & PÃ‰RIMÃˆTRES D'ACCÃˆS SYSTÃˆME
            </h2>
          </div>
          <div class="flex items-center gap-4">
            <button
              type="button"
              @click="selectionnerTout"
              class="text-xs font-bold text-bleu-nuit hover:text-or"
            >
              Tout cocher
            </button>
            <span class="text-gray-400">|</span>
            <button
              type="button"
              @click="reinitialiser"
              class="text-xs font-bold text-bleu-nuit hover:text-or"
            >
              RÃ©initialiser
            </button>
          </div>
        </div>

        <div class="p-6 space-y-3">
          <div
            v-for="permission in permissions"
            :key="permission.id"
            class="flex items-start gap-3 p-3 border rounded-lg"
            :class="
              permission.checked
                ? 'border-sky-700 bg-slate-50'
                : 'border-gray-300'
            "
          >
            <div class="mt-0.5">
              <input
                type="checkbox"
                :value="permission.id"
                v-model="form.permissions"
                class="accent-sky-900"
              />
            </div>
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <div :class="permission.accent"></div>
                <h3
                  class="text-sm font-bold text-gray-800"
                >{{ permission.nom }}</h3>
              </div>
              <p class="text-xs text-gray-600 mt-0.5">
                {{ permission.description }}
              </p>
            </div>
          </div>
        </div>

        <!-- SÃ©curitÃ© -->
        <div class="px-6 py-3 bg-slate-50 border-t border-slate-200">
          <div class="flex items-start gap-2">
            <Shield :size="14" class="text-gray-600 mt-0.5 flex-shrink-0" />
            <p class="text-xs text-gray-600">
              <strong class="uppercase">RÃˆGLE DE SÃ‰CURITÃ‰ HCR / RGPD :</strong>
              Toute modification des droits sensibles (Finances & Exports)
              gÃ©nÃ¨re une trace chiffrÃ©e immuable dans le registre de
              supervision.
            </p>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
       <div class="flex justify-end gap-3 pt-4">
         <BoutonSecondary @click="annuler">
           Annuler
         </BoutonSecondary>
         <button
           type="submit"
           class="h-10 px-5 bg-bleu-nuit rounded-lg flex items-center justify-center gap-2 text-white text-sm font-semibold"
         >
          <Send :size="16" />
          CrÃ©er et envoyer l'invitation
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import { ArrowLeft, Mail, Phone, Shield, Send } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"

const router = useRouter()

const form = ref({
  prenom: "",
  nom: "",
  email: "",
  telephone: "",
  matricule: "AGT-2026-" + String(Math.floor(Math.random() * 999) + 1).padStart(3, "0"),
  langue: "fr",
  role: "",
  statut: "Actif",
  permissions: [],
})

const permissions = ref([
  { id: "projets", nom: "Gestion des projets", accent: "w-3.5 h-2.5 bg-bleu-nuit rounded", description: "CrÃ©ation d'interventions, allocation de jalons et modification des budgets allouÃ©s." },
  { id: "beneficiaires", nom: "Saisie bÃ©nÃ©ficiaires terrain", accent: "w-3.5 h-2.5 bg-or rounded", description: "EnrÃ´lement biomÃ©trique/QR code, validation des rations et collecte mobile hors-ligne." },
  { id: "finances", nom: "AccÃ¨s finances et budgets", accent: "w-3.5 h-2.5 bg-bleu-nuit rounded", description: "Consultation des dÃ©caissements, rapprochements bancaires et factures bailleurs." },
  { id: "rapports", nom: "GÃ©nÃ©ration des rapports IA", accent: "w-3.5 h-2.5 bg-bleu-nuit rounded", description: "SynthÃ¨se automatisÃ©e d'impact, prÃ©diction des besoins alimentaires par LLM BarakaBot." },
  { id: "exports", nom: "Exportation des donnÃ©es", accent: "w-3 h-2.5 bg-bleu-nuit rounded", description: "Extraction des registres bruts (CSV, XLSX, Shapefiles SIG) sous journal d'audit strict." },
])

const selectionnerTout = () => {
  form.value.permissions = permissions.value.map((p) => p.id)
}

const reinitialiser = () => {
  form.value.permissions = []
}

const annuler = () => {
  router.push("/gerant/utilisateurs")
}

const submit = () => {
  console.log("Nouvel utilisateur:", form.value)
  router.push("/gerant/utilisateurs")
}
</script>





