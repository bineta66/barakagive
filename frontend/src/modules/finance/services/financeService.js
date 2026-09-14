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

export const budgetsMock = ref([
  { id: 1, projetId: 1, projet: "Distribution alimentaire hivernage", chefProjet: "Awa Diop", budgetTotal: 15000000, consomme: 12500000, solde: 2500000, statut: "En cours", exercice: "2025", dateDebut: "2025-01-15", dateFin: "2025-11-30", observation: "" },
  { id: 2, projetId: 2, projet: "Accès Eau Potable & Forages Solaires", chefProjet: "Mamadou Sow", budgetTotal: 8500000, consomme: 7200000, solde: 1300000, statut: "Terminée", exercice: "2025", dateDebut: "2025-02-01", dateFin: "2025-12-31", observation: "" },
  { id: 3, projetId: 3, projet: "Cliniques Mobiles & Soins Pédiatriques", chefProjet: "Fatou Ndiaye", budgetTotal: 9200000, consomme: 6800000, solde: 2400000, statut: "En cours", exercice: "2025", dateDebut: "2025-07-01", dateFin: "2026-06-30", observation: "" },
  { id: 4, projetId: 4, projet: "Appui Agricole & Résilience Maraîchère", chefProjet: "Cheikh Diop", budgetTotal: 6500000, consomme: 6200000, solde: 300000, statut: "Planifiée", exercice: "2024", dateDebut: "2024-03-10", dateFin: "2025-05-15", observation: "" },
  { id: 5, projetId: 5, projet: "Secours Alimentaire & Nutrition d'Urgence", chefProjet: "Ousmane Diallo", budgetTotal: 4500000, consomme: 0, solde: 4500000, statut: "À budgétiser", exercice: "2025", dateDebut: "2025-01-15", dateFin: "2025-11-30", observation: "" },
  { id: 6, projetId: 6, projet: "Sensibilisation Hygiène & Assainissement", chefProjet: "Ibrahima Sall", budgetTotal: 3800000, consomme: 2100000, solde: 1700000, statut: "Terminée", exercice: "2025", dateDebut: "2025-02-01", dateFin: "2025-03-31", observation: "" },
])

export const budgetsStatistiquesMock = {
  budgetTotal: 47500000,
  budgetConsomme: 29800000,
  soldeDisponible: 17700000,
  projetsBudgétises: 6,
}

export const donsFinancementsMock = ref([
  { id: 1, projetId: 1, projet: "Distribution alimentaire hivernage", bailleur: "UNICEF", montant: 5000000, date: "2025-09-10", reference: "REF-2025-001", statut: "Validé", typeFinancement: "Subvention", commentaire: "" },
  { id: 2, projetId: 2, projet: "Accès Eau Potable & Forages Solaires", bailleur: "Banque Mondiale", montant: 8000000, date: "2025-09-05", reference: "REF-2025-002", statut: "Validé", typeFinancement: "Prêt", commentaire: "" },
  { id: 3, projetId: 3, projet: "Cliniques Mobiles & Soins Pédiatriques", bailleur: "UNICEF", montant: 3500000, date: "2025-09-08", reference: "REF-2025-003", statut: "En attente", typeFinancement: "Subvention", commentaire: "" },
  { id: 4, projetId: 1, projet: "Distribution alimentaire hivernage", bailleur: "Union Européenne", montant: 2000000, date: "2025-09-01", reference: "REF-2025-004", statut: "Validé", typeFinancement: "Don", commentaire: "" },
  { id: 5, projetId: 5, projet: "Secours Alimentaire & Nutrition d'Urgence", bailleur: "Banque Mondiale", montant: 1500000, date: "2025-08-28", reference: "REF-2025-005", statut: "Rejeté", typeFinancement: "Subvention", commentaire: "Dossier incomplet" },
])

export const donsStatistiquesMock = {
  totalFinancements: 20000000,
  nombreBailleurs: 3,
  financementDuMois: 18500000,
  projetsFinances: 4,
}

export const bailleursMock = [
  "UNICEF",
  "Banque Mondiale",
  "Union Européenne",
  "UNDP",
  "USAID",
  "GIZ",
]

export const typesFinancementMock = [
  "Subvention",
  "Don",
  "Prêt",
  "Investissement",
]

