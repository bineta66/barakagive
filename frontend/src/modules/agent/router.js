import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import MesCampagnes from "./views/MesCampagnes.vue";
import BeneficiairesCampagne from "./views/BeneficiairesCampagne.vue";
import ProfilAgent from "./views/ProfilAgent.vue";
import CollecteTerrain from "./views/CollecteTerrain.vue";
import DetailBeneficiaire from "./views/DetailBeneficiaire.vue";
import AgentSynchronisation from "./views/AgentSynchronisation.vue";
import DashboardAgent from "./views/DashboardAgent.vue";
import AgentZones from "./views/AgentZones.vue";
import BeneficiairesAgent from "./views/BeneficiairesAgent.vue";

const routes = [
  {
    path: "/agent",
     component: DashboardLayout,
    redirect: { name: "agent-dashboard" },
    children: [
      { path: "dashboard", name: "agent-dashboard", component: DashboardAgent },
      {
        path: "campagnes",
        name: "agent-campagnes",
        component: MesCampagnes,
      },
      { path: "zones", name: "agent-zones", component: AgentZones },
      { path: "beneficiaires", name: "agent-beneficiaires", component: BeneficiairesAgent },
      { path: "collectes", name: "agent-collectes", component: MesCampagnes },
      {
        path: "campagnes/:id/beneficiaires",
        name: "agent-campagne-beneficiaires",
        component: BeneficiairesCampagne,
      },
      {
        path: "campagnes/:id/formulaire",
        name: "agent-campagne-formulaire",
        component: CollecteTerrain,
      },
      {
        path: "beneficiaires/:id",
        name: "agent-beneficiaire-detail",
        component: DetailBeneficiaire,
      },
      {
        path: "synchronisation",
        name: "agent-sync",
        component: AgentSynchronisation,
      },
      {
        path: "profil",
        name: "agent-profil",
        component: ProfilAgent,
      },
    ],
  },
];

export default routes;
