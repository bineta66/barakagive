export function regionName(record, fallback = "Région non renseignée") {
  const region = record?.region
  const candidates = [
    record?.region_nom,
    record?.region_name,
    typeof region === "object" && region !== null ? region.nom : null,
    region,
  ]

  const label = candidates.find((value) => {
    if (typeof value !== "string" && typeof value !== "number") return false
    const label = String(value).trim()
    return label.length > 0 && !/^\d+$/.test(label)
  })
  if (label) return String(label).trim()
  return typeof fallback === "string" && fallback.trim() && !/^\d+$/.test(fallback.trim())
    ? fallback.trim()
    : "Région non renseignée"
}

export function regionId(record) {
  const region = record?.region
  return String(record?.region_id ?? (typeof region === "object" && region !== null ? region.id : region) ?? "")
}
