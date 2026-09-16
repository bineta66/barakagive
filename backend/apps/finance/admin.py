from django.contrib import admin

from .models import Bailleur, Budget, Depense, Don, Justificatif, Partenaire, PosteBudgetaire


admin.site.register([Bailleur, Partenaire, Don, Budget, PosteBudgetaire, Depense, Justificatif])
