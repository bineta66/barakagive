import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import DashboardSuperAdmin from "./views/DashboardSuperAdmin.vue";
import DemandesONG from "./views/DemandesONG.vue";
import ONG from "./views/ONG.vue";
import Gerants from "./views/Gerants.vue";
import Abonnements from "./views/Abonnements.vue";

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
        path: "organisations/:id/verification",
        name: "super-admin-organisation-verification",
        component: () => import("./views/SuperAdminOrganisationVerification.vue"),
      },
      {
        path: "ongs",
        name: "super-admin-ongs",
        component: ONG,
      },
      {
        path: "gerants",
        name: "super-admin-gerants",
        component: Gerants,
      },
      {
        path: "abonnements",
        name: "super-admin-abonnements",
        component: Abonnements,
      },
    ],
  },
];

export default routes;
