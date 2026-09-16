import { createRouter, createWebHistory } from "vue-router";
import ReinitialisationMotDePasse from "@/views/authentification/ReinitialisationMotDePasse.vue";
import MotDePasseOublie from "@/views/authentification/MotDePasseOublie.vue";
import ActivationCompte from "@/views/authentification/ActivationCompte.vue";
import Connexion from "@/views/authentification/Connexion.vue";
import InscriptionONG from "@/views/authentification/InscriptionONG.vue";
import LandingPage from "@/views/LandingPage.vue";
import chefProjectRoutes from "@/modules/chef-projet/router.js";
import financeRoutes from "@/modules/finance/router.js";
import gerantRoutes from "@/modules/gerant/router.js";
import superAdminRoutes from "@/modules/super-admin/router.js";
import agentRoutes from "@/modules/agent/router.js";

const routes = [
  {
    path: "/",
    component: LandingPage,
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
    path: "/activate",
    redirect: (to) => ({ path: "/activation-compte", query: to.query }),
  },
  {
    path: "/inscription",
    name: "inscription",
    component: InscriptionONG,
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
    redirect: "/connexion",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const publicPaths = [
  "/",
  "/connexion",
  "/inscription",
  "/activation-compte",
  "/activate",
  "/reinitialisation",
];

router.beforeEach((to) => {
  const token = localStorage.getItem("accessToken");
  const isPublic = publicPaths.some((p) => to.path.startsWith(p));

  if (!token && !isPublic) {
    return { path: "/connexion", query: { redirect: to.fullPath } };
  }

  if (token && to.path === "/connexion") {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      switch (user.role) {
        case "SUPER_ADMIN":
          return "/super-admin/dashboard";
        case "GERANT":
          return "/gerant/dashboard";
        case "CHEF_PROJET":
          return "/chef-projet/dashboard";
        case "AGENT":
          return "/agent/dashboard";
        case "FINANCE":
          return "/finance/dashboard";
        default:
          return;
      }
    } catch {
      return;
    }
  }

  if (token && to.path === "/") {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      switch (user.role) {
        case "SUPER_ADMIN":
          return "/super-admin/dashboard";
        case "GERANT":
          return "/gerant/dashboard";
        case "CHEF_PROJET":
          return "/chef-projet/dashboard";
        case "AGENT":
          return "/agent/dashboard";
        case "FINANCE":
          return "/finance/dashboard";
        default:
          return;
      }
    } catch {
      return;
    }
  }

  return;
});

export default router;
