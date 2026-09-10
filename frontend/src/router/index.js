import { createRouter, createWebHistory } from "vue-router";
import ReinitialisationMotDePasse from "@/views/authentification/ReinitialisationMotDePasse.vue";
import MotDePasseOublie from "@/views/authentification/MotDePasseOublie.vue";
import ActivationCompte from "@/views/authentification/ActivationCompte.vue";
import Connexion from "@/views/authentification/Connexion.vue";
import DashboardLayout from "@/layouts/DashboardLayout.vue";
import ListeProjets from "@/views/projets/ListeProjets.vue";
import CreerProjet from "@/views/projets/CreerProjet.vue";
import ModifierProjet from "@/views/projets/ModifierProjet.vue";
import DetailProjet from "@/views/projets/DetailProjet.vue";
import CarteZones from "@/views/zones/CarteZones.vue";
import ListeZones from "@/views/zones/ListeZones.vue";
import CreerZone from "@/views/zones/CreerZone.vue";
import ModifierZone from "@/views/zones/ModifierZone.vue";
import DetailZone from "@/views/zones/DetailZone.vue";

const routes = [
  {
    path: "/",
    redirect: "/connexion",
  },
  {
    path: "/connexion",
    name: "connexion",
    component: Connexion,
  },
  {
    path: "/mot-de-passe-oublie",
    name: "mot-de-passe-oublie",
    component: MotDePasseOublie,
  },
  {
    path: "/activation-compte",
    name: "activation-compte",
    component: ActivationCompte,
  },
  {
    path: "/reinitialisation",
    name: "reinitialisation",
    component: ReinitialisationMotDePasse,
  },
  {
    path: "/projets",
    component: DashboardLayout,
    children: [
      {
        path: "",
        name: "projets",
        component: ListeProjets,
      },
      {
        path: "creer",
        name: "projets-creer",
        component: CreerProjet,
      },
      {
        path: "modifier/:id",
        name: "projets-modifier",
        component: ModifierProjet,
      },
      {
        path: ":id",
        name: "projets-detail",
        component: DetailProjet,
      },
    ],
  },
  {
    path: "/ListeProjets",
    redirect: "/projets",
  },
  {
    path: "/zones",
    component: DashboardLayout,
    children: [
      {
        path: "",
        name: "zones",
        component: CarteZones,
      },
      {
        path: "liste",
        name: "zones-liste",
        component: ListeZones,
      },
      {
        path: "creer",
        name: "zones-creer",
        component: CreerZone,
      },
      {
        path: "modifier/:id",
        name: "zones-modifier",
        component: ModifierZone,
      },
      {
        path: ":id",
        name: "zones-detail",
        component: DetailZone,
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/projets",
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});