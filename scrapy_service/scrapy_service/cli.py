"""Utilities for manual scraping runs and profile management."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES_FILE = PROJECT_ROOT / "profiles.json"


def _load_profiles(path: Path) -> List[Dict[str, Any]]:
    """Load a list of profiles from *path*.

    Returns an empty list when the file does not exist. Raises ``ValueError`` if the
    content is not a JSON array.
    """

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError(f"Esperado um array de perfis em {path}, mas foi encontrado {type(data).__name__}")

    normalised: List[Dict[str, Any]] = []
    for entry in data:
        if isinstance(entry, dict):
            normalised.append(entry)
        else:
            raise ValueError(
                "Cada perfil deve ser representado por um objeto JSON (dict), "
                f"mas foi encontrado {type(entry).__name__}"
            )
    return normalised


def _save_profiles(path: Path, profiles: Iterable[Dict[str, Any]]) -> None:
    """Persist profiles to disk using UTF-8 encoded JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(list(profiles), handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _parse_json_option(value: str | None, option_name: str) -> Dict[str, Any] | None:
    if value is None:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
        raise argparse.ArgumentTypeError(f"{option_name} deve ser um JSON válido: {exc}") from exc
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError(f"{option_name} deve ser um objeto JSON (dict)")
    return parsed


def command_add_profile(args: argparse.Namespace) -> None:
    """Adiciona ou atualiza um perfil no arquivo informado."""

    profiles_path = Path(args.profiles_file).expanduser().resolve()
    profiles = _load_profiles(profiles_path)

    profile: Dict[str, Any] = {
        "id": args.profile_id,
        "url": args.url,
    }
    if args.display_name:
        profile["display_name"] = args.display_name
    if args.wait_for_selector:
        profile["wait_for_selector"] = args.wait_for_selector
    if args.scroll_to_selector:
        profile["scroll_to_selector"] = args.scroll_to_selector
    if args.scroll_limit is not None:
        profile["scroll_limit"] = args.scroll_limit
    if args.scroll_delay is not None:
        profile["scroll_delay"] = args.scroll_delay

    api_headers = _parse_json_option(args.api_headers, "--api-headers")
    if api_headers:
        profile["api_headers"] = api_headers
    api_payload = _parse_json_option(args.api_payload, "--api-payload")
    if api_payload:
        profile["api_payload"] = api_payload
    if args.api_endpoint:
        profile["api_endpoint"] = args.api_endpoint

    updated = False
    for index, current in enumerate(profiles):
        current_id = str(current.get("id") or current.get("profile_id") or current.get("username"))
        if current_id == args.profile_id:
            profiles[index] = {**current, **profile}
            updated = True
            break
    if not updated:
        profiles.append(profile)

    _save_profiles(profiles_path, profiles)

    action = "Atualizado" if updated else "Adicionado"
    print(f"{action} perfil {args.profile_id} em {profiles_path}")


def _select_profiles(
    profiles: Iterable[Dict[str, Any]], targets: List[str] | None
) -> List[Dict[str, Any]]:
    if not targets:
        return [dict(profile) for profile in profiles]

    selected: List[Dict[str, Any]] = []
    target_set = {str(target) for target in targets}

    for profile in profiles:
        identifiers = {
            str(profile.get("id")),
            str(profile.get("profile_id")),
            str(profile.get("username")),
        }
        identifiers = {identifier for identifier in identifiers if identifier not in {"None", ""}}
        if identifiers & target_set:
            selected.append(dict(profile))

    missing = target_set - {str(p.get("id")) for p in selected} - {
        str(p.get("profile_id")) for p in selected
    } - {str(p.get("username")) for p in selected}
    if missing:
        raise SystemExit(f"Perfis não encontrados: {', '.join(sorted(missing))}")
    return selected


def command_run_profiles(args: argparse.Namespace) -> None:
    """Executa a spider de perfis utilizando o arquivo de configuração informado."""

    profiles_path = Path(args.profiles_file).expanduser().resolve()
    profiles = _load_profiles(profiles_path)
    selected_profiles = _select_profiles(profiles, args.profile_id)

    if not selected_profiles:
        raise SystemExit("Nenhum perfil encontrado para executar a raspagem.")

    for profile in selected_profiles:
        if args.scroll_limit is not None:
            profile["scroll_limit"] = args.scroll_limit
        if args.scroll_delay is not None:
            profile["scroll_delay"] = args.scroll_delay

    os.chdir(PROJECT_ROOT)

    from scrapy.cmdline import execute

    crawl_args = ["scrapy", "crawl", "profiles", "-a", f"profiles={json.dumps(selected_profiles, ensure_ascii=False)}"]

    if args.run_id:
        crawl_args.extend(["-s", f"RUN_ID={args.run_id}"])

    for setting in args.setting or []:
        crawl_args.extend(["-s", setting])

    execute(crawl_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Ferramentas auxiliares para executar a raspagem manualmente e gerenciar o "
            "arquivo de perfis monitorados."
        )
    )
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser(
        "add-profile", help="Adiciona ou atualiza um perfil no arquivo de perfis"
    )
    add_parser.add_argument("profile_id", help="Identificador único do perfil (ex.: username)")
    add_parser.add_argument("url", help="URL pública da timeline que será raspada")
    add_parser.add_argument(
        "--profiles-file",
        default=str(DEFAULT_PROFILES_FILE),
        help="Caminho para o arquivo JSON de perfis (padrão: %(default)s)",
    )
    add_parser.add_argument("--display-name", help="Nome de exibição opcional do perfil")
    add_parser.add_argument(
        "--wait-for-selector",
        help="CSS selector aguardado antes da extração (útil para garantir carregamento)",
    )
    add_parser.add_argument(
        "--scroll-to-selector",
        help="CSS selector utilizado para rolar até um elemento específico",
    )
    add_parser.add_argument(
        "--scroll-limit", type=int, help="Quantidade de ciclos de scroll executados na página"
    )
    add_parser.add_argument(
        "--scroll-delay", type=float, help="Intervalo (s) entre cada scroll da página"
    )
    add_parser.add_argument("--api-endpoint", help="Endpoint opcional para coleta via API interna")
    add_parser.add_argument(
        "--api-payload",
        help="Payload JSON enviado ao endpoint opcional (--api-endpoint)",
    )
    add_parser.add_argument(
        "--api-headers",
        help="Cabeçalhos JSON enviados ao endpoint opcional (--api-endpoint)",
    )
    add_parser.set_defaults(func=command_add_profile)

    run_parser = subparsers.add_parser(
        "run-profiles", help="Executa manualmente a spider de perfis"
    )
    run_parser.add_argument(
        "--profiles-file",
        default=str(DEFAULT_PROFILES_FILE),
        help="Caminho para o arquivo JSON de perfis (padrão: %(default)s)",
    )
    run_parser.add_argument(
        "--profile-id",
        action="append",
        help="Identificador do perfil a ser executado. Pode ser informado múltiplas vezes.",
    )
    run_parser.add_argument(
        "--scroll-limit", type=int, help="Sobrescreve scroll_limit para a execução atual"
    )
    run_parser.add_argument(
        "--scroll-delay", type=float, help="Sobrescreve scroll_delay para a execução atual"
    )
    run_parser.add_argument("--run-id", help="Identificador opcional para correlação de logs/metrics")
    run_parser.add_argument(
        "--setting",
        action="append",
        help="Parâmetros extras de configuração Scrapy no formato CHAVE=valor",
    )
    run_parser.set_defaults(func=command_run_profiles)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):  # pragma: no cover - argparse guarantees func
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
