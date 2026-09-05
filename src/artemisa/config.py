"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    sql_echo: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_url=os.getenv(
                "ARTEMISA_DATABASE_URL",
                "mysql+pymysql://artemisa:change_me@localhost:3306/artemisa?charset=utf8mb4",
            ),
            sql_echo=_as_bool(os.getenv("ARTEMISA_SQL_ECHO", "false")),
        )

