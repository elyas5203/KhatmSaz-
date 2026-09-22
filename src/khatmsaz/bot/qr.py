"""In-memory QR generation for shareable bot invite links."""

from io import BytesIO

import qrcode


def build_qr_png(value: str) -> bytes:
    if not value.startswith(("https://", "http://")):
        raise ValueError("QR value must be an absolute web URL")
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(value)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
