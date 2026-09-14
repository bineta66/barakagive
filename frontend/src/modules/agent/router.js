import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import DashboardAgent from "./views/DashboardAgent.vue";
import MesCampagnes from "./views/MesCampagnes.vue";
import CollecteTerrain from "./views/CollecteTerrain.vue";
import Synchronisation from "./views/Synchronisation.vue";

const routes = [
  {
    path: "/agent",
     component: DashboardLayout,
    redirect: { name: "agent-dashboard" },
    children: [
      {
        path: "dashboard",
        name: "agent-dashboard",
        component: DashboardAgent,
      },
      {
        path: "campagnes",
        name: "agent-campagnes",
        component: MesCampagnes,
      },
      {
        path: "collecte",
        name: "agent-collecte",
        component: CollecteTerrain,
      },
      {
        path: "sync",
        name: "agent-sync",
        component: Synchronisation,
      },
    ],
  },
];

export default routes;

