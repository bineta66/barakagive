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
  PiggyBank,
  Banknote,
  Activity,
  FileText,
  Building2,
  CreditCard,
  Smartphone,
  Cloud,
  RefreshCw
} from "lucide-vue-next";

export const menusConfig = {
  "Super Administrateur": [
    { nom: "Tableau de bord", route: "/super-admin/dashboard", icon: LayoutDashboard },
    { nom: "Demandes ONG", route: "/super-admin/demandes", icon: FileText },
    { nom: "ONG", route: "/super-admin/ongs", icon: Building2 },
    { nom: "Abonnements", route: "/super-admin/abonnements", icon: CreditCard },
    { nom: "Statistiques", route: "/super-admin/statistiques", icon: BarChart3 },
  ],

  "Chef de projet": [
    { nom: "Tableau de bord", route: "/chef-projet/dashboard", icon: LayoutDashboard },
    { nom: "Mes projets", route: "/chef-projet/projets", icon: FolderKanban },
    { nom: "Campagnes", route: "/chef-projet/campagnes", icon: ClipboardList },
    { nom: "Bénéficiaires", route: "/chef-projet/beneficiaires", icon: Users },
    { nom: "Zones", route: "/chef-projet/zones", icon: MapPinned },
    { nom: "Finances", route: "/chef-projet/finances", icon: Wallet },
    { nom: "Rapports", route: "/chef-projet/rapports", icon: BarChart3 },
  ],

  "Responsable Finance": [
    { nom: "Tableau de bord", route: "/finance/dashboard", icon: LayoutDashboard },
    { nom: "Projets assignés", route: "/finance/projets", icon: FolderKanban },
    { nom: "Budgets", route: "/finance/budgets", icon: Wallet },
    { nom: "Dons & Financements", route: "/finance/dons", icon: Banknote },
    { nom: "Dépenses", route: "/finance/depenses", icon: Receipt },
    { nom: "Justificatifs", route: "/finance/justificatifs", icon: ClipboardList },
    { nom: "Rapports financiers", route: "/finance/rapports", icon: BarChart3 },
  ],

  "Gérant": [
    { nom: "Tableau de bord", route: "/gerant/dashboard", icon: LayoutDashboard },
    { nom: "Mon ONG", route: "/gerant/mon-ong", icon: Building2 },
    { nom: "Utilisateurs", route: "/gerant/utilisateurs", icon: Users },
    { nom: "Projets", route: "/gerant/projets", icon: FolderKanban },
    { nom: "Finances", route: "/gerant/finances", icon: Wallet },
    { nom: "Partenaires", route: "/gerant/partenaires", icon: Handshake },
    { nom: "Bailleurs", route: "/gerant/bailleurs", icon: Landmark },
    { nom: "Rapports", route: "/gerant/rapports", icon: BarChart3 },
  ],

  "Agent de terrain": [
    { nom: "Mes campagnes", route: "/agent/campagnes", icon: FolderKanban },
      { nom: "Synchronisation", route: "/agent/synchronisation", icon: Smartphone },
      { nom: "Profil", route: "/agent/profil", icon: Users },
  ],
};

export const getMenusForRole = (role) => {
  return menusConfig[role] || menusConfig["Chef de projet"];
};

