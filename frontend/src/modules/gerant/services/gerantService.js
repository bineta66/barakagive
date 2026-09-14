import { ref } from "vue"

export const projetsGerantMock = ref([
  {
    id: 1,
    code: "PRJ-2025-001",
    nom: "Distribution alimentaire hivernage",
    chefProjet: "Awa Diop",
    responsableFinance: "Mamadou Sow",
    budget: 12500000,
    statut: "En cours",
    dateDebut: "2025-01-15",
    dateFin: "2025-11-30",
    region: "Kaolack",
    zone: "Centre",
  },
  {
    id: 2,
    code: "PRJ-2025-072",
    nom: "Accès Eau Potable & Forages Solaires",
    chefProjet: "Fatou Ndiaye",
    responsableFinance: "Mamadou Sow",
    budget: 8500000,
    statut: "Planifié",
    dateDebut: "2025-02-01",
    dateFin: "2025-12-31",
    region: "Thiès",
    zone: "Tout",
  },
  {
    id: 3,
    code: "PRJ-2025-104",
    nom: "Cliniques Mobiles & Soins Pédiatriques",
    chefProjet: "Ousmane Diallo",
    responsableFinance: "Aminata Cissé",
    budget: 9200000,
    statut: "En cours",
    dateDebut: "2025-07-01",
    dateFin: "2026-06-30",
    region: "Dakar",
    zone: "Pikine Est",
  },
  {
    id: 4,
    code: "PRJ-2025-032",
    nom: "Secours Alimentaire & Nutrition d'Urgence",
    chefProjet: "Ibrahima Sall",
    responsableFinance: "Aminata Cissé",
    budget: 4500000,
    statut: "Terminé",
    dateDebut: "2025-03-10",
    dateFin: "2025-08-15",
    region: "Dakar",
    zone: "Mermoz",
  },
  {
    id: 5,
    code: "PRJ-2024-098",
    nom: "Réhabilitation d'Infrastructures Scolaires",
    chefProjet: "Marième Ba",
    responsableFinance: "Mamadou Sow",
    budget: 7500000,
    statut: "En cours",
    dateDebut: "2024-10-01",
    dateFin: "2025-09-30",
    region: "Matam",
    zone: "Matam Ville",
  },
])

export const chefsProjetMock = ref([
  "Awa Diop",
  "Fatou Ndiaye",
  "Ousmane Diallo",
  "Ibrahima Sall",
  "Marième Ba",
])

export const responsablesFinanceMock = ref([
  "Mamadou Sow",
  "Aminata Cissé",
])

export const utilisateursMock = ref([
  {
    id: 1,
    nom: "Awa Diop",
    email: "awa.diop@barakagive.org",
    role: "Chef de projet",
    projet: "Distribution alimentaire hivernage",
    statut: "Actif",
    dateCreation: "2025-01-01",
  },
  {
    id: 2,
    nom: "Mamadou Sow",
    email: "mamadou.sow@barakagive.org",
    role: "Responsable Finance",
    projet: "3 projets",
    statut: "Actif",
    dateCreation: "2025-01-01",
  },
  {
    id: 3,
    nom: "Fatou Ndiaye",
    email: "fatou.ndiaye@barakagive.org",
    role: "Chef de projet",
    projet: "Accès Eau Potable",
    statut: "Actif",
    dateCreation: "2025-01-01",
  },
  {
    id: 4,
    nom: "Aminata Cissé",
    email: "aminata.cisse@barakagive.org",
    role: "Responsable Finance",
    projet: "2 projets",
    statut: "Actif",
    dateCreation: "2025-01-01",
  },
  {
    id: 5,
    nom: "Ousmane Diallo",
    email: "ousmane.diallo@barakagive.org",
    role: "Chef de projet",
    projet: "Cliniques Mobiles",
    statut: "Inactif",
    dateCreation: "2024-08-01",
  },
  {
    id: 6,
    nom: "Marième Ba",
    email: "marieme.ba@barakagive.org",
    role: "Chef de projet",
    projet: "Réhabilitation Scolaires",
    statut: "Actif",
    dateCreation: "2025-02-01",
  },
])

export const utilisateursStatistiquesMock = {
  totalUtilisateurs: 6,
  chefsProjet: 4,
  responsablesFinance: 2,
  utilisateursActifs: 5,
}

export const bailleursGerantMock = [
  {
    id: 1,
    nom: "DG ECHO",
    contact: "contact@echo-humanitarian.eu",
    type: "International",
    projets: 6,
    finance: "4 500 000 €",
    statut: "Reçu",
  },
  {
    id: 2,
    nom: "USAID / BHA",
    contact: "dha-desk@usaid.gov",
    type: "International",
    projets: 4,
    finance: "3 200 000 €",
    statut: "Reçu",
  },
  {
    id: 3,
    nom: "AFD",
    contact: "afd-missions@afd.fr",
    type: "National",
    projets: 3,
    finance: "2 100 000 €",
    statut: "En attente",
  },
  {
    id: 4,
    nom: "CERF",
    contact: "cerf-grants@unocha.org",
    type: "International",
    projets: 5,
    finance: "3 100 000 €",
    statut: "Reçu",
  },
  {
    id: 5,
    nom: "Union Européenne",
    contact: "humanitarian@eeas.europa.eu",
    type: "International",
    projets: 2,
    finance: "1 800 000 €",
    statut: "Reçu",
  },
]

export const partenairesGerantMock = [
  {
    id: 1,
    nom: "Croissant-Rouge Sahélien",
    domaine: "Secours d'Urgence & Santé",
    zone: "Sahel & Diffa",
    projet: "Distribution alimentaire",
    statut: "ACTIF",
  },
  {
    id: 2,
    nom: "Médecins Sans Frontières Local",
    domaine: "Cliniques Mobiles & Pédiatrie",
    zone: "Lac Tchad & Bol",
    projet: "Cliniques Mobiles",
    statut: "ACTIF",
  },
  {
    id: 3,
    nom: "Solidarités Eau & Vie",
    domaine: "Forages Solaires & Assainissement",
    zone: "Tillabéri Ouest",
    projet: "Accès Eau Potable",
    statut: "ACTIF",
  },
  {
    id: 4,
    nom: "Action contre la Faim",
    domaine: "Nutrition & Santé",
    zone: "Dakar",
    projet: "Secours Alimentaire",
    statut: "INACTIF",
  },
]

export const gerantStatistiquesMock = {
  totalProjets: 5,
  totalUtilisateurs: 6,
  budgetTotal: 42000000,
  bailleursCount: 5,
  partenairesCount: 4,
  budgetEngage: 32500000,
  soldeDisponible: 9500000,
  tauxExecution: 77,
}

export const gerantDashboardMock = {
  statistiques: gerantStatistiquesMock,
  projets: projetsGerantMock,
  utilisateurs: utilisateursMock,
  bailleurs: bailleursGerantMock,
  partenaires: partenairesGerantMock,
  chefsProjet: chefsProjetMock,
  responsablesFinance: responsablesFinanceMock,
}

export const gerantService = {
  getProjets() {
    return projetsGerantMock
  },
  getChefsProjet() {
    return chefsProjetMock
  },
  getResponsablesFinance() {
    return responsablesFinanceMock
  },
  getUtilisateurs() {
    return utilisateursMock
  },
  getUtilisateursStatistiques() {
    return utilisateursStatistiquesMock
  },
  getBailleurs() {
    return bailleursGerantMock
  },
  getPartenaires() {
    return partenairesGerantMock
  },
  getStatistiques() {
    return gerantStatistiquesMock
  },
  getDashboard() {
    return gerantDashboardMock
  },
}

