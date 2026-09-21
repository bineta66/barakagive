import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import Dashboard from "./views/dashboard/Dashboard.vue";
import ListeProjets from "./views/projets/ListeProjets.vue";
import DetailProjet from "./views/projets/DetailProjet.vue";
import CarteZones from "./views/zones/CarteZones.vue";
import ListeZones from "./views/zones/ListeZones.vue";
import CreerZone from "./views/zones/CreerZone.vue";
import ModifierZone from "./views/zones/ModifierZone.vue";
import DetailZone from "./views/zones/DetailZone.vue";
import ZoneAnalyseIA from "./views/zones/ZoneAnalyseIA.vue";
import RegionAnalyseIA from "./views/zones/RegionAnalyseIA.vue";
import ListeCampagnes from "./views/campagnes/ListeCampagnes.vue";
import CreerCampagne from "./views/campagnes/CreerCampagne.vue";
import ModifierCampagne from "./views/campagnes/ModifierCampagne.vue";
import DetailCampagne from "./views/campagnes/DetailCampagne.vue";
import FormulaireDynamique from "./views/campagnes/FormulaireDynamique.vue";
import CartePriorites from "@/modules/chef-projet/views/priorites/CartePriorites.vue";
import TableauBeneficiairesZone from "./views/priorites/TableauBeneficiairesZone.vue";
import ListeFinances from "./views/finances/ListeFinances.vue";
import DetailProjetFinance from "./views/finances/DetailProjetFinance.vue";
import ListePartenaires from "./views/partenaires/ListePartenaires.vue";
import ListeBailleurs from "./views/bailleurs/ListeBailleurs.vue";
import ListeRapports from "./views/rapports/ListeRapports.vue";

const routes = [
  {
    path: "/chef-projet",
    component: DashboardLayout,
    redirect: { name: "dashboard" },
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: Dashboard,
      },
      {
        path: "projets",
        name: "projets",
        component: ListeProjets,
      },
      {
        path: "projets/:id",
        name: "projets-detail",
        component: DetailProjet,
      },
      {
        path: "zones",
        name: "zones",
        component: ListeZones,
      },
      {
        path: "zones/carte",
        name: "zones-carte",
        component: CarteZones,
      },
      {
        path: "zones/creer",
        name: "zones-creer",
        component: CreerZone,
      },
      {
        path: "zones/modifier/:id",
        name: "zones-modifier",
        component: ModifierZone,
      },
      {
        path: "zones/:id",
        name: "zones-detail",
        component: DetailZone,
      },
      {
        path: "zones/analyse/:id",
        name: "zones-analyse-ia",
        component: ZoneAnalyseIA,
      },
      {
        path: "zones/analyse-region/:region",
        name: "zones-analyse-region",
        component: RegionAnalyseIA,
      },
      {
        path: "campagnes",
        name: "campagnes",
        component: ListeCampagnes,
      },
      {
        path: "campagnes/creer",
        name: "campagnes-creer",
        component: CreerCampagne,
      },
      {
        path: "campagnes/modifier/:id",
        name: "campagnes-modifier",
        component: ModifierCampagne,
      },
      {
        path: "campagnes/:id",
        name: "campagnes-detail",
        component: DetailCampagne,
      },
      {
        path: "campagnes/:id/formulaire",
        name: "campagnes-formulaire",
        component: FormulaireDynamique,
      },
      {
        path: "carte-priorites",
        name: "carte-priorites",
        component: CartePriorites,
      },
      {
        path: "zones/:zoneId/beneficiaires",
        name: "beneficiaires-zone",
        component: TableauBeneficiairesZone,
        props: true,
      },
      {
        path: "beneficiaires/zone",
        redirect: to => ({
          name: "beneficiaires-zone",
          params: { zoneId: to.query.zoneId || to.query.zone || "" },
          query: to.query,
        }),
      },
      {
        path: "finances",
        name: "finances",
        component: ListeFinances,
      },
      {
        path: "finances/:id",
        name: "finances-detail",
        component: DetailProjetFinance,
      },
      {
        path: "partenaires",
        name: "partenaires",
        component: ListePartenaires,
      },
      {
        path: "bailleurs",
        name: "bailleurs",
        component: ListeBailleurs,
      },
      {
        path: "rapports",
        name: "rapports",
        component: ListeRapports,
      },
    ],
  },
];

export default routes;

// Cache bust
