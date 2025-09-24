"""Serviços responsáveis por regras de negócio de perfis."""
from __future__ import annotations

from typing import Any, Dict, Optional

from api_service.repositories.profiles import ProfileRepository
from api_service.schemas.profiles import PerfilDetalhado


class ProfileService:
    """Orquestra acesso a dados e montagem do retorno de perfis."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def obter_por_username(self, username: str) -> Optional[PerfilDetalhado]:
        """Recupera o perfil solicitado convertendo para o esquema adequado."""

        registro = self._repository.buscar_por_username(username)
        if registro is None:
            return None

        return PerfilDetalhado(**self._converter_para_dict(registro))

    def _converter_para_dict(self, registro: Any) -> Dict[str, Any]:
        if isinstance(registro, dict):
            return registro

        dados: Dict[str, Any] = {}
        for campo in PerfilDetalhado.model_fields:
            if hasattr(registro, campo):
                dados[campo] = getattr(registro, campo)
        return dados