export const depensesMock = ref([
  { id: 1, projetId: 1, projet: "Distribution alimentaire hivernage", categorie: "Alimentation", montant: 2500000, date: "2025-09-12", fournisseur: "Société Africaine de Distribution", modePaiement: "Virement", statut: "Validé", libelle: "Paiement fournisseur - Distribution alimentaire", campagne: "Campagne 1", justificatif: 1, commentaire: "" },
  { id: 2, projetId: 2, projet: "Accès Eau Potable & Forages Solaires", categorie: "Logistique", montant: 950000, date: "2025-09-03", fournisseur: "Forages SA", modePaiement: "Espèces", statut: "Validé", libelle: "Paiement prestataire - Eau potable", campagne: "Campagne 2", justificatif: 2, commentaire: "" },
  { id: 3, projetId: 3, projet: "Cliniques Mobiles & Soins Pédiatriques", categorie: "Santé", montant: 1800000, date: "2025-09-08", fournisseur: "Pharmacie Centrale", modePaiement: "Chèque", statut: "En attente", libelle: "Approvisionnement médicaments - Cliniques mobiles", campagne: "Campagne 1", justificatif: null, commentaire: "" },
  { id: 4, projetId: 1, projet: "Distribution alimentaire hivernage", categorie: "Alimentation", montant: 3200000, date: "2025-08-25", fournisseur: "Coopérative Agricole", modePaiement: "Virement", statut: "Validé", libelle: "Achat intrants alimentaires", campagne: "Campagne 1", justificatif: 3, commentaire: "" },
  { id: 5, projetId: 4, projet: "Appui Agricole & Résilience Maraîchère", categorie: "Logistique", montant: 750000, date: "2025-08-15", fournisseur: "Matériel Agricole SARL", modePaiement: "Virement", statut: "Rejeté", libelle: "Achat semences résistantes", campagne: "Campagne 3", justificatif: null, commentaire: "Facture manquante" },
])

export const depensesStatistiquesMock = {
  depensesTotales: 9200000,
  depensesDuMois: 5700000,
  nombreOperations: 5,
  budgetRestant: 38300000,
}

export const categoriesDepenseMock = [
  "Alimentation",
  "Logistique",
  "Santé",
  "Éducation",
  "Transport",
  "Personnel",
  "Loyer",
  "Équipement",
]

export const modesPaiementMock = [
  "Virement",
  "Espèces",
  "Chèque",
  "Mobile Money",
  "Prélèvement",
]

export const justificatifsMock = ref([
  { id: 1, depenseId: 1, depense: "Paiement fournisseur - Distribution alimentaire", projet: "Distribution alimentaire hivernage", typeDocument: "Facture", numeroDocument: "FAC-2025-001", dateDocument: "2025-09-12", montant: 2500000, statut: "Validé", observation: "" },
  { id: 2, depenseId: 2, depense: "Paiement prestataire - Eau potable", projet: "Accès Eau Potable & Forages Solaires", typeDocument: "Facture", numeroDocument: "FAC-2025-002", dateDocument: "2025-09-03", montant: 950000, statut: "Validé", observation: "" },
  { id: 3, depenseId: 4, depense: "Achat intrants alimentaires", projet: "Distribution alimentaire hivernage", typeDocument: "Facture", numeroDocument: "FAC-2025-003", dateDocument: "2025-08-25", montant: 3200000, statut: "En attente", observation: "" },
])

export const justificatifsStatistiquesMock = {
  valides: 2,
  enAttente: 1,
  montantJustifie: 6650000,
  depensesSansJustificatif: 2,
}

export const typesDocumentMock = [
  "Facture",
  "Reçu",
  "Contrat",
  "Attestation",
  "Rapport",
  "Autre",
]

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
  getAllBudgets() {
    return budgetsMock
  },
  getBudgetsStatistiques() {
    return budgetsStatistiquesMock
  },
  getAllDonsFinancements() {
    return donsFinancementsMock
  },
  getDonsStatistiques() {
    return donsStatistiquesMock
  },
  getAllDepenses() {
    return depensesMock
  },
  getDepensesStatistiques() {
    return depensesStatistiquesMock
  },
  getAllJustificatifs() {
    return justificatifsMock
  },
  getJustificatifsStatistiques() {
    return justificatifsStatistiquesMock
  },
  getCategoriesDepense() {
    return categoriesDepenseMock
  },
  getModesPaiement() {
    return modesPaiementMock
  },
  getTypesDocument() {
    return typesDocumentMock
  },
  getBailleurs() {
    return bailleursMock
  },
  getTypesFinancement() {
    return typesFinancementMock
  },
}
