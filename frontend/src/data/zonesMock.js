import { ref } from "vue"

export const zonesMock = ref([
  {
    id: 1,
    nom: "Zone Nord Dakar",
    region: "Dakar",
    departement: "Dakar",
    rayon: 2500,
    statut: "Actif",
    latitude: 14.76,
    longitude: -17.44,
    dateCreation: "2026-01-10",
  },
  {
    id: 2,
    nom: "Zone Sud Thiès",
    region: "Thiès",
    departement: "Thiès",
    rayon: 1800,
    statut: "Inactif",
    latitude: 14.78,
    longitude: -16.92,
    dateCreation: "2026-02-05",
  },
])
