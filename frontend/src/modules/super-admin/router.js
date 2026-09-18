import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import DashboardSuperAdmin from "./views/DashboardSuperAdmin.vue";
import DemandesONG from "./views/DemandesONG.vue";
import ONG from "./views/ONG.vue";
import Abonnements from "./views/Abonnements.vue";
import Statistiques from "./views/Statistiques.vue";

const routes = [
  {
    path: "/super-admin",
     component: DashboardLayout,
    redirect: { name: "super-admin-dashboard" },
    children: [
      {
        path: "dashboard",
        name: "super-admin-dashboard",
        component: DashboardSuperAdmin,
      },
      {
        path: "demandes",
        name: "super-admin-demandes",
        component: DemandesONG,
      },
      {
        path: "ongs",
        name: "super-admin-ongs",
        component: ONG,
      },
      {
        path: "abonnements",
        name: "super-admin-abonnements",
        component: Abonnements,
      },
      {
        path: "statistiques",
        name: "super-admin-statistiques",
        component: Statistiques,
      },
    ],
  },
];

export default routes;

