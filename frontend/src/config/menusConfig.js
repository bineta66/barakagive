import {
  LayoutDashboard,
  FolderKanban,
  ClipboardList,
  Users,
  MapPinned,
  Wallet,
  Handshake,
  Landmark,
  BarChart3,
  Receipt,
  Banknote,
  FileText,
  Building2,
  CreditCard,
  Smartphone,
  Sparkles,
  UserCog,
} from "lucide-vue-next";

export const menusConfig = {
  "Super Administrateur": [
    { nom: "Tableau de bord", route: "/super-admin/dashboard", icon: LayoutDashboard },
    { nom: "Demandes ONG", route: "/super-admin/demandes", icon: FileText },
    { nom: "ONG", route: "/super-admin/ongs", icon: Building2 },
    { nom: "Gérants", route: "/super-admin/gerants", icon: UserCog },
    { nom: "Abonnements", route: "/super-admin/abonnements", icon: CreditCard },
  ],

  "Chef de projet": [
    { nom: "Tableau de bord", route: "/chef-projet/dashboard", icon: LayoutDashboard },
    { nom: "Mes projets", route: "/chef-projet/projets", icon: FolderKanban },
    { nom: "Campagnes", route: "/chef-projet/campagnes", icon: ClipboardList },
    { nom: "Carte des priorités", route: "/chef-projet/carte-priorites", icon: MapPinned },
    { nom: "Zones", route: "/chef-projet/zones", icon: MapPinned },
    { nom: "Finances", route: "/chef-projet/finances", icon: Wallet },
    { nom: "Rapports", route: "/chef-projet/rapports", icon: BarChart3 },
  ],

  "Responsable Finance": [
    { nom: "Tableau de bord", route: "/finance/dashboard", icon: LayoutDashboard },
    { nom: "Budgets", route: "/finance/budgets", icon: Wallet },
    { nom: "Lignes budgétaires", route: "/finance/lignes-budgetaires", icon: ClipboardList },
    { nom: "Financements", route: "/finance/financements", icon: Landmark },
    { nom: "Dons", route: "/finance/dons", icon: Banknote },
    { nom: "Dépenses", route: "/finance/depenses", icon: Receipt },
    { nom: "Justificatifs", route: "/finance/justificatifs", icon: ClipboardList },
    { nom: "Rapports financiers", route: "/finance/rapports", icon: BarChart3 },
  ],

  "Gérant": [
    { nom: "Tableau de bord", route: "/gerant/dashboard", icon: LayoutDashboard },
    { nom: "Assistant IA", route: "/gerant/assistant", icon: Sparkles },
    { nom: "Mon ONG", route: "/gerant/mon-ong", icon: Building2 },
    { nom: "Utilisateurs", route: "/gerant/utilisateurs", icon: Users },
    { nom: "Projets", route: "/gerant/projets", icon: FolderKanban },
    { nom: "Finances", route: "/gerant/finances", icon: Wallet },
    { nom: "Partenaires", route: "/gerant/partenaires", icon: Handshake },
    { nom: "Bailleurs", route: "/gerant/bailleurs", icon: Landmark },
    { nom: "Rapports", route: "/gerant/rapports", icon: BarChart3 },
  ],

  "Agent de terrain": [
    { nom: "Tableau de bord", route: "/agent/dashboard", icon: LayoutDashboard },
    { nom: "Mes campagnes", route: "/agent/campagnes", icon: FolderKanban },
    { nom: "Mes zones", route: "/agent/zones", icon: MapPinned },
    { nom: "Bénéficiaires", route: "/agent/beneficiaires", icon: Users },
    { nom: "Synchronisation", route: "/agent/synchronisation", icon: Smartphone },
  ],
};

export const getMenusForRole = (role) => {
  return menusConfig[role] || menusConfig["Chef de projet"];
};

