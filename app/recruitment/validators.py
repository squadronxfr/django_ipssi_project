"""
Validateurs de fichiers pour l'app recruitment.

- Extension autorisée: .pdf, .doc, .docx
- Taille maximale: 5 Mo
- Scan basique de contenu pour bloquer certains fichiers malveillants évidents.

Note: Ce scan ne remplace pas un antivirus. Pour la production, utiliser un
service spécialisé (ex: ClamAV, services AV API) pour analyser les fichiers.
"""
from __future__ import annotations

import os
import re
from typing import Iterable

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

ALLOWED_EXTENSIONS: Iterable[str] = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# Signatures/motifs simples
PDF_MAGIC = b"%PDF"
DOCX_MAGIC = b"PK\x03\x04"  # zip header
DOC_MAGIC = b"\xD0\xCF\x11\xE0"  # OLE Compound File (legacy .doc)
EXE_MAGIC = b"MZ"  # executable PE header -> devrait être bloqué

JS_PATTERNS = [
    br"<script[\s>]",
    br"/JavaScript",
    br"/JS\b",
]
SHEBANG_PATTERNS = [
    br"^#!/bin/bash",
    br"^#!/usr/bin/env bash",
    br"^#!/usr/bin/env python",
    br"^#!/bin/sh",
]


@deconstructible
class DocumentUploadValidator:
    """Validateur pour documents CV/lettre.

    Utilisable dans validators=[DocumentUploadValidator()].
    """

    def __call__(self, file_obj) -> None:
        # 1) Vérifier extension
        name = getattr(file_obj, "name", "")
        _, ext = os.path.splitext(name.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Extension de fichier non autorisée. Utilisez PDF, DOC ou DOCX.")

        # 2) Taille maximale
        size = getattr(file_obj, "size", None)
        if size is None:
            # Essayer de lire pour estimer
            pos = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(pos)
        if size and size > MAX_FILE_SIZE_BYTES:
            raise ValidationError("Fichier trop volumineux (max 5 Mo).")

        # 3) Scan basique
        # Lire un échantillon du début + éventuellement tout si petit
        head_len = 64 * 1024  # 64KB
        pos = file_obj.tell()
        try:
            file_obj.seek(0)
            head = file_obj.read(head_len)
        finally:
            file_obj.seek(pos)

        if not isinstance(head, (bytes, bytearray)):
            try:
                head = bytes(head)
            except Exception:
                head = b""

        # Bloquer les exécutables évidents
        if head.startswith(EXE_MAGIC):
            raise ValidationError("Type de fichier non autorisé.")

        # Vérifier les signatures de type attendues
        if ext == ".pdf":
            if not head.startswith(PDF_MAGIC):
                raise ValidationError("Le fichier PDF semble invalide.")
            # Détecter présence de JavaScript intégré
            for pat in JS_PATTERNS:
                if re.search(pat, head, flags=re.IGNORECASE):
                    raise ValidationError("PDF contenant du JavaScript potentiellement dangereux.")
        elif ext == ".docx":
            if not head.startswith(DOCX_MAGIC):
                # Certains .docx peuvent avoir un en-tête zip différent (PK..), on reste strict ici
                raise ValidationError("Le fichier DOCX semble invalide.")
        elif ext == ".doc":
            if not head.startswith(DOC_MAGIC):
                raise ValidationError("Le fichier DOC (ancien format) semble invalide.")

        # Bloquer des contenus script évidents en début de fichier
        for pat in SHEBANG_PATTERNS:
            if re.search(pat, head):
                raise ValidationError("Fichier potentiellement script détecté.")


# Instance réutilisable
validate_document_file = DocumentUploadValidator()