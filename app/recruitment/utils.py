from __future__ import annotations

import os
import uuid
from datetime import datetime
from django.utils.text import get_valid_filename


def _build_secure_filename(filename: str) -> str:
    base, ext = os.path.splitext(filename)
    ext = ext.lower()
    safe_base = get_valid_filename(base)[:80] or "file"
    unique = uuid.uuid4().hex
    return f"{safe_base}-{unique}{ext}"


def _build_user_date_path(instance, kind: str, filename: str) -> str:
    user = getattr(instance, "candidat", None)
    user_id = getattr(user, "id", None) or "anonymous"
    now = datetime.utcnow()
    safe_name = _build_secure_filename(filename)
    return os.path.join(
        "users",
        str(user_id),
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d"),
        kind,
        safe_name,
    )


def upload_to_cv(instance, filename: str) -> str:
    return _build_user_date_path(instance, "cv", os.path.basename(filename))


def upload_to_lettre(instance, filename: str) -> str:
    return _build_user_date_path(instance, "lettre", os.path.basename(filename))