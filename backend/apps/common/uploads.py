from pathlib import Path

from django.core.exceptions import ValidationError


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
FILE_SIGNATURES = {
    ".pdf": (b"%PDF-",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
}


def validate_document_upload(
    upload,
    *,
    extensions=(".pdf", ".jpg", ".jpeg", ".png"),
    max_size=MAX_DOCUMENT_SIZE,
):
    if upload.size > max_size:
        limit_mb = max_size // (1024 * 1024)
        raise ValidationError(f"La taille du fichier ne doit pas dépasser {limit_mb} Mo.")

    extension = Path(upload.name).suffix.lower()
    if extension not in extensions:
        raise ValidationError("Le fichier doit être au format PDF, JPG ou PNG.")

    position = upload.tell()
    try:
        header = upload.read(16)
    finally:
        upload.seek(position)
    signatures = FILE_SIGNATURES[extension]
    if not any(header.startswith(signature) for signature in signatures):
        raise ValidationError("Le contenu du fichier ne correspond pas à son extension.")
    return upload


def validate_pdf_upload(upload):
    return validate_document_upload(upload, extensions=(".pdf",), max_size=5 * 1024 * 1024)


def validate_image_upload(upload):
    return validate_document_upload(
        upload,
        extensions=(".jpg", ".jpeg", ".png"),
        max_size=5 * 1024 * 1024,
    )
