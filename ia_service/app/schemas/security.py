from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class TrustedTenant(BaseModel):
    """Identity claims populated by Django after validating the user JWT."""

    model_config = ConfigDict(extra="forbid")

    organization_id: int | None
    user_id: int
    role: Literal["SUPER_ADMIN", "GERANT", "CHEF_PROJET", "FINANCE", "AGENT"]

    @model_validator(mode="after")
    def require_organization_for_regular_users(self):
        if self.role != "SUPER_ADMIN" and self.organization_id is None:
            raise ValueError("Une organisation est obligatoire pour ce rôle.")
        return self
