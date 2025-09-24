"""Rotas de consulta de perfis."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api_service.repositories.profiles import ProfileRepository
from api_service.schemas.profiles import PerfilDetalhado
from api_service.services.profiles import ProfileService

router = APIRouter(prefix="/profiles", tags=["Perfis"])


def obter_servico_perfis() -> ProfileService:
    """Instancia o serviço de perfis com repositório padrão."""

    return ProfileService(ProfileRepository(sessao=None, modelo_perfil=None))


@router.get(
    "/{username}",
    response_model=PerfilDetalhado,
    summary="Detalhar perfil",
)
def detalhar_perfil(
    username: str, servico: ProfileService = Depends(obter_servico_perfis)
) -> PerfilDetalhado:
    """Retorna as informações públicas de um perfil monitorado."""

    perfil = servico.obter_por_username(username)
    if perfil is None:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return perfil
