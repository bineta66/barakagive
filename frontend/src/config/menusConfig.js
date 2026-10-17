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
    { nom: "Tableau de bord", shortNom: "Accueil", route: "/super-admin/dashboard", icon: LayoutDashboard, mobilePrimary: true, description: "Indicateurs globaux et statistiques de la plateforme" },
    { nom: "Demandes ONG", shortNom: "Demandes", route: "/super-admin/demandes", icon: FileText, mobilePrimary: true, description: "Validation et vérification des demandes d'ONG" },
    { nom: "ONG", shortNom: "ONG", route: "/super-admin/ongs", icon: Building2, mobilePrimary: true, description: "Organisations non gouvernementales enregistrées" },
    { nom: "Gérants", shortNom: "Gérants", route: "/super-admin/gerants", icon: UserCog, mobilePrimary: true, description: "Comptes gérants et gestion des accès" },
    { nom: "Abonnements", shortNom: "Offres", route: "/super-admin/abonnements", icon: CreditCard, mobilePrimary: true, description: "Suivi des abonnements et formules actives" },
  ],

  "Chef de projet": [
    { nom: "Tableau de bord", shortNom: "Accueil", route: "/chef-projet/dashboard", icon: LayoutDashboard, mobilePrimary: true, description: "Pilotage opérationnel de vos projets affectés" },
    { nom: "Mes projets", shortNom: "Projets", route: "/chef-projet/projets", icon: FolderKanban, mobilePrimary: true, description: "Suivi et gestion des projets sur le terrain" },
    { nom: "Campagnes", shortNom: "Campagnes", route: "/chef-projet/campagnes", icon: ClipboardList, mobilePrimary: true, description: "Campagnes de collecte et distributions" },
    { nom: "Carte des priorités", shortNom: "Carte", route: "/chef-projet/carte-priorites", icon: MapPinned, mobilePrimary: true, description: "Cartographie et analyse des zones d'action" },
    { nom: "Zones", shortNom: "Zones", route: "/chef-projet/zones", icon: MapPinned, mobilePrimary: false, description: "Découpage géographique et suivi des zones" },
    { nom: "Finances", shortNom: "Finances", route: "/chef-projet/finances", icon: Wallet, mobilePrimary: false, description: "Suivi budgétaire et dépenses des projets" },
    { nom: "Rapports", shortNom: "Rapports", route: "/chef-projet/rapports", icon: BarChart3, mobilePrimary: false, description: "Rapports d'impact et synthèses périodiques" },
  ],

  "Responsable Finance": [
    { nom: "Tableau de bord", shortNom: "Accueil", route: "/finance/dashboard", icon: LayoutDashboard, mobilePrimary: true, description: "Indicateurs financiers et soldes en temps réel" },
    { nom: "Budgets", shortNom: "Budgets", route: "/finance/budgets", icon: Wallet, mobilePrimary: true, description: "Gestion prévisionnelle et exécution budgétaire" },
    { nom: "Financements", shortNom: "Financements", route: "/finance/financements", icon: Landmark, mobilePrimary: true, description: "Fonds alloués par les bailleurs de fonds" },
    { nom: "Dons", shortNom: "Dons", route: "/finance/dons", icon: Banknote, mobilePrimary: true, description: "Collecte des dons et traçabilité" },
    { nom: "Dépenses", shortNom: "Dépenses", route: "/finance/depenses", icon: Receipt, mobilePrimary: false, description: "Engagements et décaissements validés" },
    { nom: "Lignes budgétaires", shortNom: "Lignes", route: "/finance/lignes-budgetaires", icon: ClipboardList, mobilePrimary: false, description: "Ventilation fine des lignes de dépense" },
    { nom: "Justificatifs", shortNom: "Justifs", route: "/finance/justificatifs", icon: ClipboardList, mobilePrimary: false, description: "Pièces comptables et factures jointes" },
    { nom: "Rapports financiers", shortNom: "Rapports", route: "/finance/rapports", icon: BarChart3, mobilePrimary: false, description: "États financiers et synthèses d'audit" },
  ],

  "Gérant": [
    { nom: "Tableau de bord", shortNom: "Accueil", route: "/gerant/dashboard", icon: LayoutDashboard, mobilePrimary: true, description: "Vue globale à 360° sur toute votre ONG" },
    { nom: "Projets", shortNom: "Projets", route: "/gerant/projets", icon: FolderKanban, mobilePrimary: true, description: "Supervision du portefeuille de projets" },
    { nom: "Finances", shortNom: "Finances", route: "/gerant/finances", icon: Wallet, mobilePrimary: true, description: "Trésorerie, flux financiers et rentabilité" },
    { nom: "Assistant IA", shortNom: "IA", route: "/gerant/assistant", icon: Sparkles, mobilePrimary: true, description: "Assistant IA exécutif et aide à la décision" },
    { nom: "Mon ONG", shortNom: "Mon ONG", route: "/gerant/mon-ong", icon: Building2, mobilePrimary: false, description: "Informations officielles et profil ONG" },
    { nom: "Utilisateurs", shortNom: "Équipe", route: "/gerant/utilisateurs", icon: Users, mobilePrimary: false, description: "Gestion des membres et des collaborateurs" },
    { nom: "Partenaires", shortNom: "Partenaires", route: "/gerant/partenaires", icon: Handshake, mobilePrimary: false, description: "Partenaires opérationnels et relais" },
    { nom: "Bailleurs", shortNom: "Bailleurs", route: "/gerant/bailleurs", icon: Landmark, mobilePrimary: false, description: "Bailleurs de fonds et donateurs majeurs" },
    { nom: "Rapports", shortNom: "Rapports", route: "/gerant/rapports", icon: BarChart3, mobilePrimary: false, description: "Bilans globaux et rapports d'activité" },
  ],

  "Agent de terrain": [
    { nom: "Tableau de bord", shortNom: "Accueil", route: "/agent/dashboard", icon: LayoutDashboard, mobilePrimary: true, description: "Vos tâches, objectifs et métriques du jour" },
    { nom: "Mes campagnes", shortNom: "Campagnes", route: "/agent/campagnes", icon: FolderKanban, mobilePrimary: true, description: "Campagnes actives affectées sur le terrain" },
    { nom: "Mes zones", shortNom: "Zones", route: "/agent/zones", icon: MapPinned, mobilePrimary: true, description: "Secteurs géographiques d'intervention" },
    { nom: "Bénéficiaires", shortNom: "Bénéficiaires", route: "/agent/beneficiaires", icon: Users, mobilePrimary: true, description: "Fiches et enregistrement des bénéficiaires" },
    { nom: "Synchronisation", shortNom: "Sync", route: "/agent/synchronisation", icon: Smartphone, mobilePrimary: true, description: "Synchronisation des formulaires hors-ligne" },
  ],
};

export const getMenusForRole = (role) => {
  return menusConfig[role] || menusConfig["Chef de projet"];
};
