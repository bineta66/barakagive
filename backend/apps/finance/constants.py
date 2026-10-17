"""Shared finance categories exposed by API serializers and the Vue forms."""

FINANCE_CATEGORIES = (
    ("Alimentation", "Alimentation"),
    ("Santé et médicaments", "Santé et médicaments"),
    ("Transport", "Transport"),
    ("Logistique", "Logistique"),
    ("Matériel et équipement", "Matériel et équipement"),
    ("Formation", "Formation"),
    ("Personnel", "Personnel"),
    ("Communication", "Communication"),
    ("Administration", "Administration"),
    ("Autre", "Autre"),
)

FINANCE_CATEGORY_VALUES = frozenset(value for value, _label in FINANCE_CATEGORIES)
