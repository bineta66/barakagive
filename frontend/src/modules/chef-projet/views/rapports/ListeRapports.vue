<template>
  <div class="min-h-screen bg-slate-50 p-6 space-y-6">

    <!-- ══════════════════════════════════════════════════════
         EN-TÊTE
    ═══════════════════════════════════════════════════════ -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Rapports</h1>
        <p class="text-xs text-slate-500 mt-1">
          Tableau de bord analytique
          <span v-if="derniereMaj" class="ml-2 text-slate-400">
            — Mis à jour {{ formatDate(derniereMaj) }}
          </span>
        </p>
      </div>

      <div class="flex gap-2">
        <button
          id="btn-export-pdf"
          @click="exporterPDF"
          :disabled="exportLoading"
          class="flex items-center gap-2 px-4 py-2 bg-bleu-nuit text-white text-sm font-medium rounded-lg
                 hover:bg-opacity-90 active:scale-95 transition-all disabled:opacity-50"
        >
          <FileText :size="16" />
          {{ exportLoading === 'pdf' ? 'Génération…' : 'Générer PDF' }}
        </button>
        <button
          id="btn-export-excel"
          @click="exporterExcel"
          :disabled="exportLoading"
          class="flex items-center gap-2 px-4 py-2 bg-or text-white text-sm font-medium rounded-lg
                 hover:bg-opacity-90 active:scale-95 transition-all disabled:opacity-50"
        >
          <Table2 :size="16" />
          {{ exportLoading === 'excel' ? 'Export…' : 'Exporter Excel' }}
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
         FILTRES
    ═══════════════════════════════════════════════════════ -->
    <div class="bg-white rounded-xl border border-slate-200/60 shadow-xs p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
      <!-- Projet -->
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">Projet</label>
        <select
          v-model="filtres.project_id"
          id="filtre-projet"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          @change="chargerTout"
        >
          <option value="">Tous les projets</option>
          <option v-for="p in filterOptions.projets" :key="p.id" :value="p.id">
            {{ p.code }} — {{ p.nom }}
          </option>
        </select>
      </div>

      <!-- Campagne -->
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">Campagne</label>
        <select
          v-model="filtres.campaign_id"
          id="filtre-campagne"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          @change="chargerTout"
        >
          <option value="">Toutes les campagnes</option>
          <option v-for="c in filterOptions.campagnes" :key="c.id" :value="c.id">
            {{ c.code }} — {{ c.nom }}
          </option>
        </select>
      </div>

      <!-- Région -->
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">Région</label>
        <select
          v-model="filtres.region"
          id="filtre-region"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          @change="chargerTout"
        >
          <option value="">Toutes les régions</option>
          <option v-for="r in filterOptions.regions" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>

      <!-- Début -->
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">Période début</label>
        <input
          v-model="filtres.date_debut"
          type="date"
          id="filtre-date-debut"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          @change="chargerTout"
        />
      </div>

      <!-- Fin -->
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">Période fin</label>
        <input
          v-model="filtres.date_fin"
          type="date"
          id="filtre-date-fin"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          @change="chargerTout"
        />
      </div>
    </div>

    <!-- Loader global -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-bleu-nuit border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <!-- ══════════════════════════════════════════════════════
           CARTES KPI
      ═══════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div
          v-for="kpi in kpis"
          :key="kpi.label"
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex flex-col gap-2"
        >
          <div class="flex items-center justify-between">
            <p class="text-xs font-bold uppercase text-slate-400 leading-tight">{{ kpi.label }}</p>
            <component :is="kpi.icon" :size="20" class="text-bleu-nuit opacity-50" />
          </div>
          <h3 class="text-2xl font-bold text-bleu-nuit">{{ kpi.valeur }}</h3>
          <p v-if="kpi.sous" class="text-xs text-slate-400">{{ kpi.sous }}</p>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           ONGLETS
      ═══════════════════════════════════════════════════════ -->
      <div class="flex gap-1 border-b border-slate-200">
        <button
          v-for="onglet in onglets"
          :key="onglet.id"
          :id="`onglet-${onglet.id}`"
          @click="ongletActif = onglet.id"
          class="px-5 py-2.5 text-sm font-medium border-b-2 transition-all"
          :class="ongletActif === onglet.id
            ? 'border-bleu-nuit text-bleu-nuit'
            : 'border-transparent text-slate-400 hover:text-slate-700'"
        >
          {{ onglet.label }}
        </button>
      </div>

      <!-- ══════════════════════════════════════════════════════
           ONGLET : APERÇU
      ═══════════════════════════════════════════════════════ -->
      <div v-if="ongletActif === 'apercu'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Bénéficiaires par genre -->
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5">
          <h3 class="text-sm font-bold text-bleu-nuit mb-4">Répartition par genre</h3>
          <div class="flex items-center gap-6">
            <!-- Donut SVG -->
            <div class="relative w-32 h-32 flex-shrink-0">
              <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="38" fill="transparent" stroke="#e2e8f0" stroke-width="18"/>
                <circle
                  v-if="genreTotal > 0"
                  cx="50" cy="50" r="38" fill="transparent"
                  stroke="#744D03" stroke-width="18"
                  :stroke-dasharray="`${genreFDash} ${genreCirc}`"
                />
                <circle
                  v-if="genreTotal > 0"
                  cx="50" cy="50" r="38" fill="transparent"
                  stroke="#021427" stroke-width="18"
                  :stroke-dasharray="`${genreMDash} ${genreCirc}`"
                  :stroke-dashoffset="`-${genreFDash}`"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-xl font-bold text-bleu-nuit">{{ genreTotal }}</span>
                <span class="text-xs text-slate-400">total</span>
              </div>
            </div>
            <!-- Légende -->
            <div class="space-y-3">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-bleu-nuit"></div>
                <div>
                  <p class="text-sm font-bold text-bleu-nuit">{{ dashboard?.beneficiaires_par_genre?.M || 0 }}</p>
                  <p class="text-xs text-slate-400">Hommes</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-or"></div>
                <div>
                  <p class="text-sm font-bold text-or">{{ dashboard?.beneficiaires_par_genre?.F || 0 }}</p>
                  <p class="text-xs text-slate-400">Femmes</p>
                </div>
              </div>
              <div v-if="dashboard?.beneficiaires_par_genre?.AUTRE" class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-slate-300"></div>
                <div>
                  <p class="text-sm font-bold text-slate-600">{{ dashboard.beneficiaires_par_genre.AUTRE }}</p>
                  <p class="text-xs text-slate-400">Autre</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Campagnes par statut -->
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5">
          <h3 class="text-sm font-bold text-bleu-nuit mb-4">Campagnes par statut</h3>
          <div class="space-y-3">
            <div
              v-for="s in dashboard?.campagnes_par_statut || []"
              :key="s.statut"
              class="flex items-center gap-3"
            >
              <div class="w-24 flex-shrink-0">
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="statutCampagneClass(s.statut)">
                  {{ statutCampagneLabel(s.statut) }}
                </span>
              </div>
              <div class="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  class="h-2 rounded-full transition-all duration-700"
                  :class="statutCampagneBarre(s.statut)"
                  :style="{ width: `${totalCampagnes ? Math.round(s.count / totalCampagnes * 100) : 0}%` }"
                ></div>
              </div>
              <span class="text-sm font-bold text-slate-700 w-6">{{ s.count }}</span>
            </div>
          </div>
        </div>

        <!-- Bénéficiaires par mois (graphe barres) -->
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5 lg:col-span-2">
          <h3 class="text-sm font-bold text-bleu-nuit mb-4">Bénéficiaires enregistrés par mois (12 derniers mois)</h3>
          <div v-if="benParMois.length === 0" class="text-center text-slate-400 text-sm py-8">
            Aucune donnée disponible
          </div>
          <div v-else class="flex items-end gap-1.5 h-40">
            <div
              v-for="item in benParMois"
              :key="item.mois"
              class="flex-1 flex flex-col items-center gap-1 group"
            >
              <span class="text-xs text-slate-500 opacity-0 group-hover:opacity-100 transition-all">{{ item.count }}</span>
              <div
                class="w-full bg-bleu-nuit rounded-t transition-all duration-700 hover:bg-or"
                :style="{ height: `${benMaxCount ? Math.max(4, Math.round(item.count / benMaxCount * 128)) : 4}px` }"
              ></div>
              <span class="text-xs text-slate-400 -rotate-45 origin-left whitespace-nowrap text-[10px]">
                {{ item.mois.slice(5) }}/{{ item.mois.slice(0,4) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           ONGLET : PROJETS
      ═══════════════════════════════════════════════════════ -->
      <div v-if="ongletActif === 'projets'" class="space-y-4">
        <div v-if="!rapportProjets.length" class="bg-white rounded-xl border border-slate-200/60 p-12 text-center text-slate-400">
          Aucun projet trouvé
        </div>
        <div
          v-for="p in rapportProjets"
          :key="p.id"
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5 flex flex-col md:flex-row gap-5"
        >
          <!-- Infos -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div>
                <p class="text-xs font-mono text-slate-400">{{ p.code }}</p>
                <h3 class="text-base font-bold text-bleu-nuit">{{ p.nom }}</h3>
                <p class="text-xs text-slate-500 mt-1">
                  {{ p.region }} · {{ formatDate(p.start_date) }} → {{ formatDate(p.end_date) }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold text-bleu-nuit">{{ p.nb_beneficiaires.toLocaleString('fr-FR') }}</p>
                <p class="text-xs text-slate-400">bénéficiaires</p>
              </div>
            </div>

            <!-- Barres -->
            <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Taux exécution budget -->
              <div>
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-slate-500">Taux d'exécution budgétaire</span>
                  <span class="font-bold text-bleu-nuit">{{ p.taux_execution }} %</span>
                </div>
                <div class="bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    class="h-2 rounded-full transition-all duration-700"
                    :class="p.taux_execution >= 80 ? 'bg-green-500' : p.taux_execution >= 50 ? 'bg-or' : 'bg-bleu-nuit'"
                    :style="{ width: `${Math.min(100, p.taux_execution)}%` }"
                  ></div>
                </div>
              </div>

              <!-- Avancement temps -->
              <div>
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-slate-500">Avancement (durée)</span>
                  <span class="font-bold text-bleu-nuit">{{ p.avancement_temps }} %</span>
                </div>
                <div class="bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    class="h-2 rounded-full bg-slate-400 transition-all duration-700"
                    :style="{ width: `${Math.min(100, p.avancement_temps)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Métriques -->
          <div class="flex flex-wrap md:flex-col gap-4 md:gap-2 md:w-44 flex-shrink-0">
            <div class="text-center">
              <p class="text-xs text-slate-400">Budget alloué</p>
              <p class="text-sm font-bold text-bleu-nuit">{{ formatMontant(p.budget_total) }} <span class="text-xs font-normal">FCFA</span></p>
            </div>
            <div class="text-center">
              <p class="text-xs text-slate-400">Dépensé</p>
              <p class="text-sm font-bold text-or">{{ formatMontant(p.total_depenses) }} <span class="text-xs font-normal">FCFA</span></p>
            </div>
            <div class="text-center">
              <p class="text-xs text-slate-400">Campagnes</p>
              <p class="text-sm font-bold text-bleu-nuit">{{ p.nb_campagnes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           ONGLET : CAMPAGNES
      ═══════════════════════════════════════════════════════ -->
      <div v-if="ongletActif === 'campagnes'">
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
              <tr>
                <th class="text-left px-4 py-3">Campagne</th>
                <th class="text-left px-4">Projet</th>
                <th class="text-center px-4">Statut</th>
                <th class="text-right px-4">Bénéficiaires</th>
                <th class="text-right px-4">Femmes</th>
                <th class="text-right px-4">Hommes</th>
                <th class="text-right px-4">Score moyen</th>
                <th class="text-right px-4">Zones</th>
                <th class="text-right px-4">Agents</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!rapportCampagnes.length">
                <td colspan="9" class="text-center py-12 text-slate-400 text-sm">Aucune campagne</td>
              </tr>
              <tr
                v-for="c in rapportCampagnes"
                :key="c.id"
                class="border-t hover:bg-slate-50 transition-colors"
              >
                <td class="px-4 py-3">
                  <p class="font-semibold text-sm text-slate-800">{{ c.nom }}</p>
                  <p class="text-xs text-slate-400 font-mono">{{ c.code }}</p>
                </td>
                <td class="px-4 text-sm text-slate-600">
                  <p>{{ c.projet_nom }}</p>
                  <p class="text-xs text-slate-400">{{ c.projet_region }}</p>
                </td>
                <td class="px-4 text-center">
                  <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="statutCampagneClass(c.statut)">
                    {{ statutCampagneLabel(c.statut) }}
                  </span>
                </td>
                <td class="px-4 text-right text-sm font-bold text-bleu-nuit">{{ c.nb_beneficiaires.toLocaleString('fr-FR') }}</td>
                <td class="px-4 text-right text-sm text-slate-600">{{ c.nb_femmes }}</td>
                <td class="px-4 text-right text-sm text-slate-600">{{ c.nb_hommes }}</td>
                <td class="px-4 text-right">
                  <span v-if="c.score_vulnerabilite_moyen !== null" class="text-sm font-bold" :class="scoreClass(c.score_vulnerabilite_moyen)">
                    {{ c.score_vulnerabilite_moyen }}
                  </span>
                  <span v-else class="text-slate-300 text-sm">—</span>
                </td>
                <td class="px-4 text-right text-sm text-slate-600">{{ c.nb_zones }}</td>
                <td class="px-4 text-right text-sm text-slate-600">{{ c.nb_agents }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           ONGLET : BÉNÉFICIAIRES
      ═══════════════════════════════════════════════════════ -->
      <div v-if="ongletActif === 'beneficiaires'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Par région -->
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5">
          <h3 class="text-sm font-bold text-bleu-nuit mb-4">Par région</h3>
          <div class="space-y-2">
            <div
              v-for="r in rapportBenef?.par_region || []"
              :key="r.region"
              class="flex items-center gap-3"
            >
              <span class="text-xs text-slate-500 w-32 truncate">{{ r.region }}</span>
              <div class="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  class="h-2 rounded-full bg-bleu-nuit transition-all duration-700"
                  :style="{ width: `${rapportBenef?.resume?.total ? Math.round(r.count / rapportBenef.resume.total * 100) : 0}%` }"
                ></div>
              </div>
              <span class="text-xs font-bold text-slate-700 w-8 text-right">{{ r.count }}</span>
            </div>
            <div v-if="!rapportBenef?.par_region?.length" class="text-center text-slate-400 text-sm py-6">Aucune donnée</div>
          </div>
        </div>

        <!-- Distribution score -->
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5">
          <h3 class="text-sm font-bold text-bleu-nuit mb-4">Distribution du score de vulnérabilité</h3>
          <div class="space-y-3">
            <div
              v-for="t in rapportBenef?.distribution_score || []"
              :key="t.label"
              class="flex items-center gap-3"
            >
              <span class="text-xs font-mono text-slate-500 w-12">{{ t.label }}</span>
              <div class="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  class="h-3 rounded-full transition-all duration-700"
                  :class="scoreBarClass(t.label)"
                  :style="{ width: `${rapportBenef?.resume?.total ? Math.round(t.count / rapportBenef.resume.total * 100) : 0}%` }"
                ></div>
              </div>
              <span class="text-xs font-bold text-slate-700 w-8 text-right">{{ t.count }}</span>
            </div>
          </div>
        </div>

        <!-- Top 10 vulnérables -->
        <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5 lg:col-span-2">
          <h3 class="text-sm font-bold text-bleu-nuit mb-4">Top 10 bénéficiaires les plus vulnérables</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
                <tr>
                  <th class="text-left px-3 py-2">#</th>
                  <th class="text-left px-3 py-2">Nom</th>
                  <th class="text-center px-3 py-2">Genre</th>
                  <th class="text-left px-3 py-2">Zone</th>
                  <th class="text-left px-3 py-2">Région</th>
                  <th class="text-left px-3 py-2">Campagne</th>
                  <th class="text-right px-3 py-2">Score</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(b, i) in rapportBenef?.top_vulnerables || []"
                  :key="b.id"
                  class="border-t hover:bg-slate-50"
                >
                  <td class="px-3 py-2 text-slate-400">{{ i + 1 }}</td>
                  <td class="px-3 py-2 font-medium text-slate-800">{{ b.nom }}</td>
                  <td class="px-3 py-2 text-center">
                    <span class="text-xs px-1.5 py-0.5 rounded" :class="b.sexe === 'F' ? 'bg-rose-100 text-rose-700' : 'bg-blue-100 text-blue-700'">
                      {{ b.sexe }}
                    </span>
                  </td>
                  <td class="px-3 py-2 text-slate-600">{{ b.zone }}</td>
                  <td class="px-3 py-2 text-slate-600">{{ b.region }}</td>
                  <td class="px-3 py-2 text-slate-500 text-xs">{{ b.campagne }}</td>
                  <td class="px-3 py-2 text-right">
                    <span class="font-bold text-red-600">{{ b.score }}</span>
                  </td>
                </tr>
                <tr v-if="!rapportBenef?.top_vulnerables?.length">
                  <td colspan="7" class="text-center py-8 text-slate-400 text-sm">Aucun bénéficiaire avec score</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           ONGLET : FINANCES
      ═══════════════════════════════════════════════════════ -->
      <div v-if="ongletActif === 'finance'" class="space-y-6">

        <!-- KPIs finance -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4">
            <p class="text-xs text-slate-400 uppercase font-semibold">Budget alloué</p>
            <p class="text-xl font-bold text-bleu-nuit mt-2">{{ formatMontant(rapportFinance?.resume?.budget_total) }}</p>
            <p class="text-xs text-slate-400">FCFA</p>
          </div>
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4">
            <p class="text-xs text-slate-400 uppercase font-semibold">Total dépensé</p>
            <p class="text-xl font-bold text-or mt-2">{{ formatMontant(rapportFinance?.resume?.total_depenses) }}</p>
            <p class="text-xs text-slate-400">FCFA</p>
          </div>
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4">
            <p class="text-xs text-slate-400 uppercase font-semibold">Restant</p>
            <p class="text-xl font-bold text-green-600 mt-2">{{ formatMontant(rapportFinance?.resume?.montant_restant) }}</p>
            <p class="text-xs text-slate-400">FCFA</p>
          </div>
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4">
            <p class="text-xs text-slate-400 uppercase font-semibold">Total dons</p>
            <p class="text-xl font-bold text-bleu-nuit mt-2">{{ formatMontant(rapportFinance?.resume?.total_dons) }}</p>
            <p class="text-xs text-slate-400">FCFA</p>
          </div>
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4">
            <p class="text-xs text-slate-400 uppercase font-semibold">Taux d'exécution</p>
            <p class="text-xl font-bold mt-2" :class="rapportFinance?.resume?.taux_execution >= 80 ? 'text-green-600' : 'text-bleu-nuit'">
              {{ rapportFinance?.resume?.taux_execution || 0 }} %
            </p>
            <div class="bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
              <div
                class="h-1.5 rounded-full bg-bleu-nuit transition-all duration-700"
                :style="{ width: `${Math.min(100, rapportFinance?.resume?.taux_execution || 0)}%` }"
              ></div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Dépenses par mois -->
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5">
            <h3 class="text-sm font-bold text-bleu-nuit mb-4">Dépenses par mois (12 derniers mois)</h3>
            <div v-if="!rapportFinance?.depenses_par_mois?.length" class="text-center text-slate-400 text-sm py-8">Aucune donnée</div>
            <div v-else class="flex items-end gap-1.5 h-36">
              <div
                v-for="item in rapportFinance.depenses_par_mois"
                :key="item.mois"
                class="flex-1 flex flex-col items-center gap-1 group"
              >
                <span class="text-[10px] text-slate-400 opacity-0 group-hover:opacity-100 transition-all whitespace-nowrap">
                  {{ formatMontant(item.montant) }}
                </span>
                <div
                  class="w-full bg-or rounded-t transition-all duration-700 hover:bg-bleu-nuit"
                  :style="{ height: `${financeMaxMontant ? Math.max(4, Math.round(item.montant / financeMaxMontant * 120)) : 4}px` }"
                ></div>
                <span class="text-[10px] text-slate-400 -rotate-45 origin-left whitespace-nowrap">
                  {{ item.mois.slice(5) }}/{{ item.mois.slice(0,4) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Top postes -->
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5">
            <h3 class="text-sm font-bold text-bleu-nuit mb-4">Top postes budgétaires dépensés</h3>
            <div class="space-y-2">
              <div
                v-for="(p, i) in rapportFinance?.top_postes || []"
                :key="p.poste"
                class="flex items-center gap-2"
              >
                <span class="text-xs font-bold text-slate-300 w-4">{{ i + 1 }}</span>
                <div class="flex-1 min-w-0">
                  <div class="flex justify-between text-xs mb-0.5">
                    <span class="text-slate-600 truncate">{{ p.poste }}</span>
                    <span class="font-bold text-bleu-nuit ml-2">{{ formatMontant(p.total) }}</span>
                  </div>
                  <div class="bg-slate-100 rounded-full h-1.5 overflow-hidden">
                    <div
                      class="h-1.5 rounded-full bg-bleu-nuit"
                      :style="{ width: `${financeTopMax ? Math.round(p.total / financeTopMax * 100) : 0}%` }"
                    ></div>
                  </div>
                </div>
              </div>
              <div v-if="!rapportFinance?.top_postes?.length" class="text-center text-slate-400 text-sm py-6">Aucune dépense</div>
            </div>
          </div>

          <!-- Dépenses par projet -->
          <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5 lg:col-span-2">
            <h3 class="text-sm font-bold text-bleu-nuit mb-4">Dépenses par projet</h3>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
                  <tr>
                    <th class="text-left px-3 py-2">Code</th>
                    <th class="text-left px-3 py-2">Projet</th>
                    <th class="text-right px-3 py-2">Total dépensé (FCFA)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="p in rapportFinance?.depenses_par_projet || []"
                    :key="p.code"
                    class="border-t hover:bg-slate-50"
                  >
                    <td class="px-3 py-2 font-mono text-xs text-slate-400">{{ p.code }}</td>
                    <td class="px-3 py-2 font-medium text-slate-800">{{ p.projet }}</td>
                    <td class="px-3 py-2 text-right font-bold text-bleu-nuit">{{ formatMontant(p.total) }}</td>
                  </tr>
                  <tr v-if="!rapportFinance?.depenses_par_projet?.length">
                    <td colspan="3" class="text-center py-8 text-slate-400">Aucune dépense</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import {
  FileText, Table2, FolderKanban, ClipboardList, Users,
  Wallet, Activity, BarChart3, AlertTriangle
} from "lucide-vue-next"
import axios from "axios"

// ─── État ─────────────────────────────────────────────────
const loading = ref(false)
const exportLoading = ref(null)
const derniereMaj = ref(null)
const ongletActif = ref("apercu")

const filtres = ref({
  project_id: "",
  campaign_id: "",
  region: "",
  date_debut: "",
  date_fin: "",
})

const filterOptions = ref({ projets: [], campagnes: [], regions: [] })
const dashboard = ref(null)
const rapportProjets = ref([])
const rapportCampagnes = ref([])
const rapportBenef = ref(null)
const rapportFinance = ref(null)

// ─── Onglets ──────────────────────────────────────────────
const onglets = [
  { id: "apercu", label: "Aperçu" },
  { id: "projets", label: "Projets" },
  { id: "campagnes", label: "Campagnes" },
  { id: "beneficiaires", label: "Bénéficiaires" },
  { id: "finance", label: "Finance" },
]

// ─── KPIs depuis dashboard ────────────────────────────────
const kpis = computed(() => {
  const r = dashboard.value?.resume
  if (!r) return []
  return [
    { label: "Projets", valeur: r.total_projets, icon: FolderKanban },
    { label: "Campagnes", valeur: r.total_campagnes, icon: ClipboardList },
    { label: "Bénéficiaires", valeur: r.total_beneficiaires.toLocaleString("fr-FR"), icon: Users },
    { label: "Budget (FCFA)", valeur: formatMontant(r.budget_total), icon: Wallet },
    { label: "Taux d'exécution", valeur: `${r.taux_execution} %`, icon: Activity },
    {
      label: "Score vulnérabilité moy.",
      valeur: r.score_vulnerabilite_moyen ?? "—",
      icon: AlertTriangle,
      sous: r.score_vulnerabilite_moyen ? "/ 100" : "Aucun score"
    },
  ]
})

// ─── Genre donut ──────────────────────────────────────────
const genreCirc = 2 * Math.PI * 38
const genreTotal = computed(() => {
  const g = dashboard.value?.beneficiaires_par_genre
  return g ? (g.M || 0) + (g.F || 0) + (g.AUTRE || 0) : 0
})
const genreFDash = computed(() => {
  if (!genreTotal.value) return 0
  return (dashboard.value.beneficiaires_par_genre.F / genreTotal.value) * genreCirc
})
const genreMDash = computed(() => {
  if (!genreTotal.value) return 0
  return (dashboard.value.beneficiaires_par_genre.M / genreTotal.value) * genreCirc
})

// ─── Bénéf par mois ───────────────────────────────────────
const benParMois = computed(() => dashboard.value?.beneficiaires_par_mois || [])
const benMaxCount = computed(() => Math.max(1, ...benParMois.value.map(b => b.count)))

// ─── Finance graphes ──────────────────────────────────────
const totalCampagnes = computed(() => {
  return (dashboard.value?.campagnes_par_statut || []).reduce((sum, s) => sum + s.count, 0)
})
const financeMaxMontant = computed(() => {
  const mois = rapportFinance.value?.depenses_par_mois || []
  return Math.max(1, ...mois.map(m => m.montant))
})
const financeTopMax = computed(() => {
  const postes = rapportFinance.value?.top_postes || []
  return Math.max(1, ...postes.map(p => p.total))
})

// ─── Helpers ──────────────────────────────────────────────
function formatMontant(val) {
  if (val === null || val === undefined) return "0"
  return Number(val).toLocaleString("fr-FR")
}

function formatDate(val) {
  if (!val) return ""
  const d = new Date(val)
  if (isNaN(d)) return val
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" })
}

function statutCampagneLabel(s) {
  const map = { EN_COURS: "En cours", PLANIFIER: "Planifiée", TERMINE: "Terminée", ANNULEE: "Annulée", BROUILLON: "Brouillon" }
  return map[s] || s
}
function statutCampagneClass(s) {
  const map = {
    EN_COURS: "bg-green-100 text-green-700",
    PLANIFIER: "bg-blue-100 text-blue-700",
    TERMINE: "bg-slate-100 text-slate-600",
    ANNULEE: "bg-red-100 text-red-700",
    BROUILLON: "bg-yellow-100 text-yellow-700",
  }
  return map[s] || "bg-slate-100 text-slate-600"
}
function statutCampagneBarre(s) {
  const map = {
    EN_COURS: "bg-green-500",
    PLANIFIER: "bg-blue-500",
    TERMINE: "bg-slate-400",
    ANNULEE: "bg-red-400",
    BROUILLON: "bg-yellow-400",
  }
  return map[s] || "bg-slate-400"
}
function scoreClass(score) {
  if (score >= 75) return "text-red-600"
  if (score >= 50) return "text-or"
  return "text-green-600"
}
function scoreBarClass(label) {
  const map = { "0–25": "bg-green-500", "26–50": "bg-yellow-400", "51–75": "bg-or", "76–100": "bg-red-500" }
  return map[label] || "bg-slate-400"
}

// ─── Params helpers ───────────────────────────────────────
function buildParams() {
  const p = {}
  if (filtres.value.project_id) p.project_id = filtres.value.project_id
  if (filtres.value.campaign_id) p.campaign_id = filtres.value.campaign_id
  if (filtres.value.region) p.region = filtres.value.region
  if (filtres.value.date_debut) p.date_debut = filtres.value.date_debut
  if (filtres.value.date_fin) p.date_fin = filtres.value.date_fin
  return p
}

// ─── Chargement ───────────────────────────────────────────
async function chargerFiltres() {
  try {
    const { data } = await axios.get("/api/reports/filters/")
    filterOptions.value = data
  } catch (e) {
    console.error("Erreur filtres", e)
  }
}

async function chargerTout() {
  loading.value = true
  const params = buildParams()
  try {
    const [dashRes, projRes, campRes, benRes, finRes] = await Promise.all([
      axios.get("/api/reports/dashboard/", { params }),
      axios.get("/api/reports/projets/", { params }),
      axios.get("/api/reports/campagnes/", { params }),
      axios.get("/api/reports/beneficiaires/", { params }),
      axios.get("/api/reports/finance/", { params }),
    ])
    dashboard.value = dashRes.data
    derniereMaj.value = dashRes.data.derniere_maj
    rapportProjets.value = projRes.data.projets || []
    rapportCampagnes.value = campRes.data.campagnes || []
    rapportBenef.value = benRes.data
    rapportFinance.value = finRes.data
  } catch (e) {
    console.error("Erreur chargement rapports", e)
  } finally {
    loading.value = false
  }
}

// ─── Exports ──────────────────────────────────────────────
async function exporterPDF() {
  exportLoading.value = "pdf"
  try {
    const params = buildParams()
    const response = await axios.get("/api/reports/export/pdf/", {
      params,
      responseType: "blob",
    })
    const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }))
    const a = document.createElement("a")
    a.href = url
    a.download = `rapport_barakagive_${new Date().toISOString().slice(0, 10)}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error("Erreur export PDF", e)
    alert("Erreur lors de la génération du PDF. Vérifiez que la bibliothèque reportlab est installée.")
  } finally {
    exportLoading.value = null
  }
}

async function exporterExcel() {
  exportLoading.value = "excel"
  try {
    const params = buildParams()
    const response = await axios.get("/api/reports/export/excel/", {
      params,
      responseType: "blob",
    })
    const mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    const url = URL.createObjectURL(new Blob([response.data], { type: mime }))
    const a = document.createElement("a")
    a.href = url
    a.download = `rapport_barakagive_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error("Erreur export Excel", e)
    alert("Erreur lors de l'export Excel. Vérifiez que la bibliothèque openpyxl est installée.")
  } finally {
    exportLoading.value = null
  }
}

// ─── Init ─────────────────────────────────────────────────
onMounted(async () => {
  await chargerFiltres()
  await chargerTout()
})
</script>
