from fastapi import APIRouter, HTTPException
from app.services.nco_parser import parse_nc_html

from app.schemasFolder.extractor import ExtractRequest, ExtractedNCData
import requests

router = APIRouter(prefix="/extract", tags=["extract"])

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NC-Extractor/1.0; +https://example.local)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

@router.post("", response_model=ExtractedNCData)
def extract_from_url(body: ExtractRequest):
    try:
        resp = requests.get(body.url, headers=DEFAULT_HEADERS, timeout=20)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo conectar: {exc}")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="La URL no respondió 200 OK")

    html = resp.text
    try:
        data = parse_nc_html(html, str(body.url))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error parseando HTML: {exc}")

    # sanity check mínimo
    if not (data.codigo_necesidad or data.nombre_entidad or data.objeto_compra):
        # devolver igualmente, pero advertir
        # (opcional) podrías lanzar 422 si quieres forzar parse completo
        pass

    return data
