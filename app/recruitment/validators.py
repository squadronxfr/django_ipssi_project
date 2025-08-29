from __future__ import annotations

import os
from typing import Set

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@deconstructible
class DocumentUploadValidator:
    def __call__(self, file_obj) -> None:
        name = getattr(file_obj, "name", "")
        _, ext = os.path.splitext(name.lower())

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Extension de fichier non autorisée. Utilisez PDF, DOC ou DOCX.")

        size = getattr(file_obj, "size", None)
        if size is None:
            pos = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(pos)

        if size and size > MAX_FILE_SIZE_BYTES:
            raise ValidationError("Fichier trop volumineux (max 5 Mo).")


validate_document_file = DocumentUploadValidator()