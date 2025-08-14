from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import re

def limpiar_texto(texto):
    """Elimina caracteres no imprimibles y reemplaza saltos de línea por espacio."""
    if not isinstance(texto, str):
        texto = str(texto)
    # Elimina todo menos los caracteres imprimibles
    texto = re.sub(r'[^\x20-\x7E\n]', '', texto)
    # Opcional: reemplaza saltos de línea por espacio
    texto = texto.replace('\n', ' ').replace('\r', '')
    return texto
def generar_pdf_proforma(
    data: dict,
    archivo_salida: str = None,
    membrete_path: str = None
) -> str:
    """
    Genera un PDF de proforma usando datos dinámicos y devuelve la ruta del archivo.
    """
    ancho_hoja, alto_hoja = A4
    margen_izq = 1.5 * cm
    margen_der = 1.5 * cm
    margen_sup = 3 * cm
    margen_inf = 3 * cm

    ancho_util = ancho_hoja - margen_izq - margen_der
    #proporciones = [0.18, 0.18, 0.10, 0.28, 0.09, 0.085, 0.085]
    proporciones = [0.12, 0.15, 0.10, 0.36, 0.09, 0.09, 0.09]
    colWidths = [ancho_util * p for p in proporciones]

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleBH = styles['Heading4']

    style_rojo_centrado = ParagraphStyle(
        'RojoCentrado', parent=styles['Normal'],
        alignment=0, fontSize=10, textColor=colors.red, fontName='Helvetica-Bold'
    )
    style_rojo_centrados = ParagraphStyle(
        'RojoCentrado', parent=styles['Normal'],
        alignment=1, fontSize=10, textColor=colors.red, fontName='Helvetica-Bold'
    )
    style_bold = ParagraphStyle(
        'Negrita', parent=styles['Normal'],
        alignment=0, fontSize=10, textColor=colors.black, fontName='Helvetica-Bold'
    )
    style_bold_centrado = ParagraphStyle(
        'NegritaCentrado', parent=styles['Normal'],
        alignment=1, fontSize=10, textColor=colors.black, fontName='Helvetica-Bold'
    )
    style_longtext = ParagraphStyle(
    'LongText',
    parent=styleN,
    wordWrap='CJK',     # Permite wraps por sílabas/palabras
    fontSize=9
    )

    # Nombre del archivo según txt_necesidad (o lo que prefieras)
    necesidad = data.get("txt_necesidad", "proforma").replace(" ", "_")
    archivo_salida = archivo_salida or f"proforma_{necesidad}.pdf"

    tabla_data = []

    # Fila: Proforma
 # Fila: Proforma
    txt_infimaNro = data.get("txt_infimaNro", "")
    solo_numero = txt_infimaNro.split('-')[-1] if txt_infimaNro else ""
    tabla_data.append([
        Paragraph(
            f'<b>PROFORMA <font color="red">{solo_numero}</font></b>',
            ParagraphStyle(
                'CentradoGrande',
                parent=styles['Heading4'],
                alignment=1,  # Centrado
                fontName='Helvetica-Bold',
                fontSize=10
            )
        ),
        '', '', '', '', '', ''
    ])


    # Datos generales (ajusta nombres según tu modelo de datos)
    tabla_data.append([
        Paragraph('<b>CLIENTE</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_cliente", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>RUC</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_ruc", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>DIRECCIÓN</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_direccion", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>FECHA</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_fecha", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>TELÉFONO</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_telefono", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>NECESIDAD</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_necesidad", "")), style_rojo_centrado), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>FUNCIONARIO ENCARGADO</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_funcionario", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>CORREO</b>', style_bold_centrado),
        Paragraph(str(data.get("txt_correo", "")), style_bold), '', '', '', '', ''
    ])
    tabla_data.append([
        Paragraph('<b>HORA MÁXIMA</b>', style_bold_centrado),
        Paragraph(str(data.get("tHora_maxina", "")), style_bold), '', '', '', '', ''
    ])

    # Fila: OBJETO DE COMPRA
    tabla_data.append([
        Paragraph('<b>OBJETO DE COMPRA</b>', style_bold_centrado), '', '', '', '', '', ''
    ])
    # Fila: Respuesta objeto de compra
    tabla_data.append([
        Paragraph(str(data.get("txt_objetivoCompra", "")), styleN), '', '', '', '', '', ''
    ])

    # Fila: CABECERA DE ITEMS
    tabla_data.append([
        Paragraph('<b>No.</b>', styleN),
        Paragraph('<b>CPC</b>', styleN),
        Paragraph('<b>UNIDAD</b>', styleN),
        Paragraph('<b>ESPECIFICACIONES</b>', styleN),
        Paragraph('<b>CANTIDAD</b>', styleN),
        Paragraph('<b>P. UNIT</b>', styleN),
        Paragraph('<b>P. TOTAL</b>', styleN),
    ])

    # Ítems de la tabla
    items = data.get("items", [])
    for idx, item in enumerate(items, 1):
        fila = [
            limpiar_texto(idx),
            limpiar_texto(item.get("txt_cpc", "")),
            limpiar_texto(item.get("txt_unidad", "")),
            Paragraph(limpiar_texto(item.get("txt_especificaciones", "")), style_longtext),
            limpiar_texto(item.get("int_cantidad", "")),
            limpiar_texto(item.get("flo_precioUnitario", "")),
            limpiar_texto(item.get("flo_precioTotal", "")),
        ]
        tabla_data.append(fila)

    # Fila: TOTAL (calculado)
    total = sum(float(item.get("flo_precioTotal", 0) or 0) for item in items)
    tabla_data.append([
        Paragraph('<b>TOTAL</b>', style_bold_centrado), '', '', '', '', '',
        Paragraph(f'<b>{total:.2f}</b>', styleN)
    ])
    index_total = len(tabla_data) - 1

    # Fila: NO GRAVAMOS IVA
    tabla_data.append([
        Paragraph('NO GRAVAMOS IVA', style_rojo_centrados), '', '', '', '', '', ''
    ])
    index_no_gravamos_iva = len(tabla_data) - 1

    # Nuevos campos después de NO GRAVAMOS IVA
    nuevos_campos = [
        ('PLAZO DE ENTREGA', data.get('txt_plazoEntrega', '')),
        ('VIGENCIA DE LA OFERTA', data.get('txt_vigenciaOferta', '')),
        ('FORMA DE PAGO', data.get('txt_formaPago', '')),
        ('METODOLOGIA DE TRABAJO', data.get('txt_metodologiaTrabajo', '')),
        ('GARANTIA', data.get('txt_garantia', '')),
        ('ENLACE', data.get('txt_enlace', '')),
    ]
    index_primero_nuevo = len(tabla_data)
    for etiqueta, valor in nuevos_campos:
        tabla_data.append([
            Paragraph(f'<b>{etiqueta}</b>', styleN),
            Paragraph(str(valor), styleN), '', '', '', '', ''
        ])

    # Spans
    span_cmds = [
        ('SPAN', (0,0), (6,0)),    # PROFORMA
        ('SPAN', (1,1), (6,1)),    # CLIENTE
        ('SPAN', (1,2), (6,2)),    # RUC
        ('SPAN', (1,3), (6,3)),    # DIRECCIÓN
        ('SPAN', (1,4), (6,4)),    # FECHA
        ('SPAN', (1,5), (6,5)),    # TELÉFONO
        ('SPAN', (1,6), (6,6)),    # NECESIDAD
        ('SPAN', (1,7), (6,7)),    # FUNCIONARIO ENCARGADO
        ('SPAN', (1,8), (6,8)),    # CORREO
        ('SPAN', (1,9), (6,9)),    # HORA MÁXIMA
        ('SPAN', (0,10), (6,10)),  # OBJETO DE COMPRA
        ('SPAN', (0,11), (6,11)),  # Respuesta OBJETO DE COMPRA
        ('SPAN', (0,index_total), (5,index_total)),  # TOTAL ocupa columnas 0-5
        ('SPAN', (0,index_no_gravamos_iva), (6,index_no_gravamos_iva)),  # NO GRAVAMOS IVA toda la fila
    ]
    for i in range(index_primero_nuevo, index_primero_nuevo + len(nuevos_campos)):
        span_cmds.append(('SPAN', (1, i), (6, i)))  # Respuesta ocupa columnas 1-6

    # Table y estilos
    tabla = Table(
        tabla_data,
        colWidths=colWidths
    )
    tabla.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (6,0), colors.HexColor('#DAE9F7')),
        ('BACKGROUND', (0,12), (6,12), colors.HexColor('#DAE9F7')),  # Cabecera de ítems
        ('BACKGROUND', (0,1), (0,9), colors.HexColor('#DAE9F7')),
        ('BACKGROUND', (0, index_primero_nuevo), (0, index_primero_nuevo + len(nuevos_campos) - 1), colors.HexColor('#DAE9F7')),
        ('BACKGROUND', (0, index_total), (6, index_total), colors.HexColor('#DAE9F7')),
        ('BACKGROUND', (0,10), (6,10), colors.HexColor('#DAE9F7')),    # OBJETO DE COMPRA
        *span_cmds
    ]))

    # Clase para fondo membretada
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

    # Generar el PDF
    doc = BackgroundDocTemplate(
        archivo_salida,
        pagesize=A4,
        rightMargin=margen_der,
        leftMargin=margen_izq,
        topMargin=margen_sup,
        bottomMargin=margen_inf,
        fondo_path=membrete_path
    )
    elements = [tabla]
    doc.build(elements)

    # Retorna la ruta final del archivo generado
    return os.path.abspath(archivo_salida)
