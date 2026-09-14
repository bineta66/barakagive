import { ref, computed } from "vue"
import { defineStore } from "pinia"

const utilisateursMock = [
  {
    id: 1,
    nom: "Amine Diop",
    email: "amine@barakagive.org",
    role: "Super Administrateur",
    avatar: "User",
  },
  {
    id: 2,
    nom: "Fatou Sow",
    email: "fatou@barakagive.org",
    role: "Chef de projet",
    avatar: "User",
  },
  {
    id: 3,
    nom: "Mariam Ndiaye",
    email: "mariam@barakagive.org",
    role: "Responsable Finance",
    avatar: "User",
  },
  {
    id: 4,
    nom: "Ibrahima Ba",
    email: "ibrahima@barakagive.org",
    role: "Gérant",
    avatar: "User",
  },
  {
    id: 5,
    nom: "Aïssatou Diallo",
    email: "aissatou@barakagive.org",
    role: "Agent de terrain",
    avatar: "User",
  },
]

const getSavedUserRole = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("userRole")
  }
  return null
}

const getInitialUser = () => {
  const savedRole = getSavedUserRole()
  if (savedRole) {
    const user = utilisateursMock.find((u) => u.role === savedRole)
    if (user) return user
  }
  return utilisateursMock[0]
}

export const useAuthStore = defineStore("auth", () => {
  const utilisateur = ref(getInitialUser())

  const setRole = (role) => {
    const user = utilisateursMock.find((u) => u.role === role)
    if (user) {
      utilisateur.value = user
      if (typeof window !== "undefined") {
        localStorage.setItem("userRole", role)
      }
    }
  }

  const role = computed(() => utilisateur.value.role)
  const nom = computed(() => utilisateur.value.nom)
  const email = computed(() => utilisateur.value.email)

  return {
    utilisateur,
    role,
    nom,
    email,
    setRole,
    utilisateursMock,
  }
})

export const ROLES = {
  SUPER_ADMIN: "Super Administrateur",
  CHEF_PROJET: "Chef de projet",
  RESPONSABLE_FINANCE: "Responsable Finance",
  GERANT: "Gérant",
  AGENT: "Agent de terrain",
}

