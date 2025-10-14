# app/services/receipt_service.py
import os, hashlib, datetime, locale
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
import qrcode
from io import BytesIO

COMPROBANTES_DIR = os.getenv("COMPROBANTES_DIR", "storage/comprobantes")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "app/templates")
STATIC_DIR = os.getenv("STATIC_DIR", "app/static")

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _hash_pago(pago: dict) -> str:
    s = f"{pago.get('nbIdPago')}|{pago.get('txtMontoPagar')}|{pago.get('dFechaPago')}|{pago.get('txtUsuarioPaga')}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12].upper()

def _money(value) -> str:
    # Formato "es-EC" simple: 1.234,56
    try:
        n = float(value)
    except Exception:
        return str(value)
    entero, dec = f"{n:,.2f}".split(".")  # 1,234.56
    entero = entero.replace(",", ".")      # 1.234.56 -> 1.234
    return f"{entero},{dec}"

def _build_env():
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # filtro dinero
    env.filters["money"] = _money

    # helper para rutas estáticas
    def static_rel(path: str) -> str:
        # usado en el template como {{ static('css/receipt.css') }}
        return os.path.join(STATIC_DIR, path).replace("\\", "/")
    env.globals["static"] = static_rel
    return env

def _build_qr_png(tmp_dir: str, url: str) -> str:
    _ensure_dir(tmp_dir)
    img = qrcode.make(url)
    qr_path = os.path.join(tmp_dir, "qr.png")
    img.save(qr_path)
    return qr_path

def generar_comprobante_pdf_weasy(pago: dict, url_validacion: str | None = None, empresa_footer: str | None = None) -> str:
    """
    Genera el PDF del comprobante con WeasyPrint y retorna la ruta del archivo.
    """
    _ensure_dir(COMPROBANTES_DIR)
    env = _build_env()
    template = env.get_template("comprobante_pago.html")

    comprobante_id = f"CMP-{pago['nbIdPago']:06d}"
    hash_seg = _hash_pago(pago)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tmp_dir = os.path.join(COMPROBANTES_DIR, comprobante_id)
    _ensure_dir(tmp_dir)

    qr_png_path = None
    if url_validacion:
        qr_png_path = _build_qr_png(tmp_dir, url_validacion)

    html_str = template.render(
        pago=pago,
        hash_seg=hash_seg,
        now=now,
        qr_png_path=qr_png_path,
        empresa_footer=empresa_footer or "",
    )

    pdf_filename = f"{comprobante_id}.pdf"
    pdf_path = os.path.join(COMPROBANTES_DIR, pdf_filename)

    # WeasyPrint convierte HTML → PDF; base_url resuelve rutas absolutas de estáticos
    HTML(string=html_str, base_url=os.path.abspath(".")).write_pdf(pdf_path)

    return pdf_path
