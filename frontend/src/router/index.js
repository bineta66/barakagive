import { createRouter, createWebHistory } from "vue-router";
import ReinitialisationMotDePasse from "@/views/authentification/ReinitialisationMotDePasse.vue";
import MotDePasseOublie from "@/views/authentification/MotDePasseOublie.vue";
import ActivationCompte from "@/views/authentification/ActivationCompte.vue";
import Connexion from "@/views/authentification/Connexion.vue";
import chefProjectRoutes from "@/modules/chef-projet/router.js";
import financeRoutes from "@/modules/finance/router.js";
import gerantRoutes from "@/modules/gerant/router.js";
import superAdminRoutes from "@/modules/super-admin/router.js";
import agentRoutes from "@/modules/agent/router.js";

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
  ...chefProjectRoutes,
  ...financeRoutes,
  ...gerantRoutes,
  ...superAdminRoutes,
  ...agentRoutes,
  {
    path: "/:pathMatch(.*)*",
    redirect: "/chef-projet/dashboard",
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
