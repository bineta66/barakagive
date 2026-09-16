import os, re

ROOT = "C:/Users/dell/Desktop/barakagive/frontend/src"

# Known corrupted -> replacement mapping (contextual, applied per line)
REPLACEMENTS = [
    ("�?� Retour à la connexion", "Retour à la connexion"),
    ("�Y\"' Transmission chiffrée de bout en bout", "🔒 Transmission chiffrée de bout en bout"),
    ("�?VOLUTION DES PROJETS ET B�?N�?FICIAIRES", "EVOLUTION DES PROJETS ET BENEFICIAIRES"),
    ("TRAJECTOIRE BUDG�?TAIRE ET D�?PENSES", "TRAJECTOIRE BUDGETAIRE ET DEPENSES"),
    ("�o.", "etc."),
    ("{{ item.beneficiary?.telephone || '�?\"' }}", "{{ item.beneficiary?.telephone || '-' }}"),
    ("�?� Retour aux bénéficiaires", "Retour aux bénéficiaires"),
    ("R�\"LE OP�?RATIONNEL", "ROLE OPERATIONNEL"),
    ("{{ p.region || '�?\"' }}", "{{ p.region || '-' }}"),
    ("{{ p.start_date || '�?\"' }} au {{ p.end_date || '�?\"' }}", "{{ p.start_date || '-' }} au {{ p.end_date || '-' }}"),
    ("�-", "×"),
    ("En-t�fªte", "En-tête"),
    ("G�f©rez les organisations partenaires", "Gérez les organisations partenaires"),
    ("Gérer les membres �?'", "Gérer les membres"),
    ("Voir tous les projets �?'", "Voir tous les projets"),
    ("{{ proj.start_date }} �?' {{ proj.end_date }}", "{{ proj.start_date }} au {{ proj.end_date }}"),
    ("ZONE DE D�?PLOIEMENT", "ZONE DE DEPLOIEMENT"),
    ("STATUT OP�?RATIONNEL", "STATUT OPERATIONNEL"),
    ("�Stes-vous sûr de vouloir supprimer cette campagne ?", "Êtes-vous sûr de vouloir supprimer cette campagne ?"),
    ("FINANCEMENT ENGAG�?", "FINANCEMENT ENGAGÉ"),
    ("if (str.includes('�,�') || str.toLowerCase().includes('eur'))", "if (str.includes('€') || str.toLowerCase().includes('eur'))"),
    ("'Critique' : (zone.scoreIA || 0) >= 50 ? '�?levé' : 'Normal'", "'Critique' : (zone.scoreIA || 0) >= 50 ? 'Élevé' : 'Normal'"),
    ("<!-- Bouton �?valuer -->", "<!-- Bouton Évaluer -->"),
    ("�?valuer", "Évaluer"),
    ("Analyse IA �?\" {{ selectedRegion || 'Toutes les régions' }}", "Analyse IA - {{ selectedRegion || 'Toutes les régions' }}"),
    ("FLUX EN DIRECT // S�?N�?GAL OP�?RATIONS", "FLUX EN DIRECT // SENEGAL OPERATIONS"),
    ("�?levés", "Élevés"),
    ("<option value=\"�?levé\">�?levé</option>", "<option value=\"Élevé\">Élevé</option>"),
    ("Cr�f©ez un nouveau partenaire", "Créez un nouveau partenaire"),
    ("placeholder=\"Croissant-Rouge Sah�f©lien, MSF...\"", "placeholder=\"Croissant-Rouge Sahélien, MSF...\""),
    ("placeholder=\"Secours, Sant�f©, Eau...\"", "placeholder=\"Secours, Santé, Eau...\""),
    ("placeholder=\"Dakar, Thi�f¨s, Kaolack...\"", "placeholder=\"Dakar, Thiès, Kaolack...\""),
    ("Projet associ�f©", "Projet associé"),
    ("�? budgétiser", "À budgétiser"),
    ("S�lectionner un don", "Sélectionner un don"),
    ("Voir toutes les ONG �?'", "Voir toutes les ONG"),
]

def clean_text(text):
    for bad, good in REPLACEMENTS:
        text = text.replace(bad, good)
    return text

changed = []
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith(".vue"):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            original = f.read()
        cleaned = clean_text(original)
        if cleaned != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            changed.append(path)

print("Changed files:", len(changed))
for c in changed:
    print(" -", c.replace("C:/Users/dell/Desktop/barakagive/frontend/src/", ""))