from pydantic import BaseModel

## PET

class PetBase(BaseModel):
    name: str
    age: int
    description: str | None = None


class PetCreate(PetBase):
    pass

class Pet(PetBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

## USER

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    pets: list[Pet] = []

    class Config:
        orm_mode = True




