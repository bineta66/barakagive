export const CHART_COLORS = Object.freeze({
  green: '#16a34a',
  yellow: '#eab308',
  red: '#dc2626',
  orange: '#f97316',
})

const palette = Object.values(CHART_COLORS)

export function chartColor(label = '', index = 0) {
  const normalized = String(label)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()

  if (/priorit|depense|rejet|refus|retard|annul|overdue|deficit|echec/.test(normalized)) return CHART_COLORS.red
  if (/sorti|archive|suspend|cloture|campagne|termine/.test(normalized)) return CHART_COLORS.orange
  if (/attente|planifi|brouillon|restant|disponible|solde|don|warning/.test(normalized)) return CHART_COLORS.yellow
  if (/non\s*archive|pris en charge|aide|actif|approuve|valide|recu|realise|succes|en cours|financement/.test(normalized)) return CHART_COLORS.green

  return palette[Math.abs(index) % palette.length]
}

export function distinctChartColors(labels = []) {
  const used = new Set()
  return labels.map((label, index) => {
    let color = chartColor(label, index)
    if (used.has(color)) color = palette.find(candidate => !used.has(candidate)) || palette[index % palette.length]
    used.add(color)
    return color
  })
}
