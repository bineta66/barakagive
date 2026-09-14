from django.db import models


class Organization(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspendue"

    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=50, blank=True)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    address = models.CharField(max_length=255)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Sénégal")

    intervention_domain = models.CharField(max_length=150)

    logo = models.ImageField(
        upload_to="organizations/logos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name