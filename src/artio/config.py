"""Chargement de la configuration (config.yaml, privée et non versionnée)."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

DEFAULT_PATHS = (Path("config.yaml"), Path("config.local.yaml"))


def load_config(path: str | os.PathLike | None = None) -> dict:
    """Charge la configuration.

    Ordre de recherche : argument `path`, variable d'environnement ARTIO_CONFIG,
    puis config.yaml / config.local.yaml dans le dossier courant.
    """
    candidates = []
    if path:
        candidates.append(Path(path))
    if os.environ.get("ARTIO_CONFIG"):
        candidates.append(Path(os.environ["ARTIO_CONFIG"]))
    candidates.extend(DEFAULT_PATHS)

    for candidate in candidates:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}

    raise FileNotFoundError(
        "Aucune configuration trouvée. Copier config.example.yaml en config.yaml "
        "ou définir ARTIO_CONFIG."
    )
