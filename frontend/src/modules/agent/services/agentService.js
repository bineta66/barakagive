import { ref } from "vue"

export const campagnesAgentMock = ref([
  {
    id: 1,
    nom: "Collecte de médicaments - Zone de santé 1",
    ONG: "Médecins du Monde",
    zone: "Dakar Est",
    statut: "En cours",
    dateDebut: "2025-08-01",
    dateFin: "2025-09-30",
    collecte: 850000,
    objectif: 1000000,
  },
  {
    id: 2,
    nom: "Campagne de vaccination - Zone de santé 2",
    ONG: "UNICEF Sénégal",
    zone: "Dakar Nord",
    statut: "Terminé",
    dateDebut: "2025-07-01",
    dateFin: "2025-07-31",
    collecte: 1200000,
    objectif: 800000,
  },
  {
    id: 3,
    nom: "Distributions alimentaires - Zone de santé 3",
    ONG: "Action Against Hunger",
    zone: "Pikine",
    statut: "Planifié",
    dateDebut: "2025-09-15",
    dateFin: "2025-10-15",
    collecte: 0,
    objectif: 500000,
  },
])

export const collectesTerrainMock = ref([
  {
    id: 1,
    date: "2025-09-01",
    campagne: "Collecte de médicaments",
    zone: "Dakar Est",
    montant: 450000,
    statut: "Synchronisé",
  },
  {
    id: 2,
    date: "2025-09-02",
    campagne: "Vaccination",
    zone: "Dakar Nord",
    montant: 320000,
    statut: "Synchronisé",
  },
  {
    id: 3,
    date: "2025-09-03",
    campagne: "Distribution alimentaire",
    zone: "Pikine",
    montant: 280000,
    statut: "En attente de sync",
  },
])

export const agentStatistiquesMock = {
  campagnesTotales: 3,
  campagnesEnCours: 1,
  campagnesTerminees: 1,
  campagnesPlanifiees: 1,
  collecteTotale: 2330000,
  objectifTotal: 2300000,
  tauxRealisation: 101,
  collectesTerrain: 3,
  elementsSynchronises: 2,
  elementsEnAttente: 1,
}

export const agentService = {
  getCampagnes() {
    return campagnesAgentMock
  },
  getCollectesTerrain() {
    return collectesTerrainMock
  },
  getStatistiques() {
    return agentStatistiquesMock
  },
}

