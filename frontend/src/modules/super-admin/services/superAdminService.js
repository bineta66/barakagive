import { ref } from "vue"

export const demandesONGMock = ref([
  {
    id: 1,
    nom: "ONG Secours Civique International",
    email: "contact@sci.org",
    pays: "Sénégal",
    dateDemande: "2025-09-08",
    statut: "En attente",
    telephone: "+221 33 000 00 00",
  },
  {
    id: 2,
    nom: "Association Humanitaire Solidarité",
    email: "info@ahs.ngo",
    pays: "Sénégal",
    dateDemande: "2025-09-09",
    statut: "En attente",
    telephone: "+221 77 000 00 00",
  },
  {
    id: 3,
    nom: "Caravane de l'Espoir",
    email: "contact@caravane.org",
    pays: "Mali",
    dateDemande: "2025-09-10",
    statut: "En attente",
    telephone: "+223 22 00 00 00",
  },
])

export const ongsMock = ref([
  {
    id: 1,
    nom: "BarakaGive International",
    email: "contact@barakagive.org",
    pays: "Sénégal",
    dateCreation: "2024-01-15",
    statut: "Actif",
    utilisateurs: 42,
    projets: 8,
  },
  {
    id: 2,
    nom: "Médecins du Monde",
    email: "contact@medecinsdumonde.org",
    pays: "Sénégal",
    dateCreation: "2024-03-20",
    statut: "Actif",
    utilisateurs: 28,
    projets: 5,
  },
  {
    id: 3,
    nom: "Action Against Hunger",
    email: "sa@actionagainsthunger.org",
    pays: "Sénégal",
    dateCreation: "2024-05-10",
    statut: "Inactif",
    utilisateurs: 15,
    projets: 3,
  },
  {
    id: 4,
    nom: "UNICEF Sénégal",
    email: "unicef@unicef.org",
    pays: "Sénégal",
    dateCreation: "2024-02-01",
    statut: "Actif",
    utilisateurs: 35,
    projets: 12,
  },
])

export const abonnementsMock = ref([
  {
    id: 1,
    ong: "BarakaGive International",
    plan: "Enterprise",
    dateDebut: "2025-01-01",
    dateFin: "2025-12-31",
    statut: "Actif",
    montant: 1200000,
  },
  {
    id: 2,
    ong: "Médecins du Monde",
    plan: "Professional",
    dateDebut: "2025-03-20",
    dateFin: "2026-03-19",
    statut: "Actif",
    montant: 800000,
  },
  {
    id: 3,
    ong: "Action Against Hunger",
    plan: "Starter",
    dateDebut: "2025-05-10",
    dateFin: "2025-11-10",
    statut: "Expiré",
    montant: 400000,
  },
  {
    id: 4,
    ong: "UNICEF Sénégal",
    plan: "Enterprise",
    dateDebut: "2025-02-01",
    dateFin: "2026-01-31",
    statut: "Actif",
    montant: 1200000,
  },
])

export const superAdminStatistiquesMock = {
  totalONG: 4,
  ongActives: 3,
  totalUtilisateurs: 120,
  totalProjets: 28,
  revenuMensuel: 3200000,
  tauxActivation: 85,
  abonnementsActifs: 3,
  abonnementsExpires: 1,
}

export const plansMock = [
  { nom: "Starter", prix: 400000, utilisateurs: 10, projets: 3 },
  { nom: "Professional", prix: 800000, utilisateurs: 50, projets: 10 },
  { nom: "Enterprise", prix: 1200000, utilisateurs: "∞", projets: "∞" },
]

export const demandeStatistiquesMock = {
  totalDemandes: 3,
  enAttente: 3,
  traitees: 12,
}

export const abonnementStatistiquesMock = {
  revenuTotal: 3600000,
  mensuel: 2400000,
  actifs: 3,
  expires: 1,
}

export const superAdminService = {
  getDemandesONG() {
    return demandesONGMock
  },
  getONGs() {
    return ongsMock
  },
  getAbonnements() {
    return abonnementsMock
  },
  getStatistiques() {
    return superAdminStatistiquesMock
  },
  getPlans() {
    return plansMock
  },
  getDemandeStatistiques() {
    return demandeStatistiquesMock
  },
  getAbonnementStatistiques() {
    return abonnementStatistiquesMock
  },
}

