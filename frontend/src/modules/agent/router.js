import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import AgentCampagnes from "./views/AgentCampagnes.vue";
import BeneficiairesCampagne from "./views/BeneficiairesCampagne.vue";
import ProfilAgent from "./views/ProfilAgent.vue";
import CollecteTerrain from "./views/CollecteTerrain.vue";
import DetailBeneficiaire from "./views/DetailBeneficiaire.vue";
import Synchronisation from "./views/Synchronisation.vue";

const routes = [
  {
    path: "/agent",
     component: DashboardLayout,
    redirect: { name: "agent-campagnes" },
    children: [
      {
        path: "campagnes",
        name: "agent-campagnes",
        component: AgentCampagnes,
      },
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
        component: Synchronisation,
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

