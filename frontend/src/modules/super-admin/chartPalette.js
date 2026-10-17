export const SUPER_ADMIN_CHART_COLORS = Object.freeze({
  primary: "#16a34a",
  accent: "#f97316",
  blue: "#dc2626",
  success: "#16a34a",
  warning: "#eab308",
  purple: "#f97316",
  danger: "#dc2626",
});

export const SUPER_ADMIN_STATUS_COLORS = Object.freeze({
  organizations: Object.freeze({
    EN_ATTENTE: SUPER_ADMIN_CHART_COLORS.warning,
    ACTIVE: SUPER_ADMIN_CHART_COLORS.primary,
    REJETEE: SUPER_ADMIN_CHART_COLORS.danger,
    SUSPENDED: SUPER_ADMIN_CHART_COLORS.purple,
  }),
  projects: Object.freeze({
    NON_ARCHIVE: SUPER_ADMIN_CHART_COLORS.primary,
    ARCHIVE: SUPER_ADMIN_CHART_COLORS.purple,
  }),
  campaigns: Object.freeze({
    EN_COURS: SUPER_ADMIN_CHART_COLORS.primary,
    TERMINE: SUPER_ADMIN_CHART_COLORS.purple,
    PLANIFIER: SUPER_ADMIN_CHART_COLORS.warning,
    BROUILLON: SUPER_ADMIN_CHART_COLORS.warning,
    ANNULEE: SUPER_ADMIN_CHART_COLORS.danger,
  }),
});

export const withChartOpacity = (hex, opacity = 0.12) => {
  const value = hex.replace("#", "");
  const red = Number.parseInt(value.slice(0, 2), 16);
  const green = Number.parseInt(value.slice(2, 4), 16);
  const blue = Number.parseInt(value.slice(4, 6), 16);
  return `rgba(${red}, ${green}, ${blue}, ${opacity})`;
};
