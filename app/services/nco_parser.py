import re
from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.schemasFolder.extractor import Attachment, ExtractedNCData, ItemExtraido


def _clean_text(x: Optional[str]) -> Optional[str]:
    if x is None:
        return None
    return re.sub(r"\s+", " ", x).strip()

def _find_strong_following_text(soup: BeautifulSoup, label: str) -> Optional[str]:
    """
    Busca <strong>LABEL:</strong> y devuelve el texto inmediatamente después
    (en el mismo contenedor o en el siguiente <p class="card-text">).
    """
    # Coincidir por texto (ignorando acentos HTML entities)
    strong_tags = soup.find_all("strong")
    wanted = None
    for st in strong_tags:
        txt = st.get_text(separator=" ", strip=True)
        if txt.lower().startswith(label.lower()):
            wanted = st
            break
    if not wanted:
        return None

    # 1) Texto inmediatamente después del <strong> (en el mismo nodo)
    # ejemplo: <strong>Nombre Entidad: </strong>GAD X
    tail = wanted.next_sibling
    if tail and isinstance(tail, str):
        val = _clean_text(tail)
        if val:
            return val

    # 2) Algunos campos están en <p class="card-text"> justo después
    p = wanted.find_next("p", class_="card-text")
    if p:
        return _clean_text(p.get_text())

    # 3) Sino, recoger todo el texto del contenedor padre
    parent_text = wanted.parent.get_text(" ", strip=True)
    # quitar el label del inicio
    val = parent_text.replace(wanted.get_text(strip=True), "")
    return _clean_text(val)

def _parse_attachments(soup: BeautifulSoup, base_url: str) -> List[Attachment]:
    out: List[Attachment] = []
    # La tabla de anexos tiene <table id="rounded-corner"> ... <a href="../GE/ExeGENBajarArchivoGeneral.cpe?...">
    for tbl in soup.find_all("table"):
        # Buscar filas con enlace de descarga (img bajar.gif o <a href=...>)
        links = tbl.find_all("a", href=True)
        for a in links:
            href = a["href"].strip()
            if "ExeGENBajarArchivoGeneral" in href:
                # título puede estar en la celda de la izquierda (mismo <tr>)
                tr = a.find_parent("tr")
                title = "Documento"
                if tr:
                    tds = tr.find_all("td")
                    if tds:
                        title = _clean_text(tds[0].get_text()) or title
                out.append(Attachment(
                    title=title,
                    download_url=urljoin(base_url, href)
                ))
    return out

def parse_nc_html(html: str, base_url: str) -> ExtractedNCData:
    soup = BeautifulSoup(html, "lxml")

    # Algunos valores tienen dos responsables en el mismo campo
    funcionario_nombre = _find_strong_following_text(soup, "Nombre:")
    funcionario_correo = _find_strong_following_text(soup, "Correo Electrónico:")

    data = ExtractedNCData(
        raw_title=_clean_text(soup.title.get_text() if soup.title else None),
        nombre_entidad=_find_strong_following_text(soup, "Nombre Entidad:"),
        tipo_necesidad=_find_strong_following_text(soup, "Tipo de necesidad:"),
        codigo_necesidad=_find_strong_following_text(soup, "Código Necesidad de Contratación:"),
        estado_necesidad=_find_strong_following_text(soup, "Estado de la necesidad:"),
        objeto_compra=_find_strong_following_text(soup, "Objeto de compra:"),
        fecha_publicacion=_find_strong_following_text(soup, "Fecha de Publicación de la Necesidad:"),
        fecha_limite=_find_strong_following_text(soup, "Fecha Límite para la entrega de Proformas:"),
        funcionario_nombre=_clean_text(funcionario_nombre),
        funcionario_correo=_clean_text(funcionario_correo),
        lugar_provincia=_find_strong_following_text(soup, "Provincia:"),
        lugar_canton=_find_strong_following_text(soup, "Cantón:"),
        lugar_parroquia=_find_strong_following_text(soup, "Parroquia:"),
        lugar_direccion=_find_strong_following_text(soup, "Dirección:"),
        anexos=_parse_attachments(soup, base_url)
    )

    # Normalizaciones rápidas (quitar “En Curso ” extra o espacios)
    if data.estado_necesidad:
        data.estado_necesidad = data.estado_necesidad.replace(":", "").strip()
    data.items = _parse_items_table(soup)
    return data


def _parse_items_table(soup: BeautifulSoup) -> List[ItemExtraido]:
    tabla_items = None
    for h2 in soup.find_all("h2"):
        if "detalle del objeto de compra" in h2.get_text(strip=True).lower():
            # La tabla suele estar justo después
            tabla_items = h2.find_next("table")
            break

    if not tabla_items:
        return []

    filas = tabla_items.find_all("tr")
    items: List[ItemExtraido] = []

    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) < 6:
            continue  # saltar filas incompletas

        try:
            cpc = celdas[1].get_text(strip=True)
            descripcion_corta = celdas[2].get_text(strip=True)
            descripcion_larga = celdas[3].get_text(strip=True)
            unidad = celdas[4].get_text(strip=True)
            cantidad = celdas[5].get_text(strip=True)

            items.append(ItemExtraido(
                cpc=cpc,
                descripcion_corta=descripcion_corta,
                descripcion_larga=descripcion_larga,
                unidad=unidad,
                cantidad=cantidad
            ))
        except Exception as e:
            print(f"⚠️ Error parseando fila de ítem: {e}")
            continue

    return items