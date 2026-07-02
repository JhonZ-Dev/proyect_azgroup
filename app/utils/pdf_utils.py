from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import re

def limpiar_texto(texto):
    """Elimina caracteres no imprimibles y reemplaza saltos de línea por espacio."""
    if not isinstance(texto, str):
        texto = str(texto)
    # Solo eliminamos caracteres de control, pero permitimos tildes y ñ (rango \u00C0-\u017F)
    texto = re.sub(r'[^\x20-\x7E\s\u00C0-\u017F]', '', texto)
    texto = texto.replace('\n', ' ').replace('\r', '')
    return texto
def format_decimal(num, decimales=3):
    """
    Devuelve el número en formato ecuatoriano: separador miles punto, decimales coma, siempre con 'decimales' decimales.
    - Si num es float: lo usa directo.
    - Si num es string: reemplaza ',' por '.' si es necesario.
    Ej: 2288 => '2.288,000', 8.5 => '8,500', '0,75' => '0,750'
    """
    if num is None or num == "":
        return ""
    try:
        if isinstance(num, str):
            num = num.replace(",", ".")  # Por si viene como texto "0,75"
        num = float(num)
        # Separador miles punto, decimales coma
        formatted = f"{num:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
    except Exception:
        return str(num)


def generar_pdf_proforma(
    data: dict,
    archivo_salida: str = None,
    membrete_path: str = None,
    full_name: str = None,
    job_title: str = None,
    ruc: str = None
) -> str:
    """
    Genera un PDF de proforma por secciones (cada una con sus proporciones de columnas),
    sin espacios entre secciones y con líneas negras consistentes.
    """
    # === LAYOUT GLOBAL ===
    ancho_hoja, alto_hoja = A4
    margen_izq = 1.5 * cm
    margen_der = 1.5 * cm
    margen_sup = 3 * cm
    margen_inf = 3 * cm
    ancho_util = ancho_hoja - margen_izq - margen_der

    # === PROPORCIONES POR SECCIÓN (ajústalas libremente) ===
    props_header = [1.0]                    # Cabecera PROFORMA
    props_generales = [0.22, 0.78]          # Datos generales (Etiqueta, Valor)
    props_objeto_title = [1.0]              # Título OBJETO DE COMPRA
    props_objeto_body  = [1.0]              # Respuesta OBJETO DE COMPRA
    #props_items = [0.10, 0.14, 0.10, 0.36, 0.10, 0.10, 0.10]  # Ítems
    # Ítems (No., CPC, UNIDAD, ESPECIFICACIONES, CANTIDAD, P. UNIT, P. TOTAL)
    props_items = [0.06, 0.12, 0.10, 0.38, 0.12, 0.11, 0.11]

    props_leyenda = [1.0]                   # Leyenda RIMPE
    props_campos_finales = [0.28, 0.72]     # Campos finales (Etiqueta, Valor)

    # === ESTILOS ===
    styles = getSampleStyleSheet()
    styleN = styles['Normal']

    style_rojo_centrado = ParagraphStyle(
        'RojoCentrado', parent=styles['Normal'],
        alignment=1, fontSize=10, textColor=colors.red, fontName='Helvetica-Bold'
    )
    style_rojo_necesidad = ParagraphStyle(
        'RojoCentrado', parent=styles['Normal'],
        alignment=0, fontSize=10, textColor=colors.red, fontName='Helvetica-Bold'
    )
    style_bold = ParagraphStyle(
        'Negrita', parent=styles['Normal'],
        alignment=0, fontSize=10, textColor=colors.black, fontName='Helvetica-Bold'
    )
    style_bold_izquierda = ParagraphStyle(
        'NegritaIzquierda', parent=styles['Normal'],
        alignment=0, fontSize=10, textColor=colors.black, fontName='Helvetica-Bold'
    )
    style_bold_centrado = ParagraphStyle(
        'NegritaCentrado', parent=styles['Normal'],
        alignment=1, fontSize=10, textColor=colors.black, fontName='Helvetica-Bold'
    )
    style_longtext = ParagraphStyle(
        'LongText', parent=styleN, wordWrap='CJK', fontSize=9
    )
    style_heading_cell = ParagraphStyle(
        'HeadingCell', parent=styles['Heading4'],
        alignment=1, fontName='Helvetica-Bold', fontSize=10
    )
    style_centrado = ParagraphStyle(
    'Centrado', parent=styles['Normal'],
    alignment=1, fontSize=10, fontName='Helvetica'
)

    # === NOMBRE DE ARCHIVO ===
    necesidad = (data.get("txt_necesidad", "proforma") or "proforma").replace(" ", "_")
    archivo_salida = archivo_salida or f"proforma_{necesidad}.pdf"

    # === Helper: construir Table sin espacios externos y paddings internos mínimos ===
    def _table(data_rows, props, style_cmds=None, font_size=None, grid=True, hpad=4, vpad=1):
        col_widths = [ancho_util * p for p in props]
        t = Table(data_rows, colWidths=col_widths)
        # Sin separación externa entre tablas
        t.spaceBefore = 0
        t.spaceAfter  = 0

        cmds = []
        if grid:
            # GRID en negro
            cmds.append(('GRID', (0,0), (-1,-1), 0.4, colors.black))
        cmds.append(('VALIGN', (0,0), (-1,-1), 'MIDDLE'))
        # Paddings internos compactos
        cmds += [
            ('LEFTPADDING',  (0,0), (-1,-1), hpad),
            ('RIGHTPADDING', (0,0), (-1,-1), hpad),
            ('TOPPADDING',   (0,0), (-1,-1), vpad),
            ('BOTTOMPADDING',(0,0), (-1,-1), vpad),
        ]
        if font_size:
            cmds.append(('FONTSIZE', (0,0), (-1,-1), font_size))
        if style_cmds:
            # Asegúrate de que LINEABOVE/LINEBELOW vayan DESPUÉS del GRID si quieres sobrescribir bordes
            cmds.extend(style_cmds)
        t.setStyle(TableStyle(cmds))
        return t

    # ===== SECCIÓN 1: CABECERA PROFORMA =====
    txt_infimaNro = data.get("txt_numeroProforma", "")
    solo_numero = txt_infimaNro.split('-')[-1] if txt_infimaNro else ""
    header_rows = [[
        Paragraph(f'<b>PROFORMA <font color="red">{solo_numero}</font></b>', style_heading_cell)
    ]]
    header_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DAE9F7')),
        ('LEFTPADDING',  (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        # Esta tabla pone la línea inferior NEGRA para el borde con la siguiente sección
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
    ]
    tbl_header = _table(header_rows, props_header, header_style, font_size=10)

    # ===== SECCIÓN 2: DATOS GENERALES =====
    generales_pairs = [
        ('CLIENTE',   Paragraph(limpiar_texto(data.get("txt_cliente", "")), style_bold)),
        ('RUC',       Paragraph(limpiar_texto(data.get("txt_ruc", "")), style_bold)),
        ('DIRECCIÓN', Paragraph(limpiar_texto(data.get("txt_direccion", "")), style_bold)),
        ('FECHA',     Paragraph(limpiar_texto(data.get("txt_fecha", "")), style_bold)),
        ('TELÉFONO',  Paragraph(limpiar_texto(data.get("txt_telefono", "")), style_bold)),
        ('NECESIDAD', Paragraph(limpiar_texto(data.get("txt_necesidad", "")), style_rojo_necesidad)),
        ('FUNCIONARIO ENCARGADO', Paragraph(limpiar_texto(data.get("txt_funcionario", "")), style_bold)),
        ('CORREO',    Paragraph(limpiar_texto(data.get("txt_correo", "")), style_bold)),
        ('HORA MÁXIMA', Paragraph(limpiar_texto(data.get("tHora_maxina", "")), style_bold)),
    ]
    generales_rows = []
    for etq, val in generales_pairs:
        generales_rows.append([
            Paragraph(f'<b>{etq}</b>', style_bold_izquierda),
            val
        ])
    generales_style = [
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#DAE9F7')),
        # Como la línea inferior de la tabla anterior ya es negra,
        # quitamos la superior aquí para evitar doble trazo.
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
        # Esta tabla dibuja su línea inferior NEGRA para la siguiente sección
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
    ]
    tbl_generales = _table(generales_rows, props_generales, generales_style, font_size=10)

    # ===== SECCIÓN 3: OBJETO DE COMPRA =====
    objeto_title_rows = [[Paragraph('<b>OBJETO DE COMPRA</b>', style_bold_centrado)]]
    objeto_title_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DAE9F7')),
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),           # sin línea superior (ya la puso la anterior)
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),       # inferior negra
    ]
    tbl_objeto_title = _table(objeto_title_rows, props_objeto_title, objeto_title_style, font_size=10)

    objeto_body_rows = [[Paragraph(limpiar_texto(data.get("txt_objetivoCompra", "")), style_bold_centrado)]]
    objeto_body_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E0E0E0')),
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
    ]
    tbl_objeto_body = _table(objeto_body_rows, props_objeto_body, objeto_body_style, font_size=10)

    # ===== SECCIÓN 4: TABLA DE ÍTEMS =====
    # Header de ítems
    items_header = [[
        Paragraph('<b>No.</b>', styleN),
        Paragraph('<b>CPC</b>', styleN),
        Paragraph('<b>UNIDAD</b>', styleN),
        Paragraph('<b>ESPECIFICACIONES</b>', styleN),
        Paragraph('<b>CANTIDAD</b>', styleN),
        Paragraph('<b>P. UNIT</b>', styleN),
        Paragraph('<b>P. TOTAL</b>', styleN),
    ]]
    items_header_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DAE9F7')),
        ('FONTSIZE', (0,0), (0,0), 8),  # "No." pequeñito
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
    ]
    tbl_items_header = _table(items_header, props_items, items_header_style, font_size=10)

    # Cuerpo de ítems
    items = data.get("items", []) or []
    item_rows = []
    for idx, item in enumerate(items, 1):
        precio_unit = item.get("flo_precioUnitario", "")
        precio_total = item.get("flo_precioTotal", "")
        item_rows.append([
            limpiar_texto(idx),
            limpiar_texto(item.get("txt_cpc", "")),
            limpiar_texto(item.get("txt_unidad", "")),
            Paragraph(limpiar_texto(item.get("txt_especificaciones", "")), style_longtext),
            Paragraph(limpiar_texto(item.get("int_cantidad", "")), style_centrado),  # Centrado
            Paragraph(f"${format_decimal(precio_unit, 3)}" if precio_unit not in ("", None) else "", style_centrado),  # Centrado
            Paragraph(f"${format_decimal(precio_total, 2)}" if precio_total not in ("", None) else "", style_centrado), # Centrado
           
        ])
    body_style = [
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
    ]
    tbl_items_body = _table(item_rows, props_items, body_style, font_size=9) if item_rows else _table([], props_items, body_style, font_size=9)

    # Total y Leyenda
    items = data.get("items", []) or []
    
    is_jhon = False
    usuario_registra = str(data.get("txtUsuarioRegistra", "")).lower()
    formato = str(data.get("txtFormato", "antiguo")).lower()
    if "jhon" in usuario_registra and formato == "nuevo":
        is_jhon = True

    if is_jhon:
        subtotal_0 = 0.0
        subtotal_15 = 0.0
        iva_15 = 0.0
        
        for it in items:
            porcentaje = float(it.get('flo_iva_porcentaje') or 0.0)
            subtotal = float(it.get('flo_precioTotal', 0) or 0)
            
            if porcentaje == 15.0 or porcentaje == 15:
                subtotal_15 += subtotal
                iva_15 += float(it.get('flo_iva_valor') or (subtotal * 0.15))
            else:
                subtotal_0 += subtotal
                
        total_final = subtotal_0 + subtotal_15 + iva_15
        
        total_row = [
            [Paragraph('<b>SUBTOTAL 0%</b>', style_bold_centrado), '', '', '', '', '', Paragraph(f'<b>${format_decimal(subtotal_0, 2)}</b>', style_bold_centrado)],
            [Paragraph('<b>SUBTOTAL 15%</b>', style_bold_centrado), '', '', '', '', '', Paragraph(f'<b>${format_decimal(subtotal_15, 2)}</b>', style_bold_centrado)],
            [Paragraph('<b>IVA 15%</b>', style_bold_centrado), '', '', '', '', '', Paragraph(f'<b>${format_decimal(iva_15, 2)}</b>', style_bold_centrado)],
            [Paragraph('<b>TOTAL</b>', style_bold_centrado), '', '', '', '', '', Paragraph(f'<b>${format_decimal(total_final, 2)}</b>', style_bold_centrado)]
        ]
        
        total_style = [
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#DAE9F7')),
            ('SPAN', (0,0), (5,0)),
            ('SPAN', (0,1), (5,1)),
            ('SPAN', (0,2), (5,2)),
            ('SPAN', (0,3), (5,3)),
            ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
            # Lineas intermedias sutiles para los subtotales
            ('LINEBELOW', (0,0), (-1,0), 0.2, colors.gray),
            ('LINEBELOW', (0,1), (-1,1), 0.2, colors.gray),
            ('LINEBELOW', (0,2), (-1,2), 0.2, colors.gray),
        ]
        leyenda_text = 'SOMOS REGIMEN RIMPE - EMPRENDEDOR'
    else:
        total = sum(float(item.get("flo_precioTotal", 0) or 0) for item in items)
        total_row = [[
            Paragraph('<b>TOTAL</b>', style_bold_centrado), '', '', '', '', '',
            Paragraph(f'<b>${format_decimal(total, 2)}</b>', style_bold_centrado)
        ]]
        total_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DAE9F7')),
            ('SPAN', (0,0), (5,0)),  # "TOTAL" ocupa columnas 0-5
            ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
        ]
        leyenda_text = 'NO GRAVAMOS IVA - SOMOS REGIMEN RIMPE - NEGOCIO POPULAR'

    tbl_items_total = _table(total_row, props_items, total_style, font_size=10)

    # ===== SECCIÓN 5: LEYENDA RIMPE =====
    leyenda_rows = [[
        Paragraph(leyenda_text, style_rojo_centrado)
    ]]
    leyenda_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.white),
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.black),
    ]
    tbl_leyenda = _table(leyenda_rows, props_leyenda, leyenda_style, font_size=10)

    # ===== SECCIÓN 6: CAMPOS FINALES (2 columnas) =====
    nuevos_campos = [
        ('PLAZO DE ENTREGA',          data.get('txt_plazoEntrega', '')),
        ('VIGENCIA DE LA OFERTA',     data.get('txt_vigenciaOferta', '')),
        ('FORMA DE PAGO',             data.get('txt_formaPago', '')),
        ('METODOLOGIA DE TRABAJO',    data.get('txt_metodologiaTrabajo', '')),
        ('GARANTIA',                  data.get('txt_garantia', '')),
        ('ENLACE', f'<a href="{limpiar_texto(data.get("txt_enlace", ""))}">{limpiar_texto(data.get("txt_enlace", ""))}</a>'),

        #('ENLACE',                    data.get('txt_enlace', '')),
    ]
    campos_rows = []
    for etiqueta, valor in nuevos_campos:
        campos_rows.append([
            Paragraph(f'<b>{limpiar_texto(etiqueta)}</b>', styleN),
            Paragraph(valor, styleN)
        ])
    campos_style = [
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#DAE9F7')),  # columna de etiquetas
        ('LINEABOVE', (0,0), (-1,0), 0, colors.black),              # sin línea superior (ya la pone la leyenda)
        # esta es la última sección: no hace falta LINEBELOW especial (GRID ya dibuja negro)
    ]
    tbl_campos = _table(campos_rows, props_campos_finales, campos_style, font_size=10)

    # === DocTemplate con fondo membretado ===
    class BackgroundDocTemplate(SimpleDocTemplate):
        def __init__(self, *args, fondo_path=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.fondo_path = fondo_path

        def handle_pageBegin(self):
            super().handle_pageBegin()
            self.canv.saveState()
            if self.fondo_path:
                self.canv.drawImage(
                    self.fondo_path,
                    0, 0,
                    width=ancho_hoja,
                    height=alto_hoja
                )
            self.canv.restoreState()

    doc = BackgroundDocTemplate(
        archivo_salida,
        pagesize=A4,
        rightMargin=margen_der,
        leftMargin=margen_izq,
        topMargin=margen_sup,
        bottomMargin=margen_inf,
        fondo_path=membrete_path
    )

    # === Construcción (sin Spacers entre secciones) ===
    elements = [
        tbl_header,
        tbl_generales,
        tbl_objeto_title,
        tbl_objeto_body,
        tbl_items_header,
        tbl_items_body,
        tbl_items_total,
        tbl_leyenda,
        tbl_campos,
    ]

    # === Firma (dejamos un espacio solo aquí) ===
    elements.append(Spacer(1, 2.2 * cm))
    
    # Datos de firma dinámicos o por defecto
    f_nombre = (full_name or 'DAYANA LISBETH ZAMBRANO MACIAS').upper()
    f_cargo = (job_title or 'REPRESENTANTE LEGAL').upper()
    f_ruc = (ruc or '2350621211001').upper()
    if "RUC" not in f_ruc:
        f_ruc = f"RUC: {f_ruc}"

    elements.append(
        Paragraph(
            f'<font color="#003366"><b>{f_nombre}</b></font>',
            ParagraphStyle('firma_nombre', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold')
        )
    )
    elements.append(
        Paragraph(
            f'<font color="#003366">{f_cargo}</font>',
            ParagraphStyle('firma_cargo', parent=styles['Normal'], alignment=1, fontSize=10)
        )
    )
    elements.append(
        Paragraph(
            f'<font color="#003366">{f_ruc}</font>',
            ParagraphStyle('firma_ruc', parent=styles['Normal'], alignment=1, fontSize=10)
        )
    )

    # Construir PDF
    doc.build(elements)
    return os.path.abspath(archivo_salida)
