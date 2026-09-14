from django.db import models
from django.conf import settings


class ProjectCriteria(models.Model):

    name = models.CharField(max_length=200, unique=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_criteria",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):

    name = models.CharField(max_length=200)

    code = models.CharField(max_length=30, unique=True, blank=True, editable=False)

    description = models.TextField()

    region = models.CharField(max_length=100)

    objectif = models.TextField()

    start_date = models.DateField()

    end_date = models.DateField()

    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    chef_projet = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects_as_chef",
    )

    responsable_finance = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects_as_finance",
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="projects",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    archived = models.BooleanField(default=False)

    criteria = models.ManyToManyField(
        ProjectCriteria,
        related_name="projects",
        blank=True,
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        from django.utils import timezone
        year = self.start_date.year if self.start_date else timezone.now().year
        region_prefix = self.region[:3].upper() if self.region else "XXX"
        count = Project.objects.filter(
            code__startswith=f"PRJ-{year}-{region_prefix}-"
        ).count()
        sequence = count + 1
        return f"PRJ-{year}-{region_prefix}-{sequence:03d}"
