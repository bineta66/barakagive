import { ref } from "vue"

export const financesMock = ref([
  {
    id: 1,
    code: "PRJ-2025-001",
    nom: "Distribution alimentaire hivernage",
    responsable: "Chef de projet Alimentaire",
    budgetAllocation: 15000000,
    montantEngage: 12500000,
    statut: "En cours",
    dateDebut: "15 Jan 2025",
    dateFin: "30 Nov 2025",
    region: "Dakar",
  },
  {
    id: 2,
    code: "PRJ-2025-072",
    nom: "Accès Eau Potable & Forages Solaires",
    responsable: "Chef de projet Eau",
    budgetAllocation: 8500000,
    montantEngage: 7200000,
    statut: "Terminée",
    dateDebut: "01 Fév 2025",
    dateFin: "31 Déc 2025",
    region: "Thiès",
  },
  {
    id: 3,
    code: "PRJ-2025-104",
    nom: "Cliniques Mobiles & Soins Pédiatriques",
    responsable: "Chef de projet Santé",
    budgetAllocation: 9200000,
    montantEngage: 6800000,
    statut: "En cours",
    dateDebut: "01 Juil 2025",
    dateFin: "30 Juin 2026",
    region: "Kaolack",
  },
  {
    id: 4,
    code: "PRJ-2024-045",
    nom: "Appui Agricole & Résilience Maraîchère",
    responsable: "Chef de projet Agriculture",
    budgetAllocation: 6500000,
    montantEngage: 6200000,
    statut: "Planifiée",
    dateDebut: "10 Mar 2024",
    dateFin: "15 Mai 2025",
    region: "Saint-Louis",
  },
  {
    id: 5,
    code: "PRJ-2025-032",
    nom: "Secours Alimentaire & Nutrition d'Urgence",
    responsable: "Chef de projet Nutrition",
    budgetAllocation: 4500000,
    montantEngage: 3800000,
    statut: "En cours",
    dateDebut: "15 Jan 2025",
    dateFin: "30 Nov 2025",
    region: "Dakar",
  },
  {
    id: 6,
    code: "PRJ-2025-058",
    nom: "Sensibilisation Hygiène & Assainissement",
    responsable: "Chef de projet Hygiène",
    budgetAllocation: 3800000,
    montantEngage: 2100000,
    statut: "Terminée",
    dateDebut: "01 Fév 2025",
    dateFin: "31 Mars 2025",
    region: "Kolda",
  },
  {
    id: 7,
    code: "PRJ-2025-089",
    nom: "Protection Sociale & Appui aux Plus Vulnérables",
    responsable: "Chef de projet Protection",
    budgetAllocation: 5200000,
    montantEngage: 4100000,
    statut: "Planifiée",
    dateDebut: "01 Avr 2025",
    dateFin: "30 Sept 2025",
    region: "Tambacounda",
  },
  {
    id: 8,
    code: "PRJ-2024-098",
    nom: "Réhabilitation d'Infrastructures Scolaires",
    responsable: "Chef de projet Éducation",
    budgetAllocation: 7500000,
    montantEngage: 7100000,
    statut: "En cours",
    dateDebut: "01 Oct 2024",
    dateFin: "31 Mars 2025",
    region: "Matam",
  },
])

export const depensesParCategorieMock = [
  { categorie: "Alimentation", montant: 22500000, couleur: "#F59E0B" },
  { categorie: "Santé", montant: 18900000, couleur: "#10B981" },
  { categorie: "Logistique", montant: 15600000, couleur: "#3B82F6" },
  { categorie: "Éducation", montant: 12300000, couleur: "#8B5CF6" },
]

export const dernieresOperationsMock = [
  { id: 1, date: "12 Sep 2025", libelle: "Paiement fournisseur - Distribution alimentaire", montant: 2500000, type: "depense" },
  { id: 2, date: "10 Sep 2025", libelle: "Donation UNICEF", montant: 5000000, type: "don" },
  { id: 3, date: "08 Sep 2025", libelle: "Paiement personnel - Cliniques mobiles", montant: 1800000, type: "depense" },
  { id: 4, date: "05 Sep 2025", libelle: "Don Banque Mondiale", montant: 8000000, type: "don" },
  { id: 5, date: "03 Sep 2025", libelle: "Paiement prestataire - Eau potable", montant: 950000, type: "depense" },
]

export const projetsAssignesMock = ref([
  { id: 1, code: "PRJ-2025-001", nom: "Distribution alimentaire hivernage", chefProjet: "Awa Diop", budget: 12500000, statut: "Budgétisé", region: "Kaolack" },
  { id: 2, code: "PRJ-2025-072", nom: "Accès Eau Potable & Forages Solaires", chefProjet: "Mamadou Sow", budget: 8500000, statut: "En cours", region: "Thiès" },
  { id: 3, code: "PRJ-2025-104", nom: "Cliniques Mobiles & Soins Pédiatriques", chefProjet: "Fatou Ndiaye", budget: 9200000, statut: "En cours", region: "Kaolack" },
  { id: 4, code: "PRJ-2025-032", nom: "Secours Alimentaire & Nutrition d'Urgence", chefProjet: "Ousmane Diallo", budget: 4500000, statut: "À budgétiser", region: "Dakar" },
  { id: 5, code: "PRJ-2024-098", nom: "Réhabilitation d'Infrastructures Scolaires", chefProjet: "Marième Ba", budget: 7500000, statut: "En cours", region: "Matam" },
  { id: 6, code: "PRJ-2025-058", nom: "Sensibilisation Hygiène & Assainissement", chefProjet: "Ibrahima Sall", budget: 3800000, statut: "Budgétisé", region: "Kolda" },
  { id: 7, code: "PRJ-2025-089", nom: "Protection Sociale & Appui aux Plus Vulnérables", chefProjet: "Aminata Cissé", budget: 5200000, statut: "À budgétiser", region: "Tambacounda" },
  { id: 8, code: "PRJ-2024-045", nom: "Appui Agricole & Résilience Maraîchère", chefProjet: "Cheikh Diop", budget: 6500000, statut: "Budgétisé", region: "Saint-Louis" },
])

export const statistiquesFinanceMock = {
  budgetTotal: 345000000,
  depensesRealisees: 224250000,
  soldeDisponible: 120750000,
  tauxExecution: 65,
  campagnesFinancées: 7,
  totalProjets: 4,
}

export const financeService = {
  getFinances() {
    return financesMock
  },
  getDepensesParCategorie() {
    return depensesParCategorieMock
  },
  getDernieresOperations() {
    return dernieresOperationsMock
  },
  getProjetsAssignes() {
    return projetsAssignesMock
  },
  getStatistiques() {
    return statistiquesFinanceMock
  },
}
