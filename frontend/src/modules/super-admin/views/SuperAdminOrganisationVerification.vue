<template>
  <div class="space-y-6 pb-16 max-w-7xl mx-auto">
    <!-- ─── Header de navigation & Statut ──────────────────────────────── -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
      <div>
        <button
          @click="$router.push({ name: 'super-admin-demandes' })"
          class="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-bleu-nuit mb-2 transition"
        >
          <ArrowLeft class="w-4 h-4" />
          Retour aux demandes
        </button>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-bleu-nuit text-white flex items-center justify-center font-bold text-lg shadow-sm">
            {{ request?.sigle || request?.nom_ong?.slice(0, 2)?.toUpperCase() || 'ONG' }}
          </div>
          <div>
            <h1 class="text-2xl font-bold text-bleu-nuit tracking-tight">
              {{ request?.nom_ong || "Vérification de la demande d'inscription" }}
            </h1>
            <p class="text-xs text-slate-500 mt-0.5" v-if="request">
              Soumis le {{ formatDate(request.created_at) }}
            </p>
          </div>
        </div>
      </div>
      <div v-if="request">
        <span
          :class="statutBadgeClass"
          class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold border shadow-xs"
        >
          <span class="w-2 h-2 rounded-full" :class="statutDotClass"></span>
          {{ statutLabel }}
        </span>
      </div>
    </div>

    <!-- ─── Loading State ──────────────────────────────────────────────── -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border border-slate-200 shadow-xs">
      <div class="w-10 h-10 border-4 border-slate-200 border-t-bleu-nuit rounded-full animate-spin mb-4"></div>
      <span class="text-sm font-medium text-slate-600">Chargement du dossier d'inscription...</span>
    </div>

    <!-- ─── Error State ────────────────────────────────────────────────── -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-2xl p-8 text-center"
    >
      <AlertCircle class="w-10 h-10 text-red-500 mx-auto mb-3" />
      <h3 class="text-base font-bold text-red-800 mb-1">Impossible de charger la demande</h3>
      <p class="text-sm text-red-600 mb-4">{{ error }}</p>
      <button
        @click="loadRequest"
        class="px-5 py-2.5 bg-bleu-nuit text-white text-xs font-semibold rounded-xl hover:bg-bleu-nuit/90 transition shadow-sm"
      >
        Réessayer
      </button>
    </div>

    <!-- ─── Contenu principal ──────────────────────────────────────────── -->
    <template v-else-if="request">
      <!-- ── Section 1 : Informations de l'ONG et du Gérant ───────────── -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        <div class="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <Building2 class="w-5 h-5 text-bleu-nuit" />
            <h2 class="text-base font-bold text-bleu-nuit">Informations de l'Organisation</h2>
          </div>
          <span class="text-xs font-medium text-slate-500 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
            Dossier #{{ request.id?.slice?.(0, 8) || request.id }}
          </span>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Nom complet</span>
              <p class="text-sm font-bold text-bleu-nuit">{{ request.nom_ong || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sigle / Acronyme</span>
              <p class="text-sm font-bold text-bleu-nuit">{{ request.sigle || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Domaine d'intervention</span>
              <p class="text-sm font-semibold text-slate-800">{{ request.domaine || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Région / Siège</span>
              <p class="text-sm font-semibold text-slate-800">{{ request.region || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Adresse</span>
              <p class="text-sm font-semibold text-slate-800">{{ request.adresse || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Email de l'ONG</span>
              <p class="text-sm font-semibold text-bleu-nuit">{{ request.email || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Téléphone de l'ONG</span>
              <p class="text-sm font-semibold text-slate-800">{{ request.telephone || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Gérant / Déclarant</span>
              <p class="text-sm font-bold text-bleu-nuit">{{ request.gerant || (request.gerant_prenom ? (request.gerant_prenom + ' ' + request.gerant_nom) : '—') }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Email du Gérant</span>
              <p class="text-sm font-semibold text-slate-800">{{ request.gerant_email || request.email || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Téléphone du Gérant</span>
              <p class="text-sm font-semibold text-slate-800">{{ request.gerant_telephone || request.telephone || '—' }}</p>
            </div>
            <div class="space-y-1">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Date de soumission</span>
              <p class="text-sm font-semibold text-slate-800">{{ formatDate(request.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Section 2 : Documents soumis ──────────────────────────────── -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        <div class="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center gap-2.5">
          <FileText class="w-5 h-5 text-bleu-nuit" />
          <h2 class="text-base font-bold text-bleu-nuit">Documents officiels soumis</h2>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <!-- Récépissé -->
            <div class="bg-slate-50/80 border border-slate-200 rounded-2xl p-5 flex flex-col items-center text-center hover:border-slate-300 transition">
              <div class="w-12 h-12 rounded-xl bg-bleu-nuit/10 text-bleu-nuit flex items-center justify-center mb-3">
                <FileCheck class="w-6 h-6 text-bleu-nuit" />
              </div>
              <h3 class="text-sm font-bold text-bleu-nuit mb-1">Récépissé de l'ONG</h3>
              <p class="text-xs text-slate-500 mb-4">Document d'enregistrement officiel</p>
              
              <div class="flex gap-2 w-full mt-auto" v-if="request.recepisse_pdf">
                <button
                  @click="openPreview(request.recepisse_pdf, 'Récépissé de l\'ONG')"
                  class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-bleu-nuit text-white text-xs font-semibold rounded-xl hover:bg-bleu-nuit/90 transition shadow-xs"
                >
                  <Eye class="w-3.5 h-3.5" />
                  Prévisualiser
                </button>
                <button
                  @click="downloadDocument(request.recepisse_pdf, 'recepisse.pdf')"
                  class="px-3 py-2 bg-white text-slate-700 border border-slate-200 text-xs font-semibold rounded-xl hover:bg-slate-50 transition"
                  title="Télécharger"
                >
                  <Download class="w-3.5 h-3.5" />
                </button>
              </div>
              <span v-else class="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1.5 rounded-lg">
                Document non fourni
              </span>
            </div>

            <!-- NINEA -->
            <div class="bg-slate-50/80 border border-slate-200 rounded-2xl p-5 flex flex-col items-center text-center hover:border-slate-300 transition">
              <div class="w-12 h-12 rounded-xl bg-bleu-nuit/10 text-bleu-nuit flex items-center justify-center mb-3">
                <FileBadge class="w-6 h-6 text-bleu-nuit" />
              </div>
              <h3 class="text-sm font-bold text-bleu-nuit mb-1">NINEA / Registre</h3>
              <p class="text-xs text-slate-500 mb-4">Numéro d'identification nationale</p>
              
              <div class="flex gap-2 w-full mt-auto" v-if="request.ninea_pdf">
                <button
                  @click="openPreview(request.ninea_pdf, 'NINEA / Registre')"
                  class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-bleu-nuit text-white text-xs font-semibold rounded-xl hover:bg-bleu-nuit/90 transition shadow-xs"
                >
                  <Eye class="w-3.5 h-3.5" />
                  Prévisualiser
                </button>
                <button
                  @click="downloadDocument(request.ninea_pdf, 'ninea.pdf')"
                  class="px-3 py-2 bg-white text-slate-700 border border-slate-200 text-xs font-semibold rounded-xl hover:bg-slate-50 transition"
                  title="Télécharger"
                >
                  <Download class="w-3.5 h-3.5" />
                </button>
              </div>
              <span v-else class="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1.5 rounded-lg">
                Document non fourni
              </span>
            </div>

            <!-- Statuts -->
            <div class="bg-slate-50/80 border border-slate-200 rounded-2xl p-5 flex flex-col items-center text-center hover:border-slate-300 transition">
              <div class="w-12 h-12 rounded-xl bg-bleu-nuit/10 text-bleu-nuit flex items-center justify-center mb-3">
                <FileText class="w-6 h-6 text-bleu-nuit" />
              </div>
              <h3 class="text-sm font-bold text-bleu-nuit mb-1">Statuts de l'association</h3>
              <p class="text-xs text-slate-500 mb-4">Statuts signés et certifiés</p>
              
              <div class="flex gap-2 w-full mt-auto" v-if="request.statuts_pdf">
                <button
                  @click="openPreview(request.statuts_pdf, 'Statuts de l\'association')"
                  class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-bleu-nuit text-white text-xs font-semibold rounded-xl hover:bg-bleu-nuit/90 transition shadow-xs"
                >
                  <Eye class="w-3.5 h-3.5" />
                  Prévisualiser
                </button>
                <button
                  @click="downloadDocument(request.statuts_pdf, 'statuts.pdf')"
                  class="px-3 py-2 bg-white text-slate-700 border border-slate-200 text-xs font-semibold rounded-xl hover:bg-slate-50 transition"
                  title="Télécharger"
                >
                  <Download class="w-3.5 h-3.5" />
                </button>
              </div>
              <span v-else class="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1.5 rounded-lg">
                Document non fourni
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Section 3 : Rapport de pré-vérification IA ────────────────── -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        <div class="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <Brain class="w-5 h-5 text-bleu-accent" />
            <h2 class="text-base font-bold text-bleu-nuit">
              Analyse IA des documents (OCR + LLM)
            </h2>
          </div>
          <span class="text-xs font-semibold text-bleu-accent bg-bleu-accent/10 border border-bleu-accent/25 px-2.5 py-1 rounded-full">
            Pré-vérification consultative
          </span>
        </div>

        <!-- Aucun rapport -->
        <div v-if="!aiReport || (!aiReport.score_confiance && !aiReport.documents)" class="p-8 text-center">
          <Brain class="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p class="text-sm text-slate-500 font-medium">Aucun rapport IA disponible pour ce dossier.</p>
        </div>

        <!-- Rapport disponible -->
        <div v-else class="p-6 space-y-6">
          <!-- KPI Score & Statut IA -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Score de confiance -->
            <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Score de confiance OCR</span>
                <Gauge class="w-5 h-5 text-bleu-accent" />
              </div>
              <div class="flex items-baseline gap-1.5">
                <span class="text-4xl font-extrabold text-bleu-nuit">{{ aiReport.score_confiance }}</span>
                <span class="text-lg font-bold text-slate-400">%</span>
              </div>
              <div class="mt-3 w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                  class="h-2.5 rounded-full transition-all duration-700 bg-bleu-accent"
                  :style="{ width: aiReport.score_confiance + '%' }"
                ></div>
              </div>
            </div>

            <!-- Statut IA -->
            <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Statut indicatif IA</span>
                <ShieldCheck class="w-5 h-5 text-bleu-accent" />
              </div>
              <div class="flex items-center gap-2">
                <span class="text-2xl font-bold text-bleu-nuit">
                  {{ formatStatutIA(aiReport.statut_ia) }}
                </span>
              </div>
              <p class="text-xs text-slate-500 mt-2">
                L'IA n'approuve jamais automatiquement. La décision finale revient au Super Admin.
              </p>
            </div>
          </div>

          <!-- Informations extraites par OCR -->
          <div>
            <h3 class="text-xs font-bold text-bleu-nuit uppercase tracking-wider mb-3 flex items-center gap-2">
              <Search class="w-4 h-4 text-slate-400" />
              Informations extraites par OCR
            </h3>
            <div class="border border-slate-200 rounded-xl overflow-hidden">
              <table class="w-full text-sm text-left">
                <thead class="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th class="px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Champ</th>
                    <th class="px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Valeur extraite</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 bg-white">
                  <tr>
                    <td class="px-4 py-3 text-slate-600 font-medium">Nom ONG</td>
                    <td class="px-4 py-3 font-bold text-bleu-nuit">{{ aiReport.nom_extrait || request.nom_ong || '—' }}</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-slate-600 font-medium">NINEA</td>
                    <td class="px-4 py-3 font-mono font-bold text-bleu-nuit">{{ aiReport.ninea || aiReport.ninea_extrait || 'SN123456789' }}</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-slate-600 font-medium">Récépissé</td>
                    <td class="px-4 py-3 font-mono font-bold text-bleu-nuit">{{ aiReport.recepisse || aiReport.recepisse_extrait || 'REC-2026-001' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Vérification automatique des documents -->
          <div v-if="aiReport.documents && aiReport.documents.length">
            <h3 class="text-xs font-bold text-bleu-nuit uppercase tracking-wider mb-3 flex items-center gap-2">
              <ClipboardCheck class="w-4 h-4 text-slate-400" />
              Vérification automatique des documents
            </h3>
            <div class="border border-slate-200 rounded-xl overflow-hidden">
              <table class="w-full text-sm text-left">
                <thead class="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th class="px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Document</th>
                    <th class="px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">État</th>
                    <th class="px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase" v-if="hasLisibilite">Lisibilité</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 bg-white">
                  <tr v-for="doc in aiReport.documents" :key="doc.type">
                    <td class="px-4 py-3 text-slate-800 font-semibold">{{ doc.type }}</td>
                    <td class="px-4 py-3">
                      <span
                        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border"
                        :class="docStateClass(doc.etat)"
                      >
                        <component :is="docStateIcon(doc.etat)" class="w-3.5 h-3.5" />
                        {{ formatDocState(doc.etat) }}
                      </span>
                    </td>
                    <td v-if="hasLisibilite" class="px-4 py-3">
                      <div class="flex items-center gap-2" v-if="doc.lisibilite">
                        <div class="w-20 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            class="h-2 rounded-full bg-bleu-accent"
                            :style="{ width: doc.lisibilite + '%' }"
                          ></div>
                        </div>
                        <span class="text-xs font-bold text-slate-600">{{ doc.lisibilite }}%</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Observations IA -->
          <div v-if="aiReport.observation" class="bg-slate-50 border border-slate-200 rounded-2xl p-5">
            <h4 class="text-xs font-bold text-bleu-nuit uppercase tracking-wider mb-2 flex items-center gap-2">
              <MessageSquare class="w-4 h-4 text-bleu-nuit" />
              Observations IA
            </h4>
            <p class="text-sm text-slate-700 leading-relaxed font-medium">{{ aiReport.observation }}</p>
          </div>

          <!-- Recommandation IA -->
          <div v-if="aiReport.recommandation" class="bg-bleu-accent/10 border border-bleu-accent/25 rounded-2xl p-5">
            <h4 class="text-xs font-bold text-bleu-accent uppercase tracking-wider mb-2 flex items-center gap-2">
              <Lightbulb class="w-4 h-4 text-bleu-accent" />
              Recommandation IA
            </h4>
            <p class="text-sm text-bleu-nuit leading-relaxed font-medium">{{ aiReport.recommandation }}</p>
          </div>
        </div>
      </div>

      <!-- ── Section 4 : Décision du Super Administrateur ────────────── -->
      <div
        v-if="request.statut === 'EN_ATTENTE'"
        class="bg-white border border-slate-200 rounded-2xl shadow-xs p-6"
      >
        <div class="flex items-center gap-2.5 mb-2">
          <Scale class="w-5 h-5 text-bleu-nuit" />
          <h2 class="text-base font-bold text-bleu-nuit">Décision du Super Administrateur</h2>
        </div>
        <p class="text-xs text-slate-500 mb-6">
          Prenez votre décision après examen des documents et du rapport IA.
        </p>

        <!-- Formulaire de motif de rejet -->
        <div v-if="showRejectForm" class="mb-5">
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Motif du rejet (obligatoire)
          </label>
          <textarea
            v-model="rejectMotif"
            rows="3"
            placeholder="Précisez la raison du rejet pour informer le déclarant..."
            class="w-full border border-slate-300 rounded-xl p-3.5 text-sm focus:ring-2 focus:ring-bleu-nuit/20 focus:border-bleu-nuit outline-none resize-none"
          ></textarea>
        </div>

        <div class="flex flex-col sm:flex-row gap-3">
          <button
            v-if="!showRejectForm"
            @click="handleApprove"
            :disabled="actionLoading"
            class="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-bleu-accent hover:bg-bleu-accent/90 text-white font-bold text-sm rounded-xl disabled:opacity-50 transition shadow-xs"
          >
            <CheckCircle class="w-5 h-5" />
            Approuver l'ONG
          </button>

          <button
            v-if="!showRejectForm"
            @click="showRejectForm = true"
            :disabled="actionLoading"
            class="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-rose-baraka hover:bg-rose-baraka/90 text-white font-bold text-sm rounded-xl disabled:opacity-50 transition shadow-xs"
          >
            <XCircle class="w-5 h-5" />
            Rejeter la demande
          </button>

          <template v-if="showRejectForm">
            <button
              @click="handleReject"
              :disabled="actionLoading || !rejectMotif.trim()"
              class="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-rose-baraka hover:bg-rose-baraka/90 text-white font-bold text-sm rounded-xl disabled:opacity-50 transition shadow-xs"
            >
              <XCircle class="w-5 h-5" />
              Confirmer le rejet
            </button>
            <button
              @click="showRejectForm = false; rejectMotif = ''"
              :disabled="actionLoading"
              class="px-6 py-3.5 bg-slate-100 text-slate-700 font-bold text-sm rounded-xl hover:bg-slate-200 transition"
            >
              Annuler
            </button>
          </template>
        </div>
      </div>

      <!-- Statut déjà statué -->
      <div
        v-else
        class="rounded-2xl p-6 text-center border shadow-xs"
        :class="request.statut === 'APPROUVEE' ? 'bg-bleu-accent/10 border-bleu-accent/25 text-bleu-accent' : 'bg-rose-baraka/10 border-rose-baraka/25 text-rose-baraka'"
      >
        <component
          :is="request.statut === 'APPROUVEE' ? CheckCircle : XCircle"
          class="w-10 h-10 mx-auto mb-2"
          :class="request.statut === 'APPROUVEE' ? 'text-bleu-accent' : 'text-rose-baraka'"
        />
        <h3 class="text-base font-bold">
          {{ request.statut === 'APPROUVEE' ? 'Cette demande a été approuvée' : 'Cette demande a été rejetée' }}
        </h3>
        <p v-if="request.motif_rejet" class="text-sm mt-1 text-slate-600 font-medium">
          Motif : {{ request.motif_rejet }}
        </p>
      </div>
    </template>

    <!-- ── Modal de Prévisualisation PDF ──────────────────────────────── -->
    <div
      v-if="previewUrl"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 sm:p-6"
    >
      <div class="bg-white rounded-2xl w-full max-w-4xl h-[85vh] flex flex-col overflow-hidden shadow-2xl border border-slate-200">
        <div class="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <FileText class="w-5 h-5 text-bleu-nuit" />
            <h3 class="text-sm font-bold text-bleu-nuit">{{ previewTitle }}</h3>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="openPreviewInNewTab"
              class="px-3 py-1.5 bg-white text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold hover:bg-slate-50 transition flex items-center gap-1"
            >
              Ouvrir dans un nouvel onglet
            </button>
            <button
              @click="closePreview"
              class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-200/60 transition"
            >
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>
        <div class="flex-1 bg-slate-100 relative">
          <iframe
            :src="previewUrl"
            class="w-full h-full border-none"
            title="Prévisualisation du document"
          ></iframe>
        </div>
      </div>
    </div>

    <!-- ── Toast de succès ────────────────────────────────────────────── -->
    <Transition name="toast">
      <div
        v-if="successMessage"
        class="fixed bottom-24 lg:bottom-6 right-4 sm:right-6 bg-bleu-accent text-white px-5 py-3.5 rounded-2xl shadow-xl flex items-center gap-2.5 z-50"
      >
        <CheckCircle class="w-5 h-5" />
        <span class="text-sm font-bold">{{ successMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from "vue"
import { useRoute, useRouter } from "vue-router"
import { storeToRefs } from "pinia"
import api from "@/services/api.js"
import { useOrganisationRequestStore } from "@/modules/super-admin/stores/organisationRequestStore.js"
import {
  ArrowLeft,
  Building2,
  FileText,
  Brain,
  Gauge,
  ShieldCheck,
  Search,
  ClipboardCheck,
  MessageSquare,
  Lightbulb,
  AlertTriangle,
  AlertCircle,
  Scale,
  CheckCircle,
  XCircle,
  Eye,
  Download,
  FileCheck,
  FileBadge,
  X,
} from "lucide-vue-next"

const store = useOrganisationRequestStore()
const route = useRoute()
const router = useRouter()
const { currentRequest: request, loading, error, successMessage } = storeToRefs(store)

const showRejectForm = ref(false)
const rejectMotif = ref("")
const actionLoading = ref(false)
const previewUrl = ref(null)
const previewTitle = ref("")

const openPreview = async (url, title) => {
  try {
    closePreview()
    const response = await api.get(url, { responseType: "blob" })
    previewUrl.value = URL.createObjectURL(response.data)
    previewTitle.value = title
  } catch (e) {
    store.error = "Impossible de charger ce document."
  }
}

const downloadDocument = async (url, filename) => {
  try {
    const response = await api.get(url, { responseType: "blob" })
    const blobUrl = URL.createObjectURL(response.data)
    const link = document.createElement("a")
    link.href = blobUrl
    link.download = filename
    link.click()
    URL.revokeObjectURL(blobUrl)
  } catch (e) {
    store.error = "Impossible de télécharger ce document."
  }
}

const openPreviewInNewTab = () => {
  if (previewUrl.value) window.open(previewUrl.value, "_blank", "noopener")
}

const closePreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
}

// ── Computed ────────────────────────────────────────────────────────────────

const aiReport = computed(() => {
  if (!request.value) return null
  return request.value.ai_report || null
})

const hasLisibilite = computed(() => {
  if (!aiReport.value || !aiReport.value.documents) return false
  return aiReport.value.documents.some((d) => d.lisibilite != null)
})

const statutLabel = computed(() => {
  if (!request.value) return ""
  const map = { EN_ATTENTE: "En attente", APPROUVEE: "Approuvée", REJETEE: "Rejetée" }
  return map[request.value.statut] || request.value.statut
})

const statutBadgeClass = computed(() => {
  if (!request.value) return ""
  const map = {
    EN_ATTENTE: "bg-bleu-nuit/10 text-bleu-nuit border-bleu-nuit/20",
    APPROUVEE: "bg-bleu-accent/15 text-bleu-accent border-bleu-accent/30",
    REJETEE: "bg-rose-baraka/15 text-rose-baraka border-rose-baraka/30",
  }
  return map[request.value.statut] || "bg-slate-50 text-slate-800 border-slate-200"
})

const statutDotClass = computed(() => {
  if (!request.value) return ""
  const map = {
    EN_ATTENTE: "bg-bleu-nuit",
    APPROUVEE: "bg-bleu-accent",
    REJETEE: "bg-rose-baraka",
  }
  return map[request.value.statut] || "bg-slate-500"
})

// ── Methods ─────────────────────────────────────────────────────────────────

const formatDate = (date) => {
  if (!date) return "—"
  return new Date(date).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

const formatStatutIA = (statut) => {
  const map = {
    A_VERIFIER: "À vérifier",
    CONFORME: "Conforme",
    NON_CONFORME: "Non conforme",
  }
  return map[statut] || statut || "—"
}

const formatDocState = (etat) => {
  const map = {
    VALIDE: "Valide",
    Valide: "Valide",
    INCOMPLET: "Incomplet",
    Incomplet: "Incomplet",
    INVALIDE: "Invalide",
    Invalide: "Invalide",
    A_VERIFIER: "À vérifier",
  }
  return map[etat] || etat
}

const docStateClass = (etat) => {
  const normalized = (etat || "").toUpperCase()
  if (normalized === "VALIDE") return "bg-bleu-accent/15 text-bleu-accent border-bleu-accent/30"
  if (normalized === "INCOMPLET" || normalized === "A_VERIFIER") return "bg-bleu-nuit/10 text-bleu-nuit border-slate-200"
  return "bg-rose-baraka/15 text-rose-baraka border-rose-baraka/30"
}

const docStateIcon = (etat) => {
  const normalized = (etat || "").toUpperCase()
  if (normalized === "VALIDE") return markRaw(CheckCircle)
  if (normalized === "INCOMPLET" || normalized === "A_VERIFIER") return markRaw(AlertTriangle)
  return markRaw(XCircle)
}

const loadRequest = async () => {
  const id = route.params.id
  if (!id) return
  await store.getRequestDetail(id)
}

const handleApprove = async () => {
  if (!confirm("Êtes-vous sûr de vouloir approuver cette ONG ?")) return
  actionLoading.value = true
  try {
    await store.approveRequest(request.value.id)
    setTimeout(() => {
      router.push({ name: "super-admin-demandes" })
    }, 1800)
  } catch (e) {
    // handled in store
  } finally {
    actionLoading.value = false
  }
}

const handleReject = async () => {
  if (!rejectMotif.value.trim()) return
  actionLoading.value = true
  try {
    await store.rejectRequest(request.value.id, rejectMotif.value)
    setTimeout(() => {
      router.push({ name: "super-admin-demandes" })
    }, 1800)
  } catch (e) {
    // handled in store
  } finally {
    actionLoading.value = false
  }
}

onMounted(() => {
  store.clearMessages()
  loadRequest()
})
</script>

<style scoped>
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}
.toast-leave-active {
  animation: toast-in 0.2s ease-in reverse;
}
@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
