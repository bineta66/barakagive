param(
    [string]$BaseUrl = "http://localhost:5173",
    [string]$ProjetId,
    [string]$ZoneId,
    [string]$CampagneId,
    [string]$BeneficiaireId,
    [string]$BudgetId,
    [string]$OrganisationId,
    [string]$OutputPath = (Join-Path $PSScriptRoot "..\HTML_TO_DESIGN_URLS.txt")
)

$base = $BaseUrl.TrimEnd('/')
$routes = [System.Collections.Generic.List[string]]::new()

# Pages publiques
@(
    "/", "/contact", "/connexion", "/mot-de-passe-oublie",
    "/activation-compte", "/inscription", "/reinitialisation"
) | ForEach-Object { $routes.Add($_) }

# Chef de projet
@(
    "/chef-projet/dashboard", "/chef-projet/projets", "/chef-projet/zones",
    "/chef-projet/zones/carte", "/chef-projet/zones/creer",
    "/chef-projet/zones/analyse-region/Dakar", "/chef-projet/campagnes",
    "/chef-projet/campagnes/creer", "/chef-projet/carte-priorites",
    "/chef-projet/finances", "/chef-projet/partenaires", "/chef-projet/bailleurs",
    "/chef-projet/rapports"
) | ForEach-Object { $routes.Add($_) }

# Agent
@(
    "/agent/dashboard", "/agent/campagnes", "/agent/zones",
    "/agent/beneficiaires", "/agent/synchronisation", "/agent/profil"
) | ForEach-Object { $routes.Add($_) }

# Responsable finance
@(
    "/finance/dashboard", "/finance/budgets", "/finance/lignes-budgetaires",
    "/finance/financements", "/finance/dons", "/finance/depenses",
    "/finance/justificatifs", "/finance/rapports"
) | ForEach-Object { $routes.Add($_) }

# Gerant
@(
    "/gerant/dashboard", "/gerant/mon-ong", "/gerant/projets",
    "/gerant/projets/creer", "/gerant/utilisateurs", "/gerant/utilisateurs/creer",
    "/gerant/partenaires", "/gerant/bailleurs", "/gerant/finances",
    "/gerant/rapports", "/gerant/assistant", "/gerant/payment",
    "/gerant/payment/subscribe", "/gerant/payment/expired", "/gerant/payment/history"
) | ForEach-Object { $routes.Add($_) }

# Super-admin
@(
    "/super-admin/dashboard", "/super-admin/demandes", "/super-admin/ongs",
    "/super-admin/gerants", "/super-admin/abonnements"
) | ForEach-Object { $routes.Add($_) }

# Pages de detail : ajoute-les uniquement si tu fournis de vrais identifiants.
if ($ProjetId) {
    $id = [uri]::EscapeDataString($ProjetId)
    $routes.Add("/chef-projet/projets/$id")
    $routes.Add("/gerant/projets/$id")
    $routes.Add("/gerant/projets/modifier/$id")
}
if ($ZoneId) {
    $id = [uri]::EscapeDataString($ZoneId)
    $routes.Add("/chef-projet/zones/$id")
    $routes.Add("/chef-projet/zones/modifier/$id")
    $routes.Add("/chef-projet/zones/analyse/$id")
    $routes.Add("/chef-projet/zones/$id/beneficiaires")
}
if ($CampagneId) {
    $id = [uri]::EscapeDataString($CampagneId)
    $routes.Add("/chef-projet/campagnes/$id")
    $routes.Add("/chef-projet/campagnes/$id/formulaire")
    $routes.Add("/chef-projet/campagnes/modifier/$id")
    $routes.Add("/agent/campagnes/$id/beneficiaires")
    $routes.Add("/agent/campagnes/$id/formulaire")
}
if ($BeneficiaireId) {
    $routes.Add("/agent/beneficiaires/$([uri]::EscapeDataString($BeneficiaireId))")
}
if ($BudgetId) {
    $routes.Add("/finance/budgets/$([uri]::EscapeDataString($BudgetId))")
}
if ($OrganisationId) {
    $routes.Add("/super-admin/organisations/$([uri]::EscapeDataString($OrganisationId))/verification")
}

$urls = $routes | Select-Object -Unique | ForEach-Object { "$base$_" }
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
$parent = Split-Path -Parent $resolvedOutput
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}
[System.IO.File]::WriteAllLines($resolvedOutput, $urls, [System.Text.UTF8Encoding]::new($false))

Write-Host "Liste creee : $resolvedOutput"
Write-Host "Nombre d'URL : $($urls.Count)"
Write-Host "Copie le contenu du fichier dans le champ URL de html.to.design."
Write-Host "Pour les pages protegees, connecte-toi d'abord dans le navigateur et capture-les avec l'extension html.to.design."
