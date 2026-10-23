from pydantic import BaseModel, ConfigDict, Field


class UserProfileCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )
    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=15,
    )
    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )
    headline: str | None = Field(
        default=None,
        max_length=256,
    )
    links: dict[str, str] | None = None


class UserProfileUpdate(BaseModel):
    # model_config=model_dump(exclude_unset=True)
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )
    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=15,
    )
    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )
    headline: str | None = Field(
        default=None,
        max_length=256,
    )
    links: dict[str, str] | None = None
    


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    phone: str | None
    location: str | None
    headline: str | None
    links: dict[str, str] | None