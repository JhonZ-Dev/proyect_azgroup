from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import qn
import os

def set_cell_bg(cell, color_hex):
    """Set background color of a cell by direct XML injection."""
    cell._tc.get_or_add_tcPr().append(
        parse_xml(
            r'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="{}"/>'.format(color_hex)
        )
    )
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_hyperlink(paragraph, url, text, color="2d3fd6", underline=True, font_name="Calibri", font_size=11):
    # Create the w:hyperlink tag and add needed values
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    # Create a w:r element
    new_run = OxmlElement('w:r')

    # Create a w:rPr element
    rPr = OxmlElement('w:rPr')

    # Style: color
    c = OxmlElement('w:color')
    c.set(qn('w:val'), color)
    rPr.append(c)
    # Style: underline
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), "single")
        rPr.append(u)

    # Font size and font name
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(font_size*2))
    rPr.append(sz)
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rPr.append(rFonts)

    # Add rPr to run
    new_run.append(rPr)

    # Add text to run
    t = OxmlElement('w:t')
    t.text = text
    new_run.append(t)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return paragraph


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
plantilla_path = os.path.join(BASE_DIR, "plantilla.docx")

def generar_doc_proforma(data, plantilla_path=plantilla_path, archivo_salida="proforma_final.docx"):
    # 1. Cargar plantilla membretada y eliminar tabla dummy
    doc = Document(plantilla_path)
    if doc.tables:
        tbl = doc.tables[0]
        tbl._element.getparent().remove(tbl._element)

    # --- Ajuste de tabla: ocupa 18 cm exactos (márgenes ya definidos en Word)
    tabla = doc.add_table(rows=0, cols=7)
    tabla.style = 'Table Grid'
    tabla.autofit = False
    tabla.allow_autofit = False
    tabla.width = Cm(18)

    # Define el ancho de cada columna (debe sumar 18 cm aprox.)
    col_widths = [2.3, 2.7, 2, 5.5, 1.7, 1.9, 1.9]  # Puedes ajustar a tu gusto

    # 1. PROFORMA (cabecera)
    # 1. PROFORMA (cabecera)
    row = tabla.add_row().cells
    row[0].merge(row[6])
    p = row[0].paragraphs[0]
    p.clear()

    # Extraer solo el número (por ejemplo, de '04-08-000000001' obtener '000000001')
    infima_nro = data.get('txt_infimaNro', '')
    solo_numero = infima_nro.split('-')[-1] if infima_nro else ''

    # Primer run: PROFORMA (negro)
    run1 = p.add_run("PROFORMA ")
    run1.bold = True
    run1.font.size = Pt(10)
    run1.font.name = 'Arial'
    r1 = run1._element
    r1.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')

    # Segundo run: el número (rojo)
    run2 = p.add_run(solo_numero)
    run2.bold = True
    run2.font.size = Pt(10)
    run2.font.name = 'Arial'
    run2.font.color.rgb = RGBColor.from_string('DC2626')  # Rojo
    r2 = run2._element
    r2.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')

    # Centrado y fondo
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cell_bg(row[0], 'dae9f7')


    # 2. Campos principales (campo + respuesta, formateados según tu pedido)
    campos = [
        ('CLIENTE', data.get('txt_cliente', '')),
        ('RUC', data.get('txt_ruc', '')),
        ('DIRECCIÓN:', data.get('txt_direccion', '')),
        ('FECHA', data.get('txt_fecha', '')),
        ('TELEFONO', data.get('txt_telefono', '')),
        ('NECESIDAD', data.get('txt_necesidad', '')),
        ('FUNCIONARIO ENCARGADO:', data.get('txt_funcionario', '')),
        ('CORREO', data.get('txt_correo', '')),
        ('HORA MAXIMA:', str(data.get('tHora_maxina', ''))[:16].replace('T',' ')),
    ]

    for label, valor in campos:
        row = tabla.add_row().cells
        row[0].merge(row[1])
        set_cell_bg(row[0], 'e8f2fe')
        p = row[0].paragraphs[0]
        p.clear()
        run = p.add_run(label)
        run.font.size = Pt(10)
        run.bold = True
        run.font.name = 'Arial'
        r = run._element
        r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        row[2].merge(row[6])
        p2 = row[2].paragraphs[0]
        p2.clear()
        run2 = p2.add_run(valor)
        run2.font.size = Pt(10)
        run2.font.name = 'Arial'
        r2 = run2._element
        r2.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')

        # Formato especial por campo
        if label in ('CLIENTE', 'RUC', 'DIRECCIÓN:', 'FECHA', 'TELEFONO'):
            run2.bold = True
        elif label == 'NECESIDAD':
            run2.bold = True
            run2.font.color.rgb = RGBColor.from_string('DC2626')  # Rojo
        elif label == 'CORREO':
            run2.font.color.rgb = RGBColor.from_string('2d3fd6')  # Azul
            run2.underline = True
        elif label == 'HORA MAXIMA:':
            run2.bold = True
            run2.font.color.rgb = RGBColor.from_string('1A365D')  # Azul oscuro

    # 3. OBJETO DE COMPRA (título y respuesta)
# --- OBJETO DE COMPRA (título centrado, azul claro, Arial 10, negrita) ---
    row = tabla.add_row().cells
    row[0].merge(row[6])
    p = row[0].paragraphs[0]
    p.clear()
    run = p.add_run("OBJETO DE COMPRA")
    run.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial'
    r = run._element
    r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    set_cell_bg(row[0], 'dae9f7')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- OBJETO DE COMPRA (respuesta centrada, Arial 10) ---
    row = tabla.add_row().cells
    row[0].merge(row[6])
    p = row[0].paragraphs[0]
    p.clear()
    run = p.add_run(data.get('txt_objetivoCompra', ''))
    run.font.size = Pt(10)
    run.font.name = 'Arial'
    r = run._element
    r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    set_cell_bg(row[0], 'D8D8D8')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    

    # 4. CABECERAS DE ÍTEMS
    headers = ['No.', 'CPC', 'UNIDAD', 'ESPECIFICACIONES', 'CANTIDAD', 'P. UNIT', 'P.TOTAL']
    row = tabla.add_row().cells
    for i, h in enumerate(headers):
        p = row[i].paragraphs[0]
        p.clear()
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(10)
        run.font.name = 'Arial'
        r = run._element
        r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(row[i], 'dae9f7')

    # 5. FILAS DE ÍTEMS
    items = data.get('items', [])
    total = 0
    for idx, item in enumerate(items):
        row = tabla.add_row().cells
        row[0].text = str(idx+1)
        row[1].text = str(item.get('txt_cpc', ''))
        row[2].text = str(item.get('txt_unidad', ''))
        row[3].text = str(item.get('txt_especificaciones', ''))
        row[4].text = str(item.get('int_cantidad', ''))
        row[5].text = f"{item.get('flo_precioUnitario', 0):.2f}"
        row[6].text = f"{item.get('flo_precioTotal', 0):.2f}"
        total += item.get('flo_precioTotal', 0)

    # 6. TOTAL
    # --- FILA TOTAL ---
    row = tabla.add_row().cells
    row[0].merge(row[5])

    # Celda "TOTAL": centrado, negrita, Arial 10, fondo amarillo claro
    p = row[0].paragraphs[0]
    p.clear()
    run = p.add_run("TOTAL")
    run.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial'
    r = run._element
    r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cell_bg(row[0], 'dae9f7')  # fondo amarillo claro

    # Celda con el valor: Arial 10, negrita, SIN fondo
    p2 = row[6].paragraphs[0]
    p2.clear()
    run2 = p2.add_run(f"${total:.2f}")
    run2.bold = True
    run2.font.size = Pt(10)
    run2.font.name = 'Arial'
    r2 = run2._element
    r2.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # (No se pone fondo aquí)

    # 7. NO GRAVAMOS IVA
    # --- NO GRAVAMOS IVA ---
    row = tabla.add_row().cells
    row[0].merge(row[6])

    p = row[0].paragraphs[0]
    p.clear()
    run = p.add_run("NO GRAVAMOS IVA - SOMOS REGIMEN RIMPE - NEGOCIO POPULAR")
    run.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial'
    run.font.color.rgb = RGBColor.from_string('DC2626')  # rojo
    r = run._element
    r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    set_cell_bg(row[0], 'dae9f7')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


    # 8. CAMPOS FINALES
    # finales = [
    #     ('PLAZO DE ENTREGA', data.get('txt_plazoEntrega', '')),
    #     ('VIGENCIA DE LA OFERTA', data.get('txt_vigenciaOferta', '')),
    #     ('FORMA DE PAGO:', data.get('txt_formaPago', '')),
    #     ('METODOLOGIA DE TRABAJO', data.get('txt_metodologiaTrabajo', '')),
    #     ('GARANTIA', data.get('txt_garantia', '')),
    #     ('ENLACE', data.get('txt_enlace', ''))
    # ]
    # for label, valor in finales:
    #     row = tabla.add_row().cells
    #     row[0].merge(row[1])
    #     row[0].text = label
    #     row[2].merge(row[6])
    #     row[2].text = valor
    #     # --- CAMPOS FINALES
    finales = [
        ('PLAZO DE ENTREGA', data.get('txt_plazoEntrega', '')),
        ('VIGENCIA DE LA OFERTA', data.get('txt_vigenciaOferta', '')),
        ('FORMA DE PAGO:', data.get('txt_formaPago', '')),
        ('METODOLOGIA DE TRABAJO', data.get('txt_metodologiaTrabajo', '')),
        ('GARANTIA', data.get('txt_garantia', '')),
        ('ENLACE', data.get('txt_enlace', ''))
    ]
    for label, valor in finales:
        row = tabla.add_row().cells
        # Campo (label)
        row[0].merge(row[1])
        p1 = row[0].paragraphs[0]
        p1.clear()
        run1 = p1.add_run(label)
        run1.bold = True
        run1.font.size = Pt(10)
        run1.font.name = 'Arial'
        r1 = run1._element
        r1.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')

        # Respuesta (valor)
        row[2].merge(row[6])
        p2 = row[2].paragraphs[0]
        p2.clear()
        if label == 'ENLACE':
            add_hyperlink(
                p2,
                valor,
                valor,
                color="2d3fd6",
                underline=True,
                font_name="Calibri",
                font_size=11
            )
            # run2 = p2.add_run(valor)
            # run2.font.size = Pt(11)
            # run2.font.name = 'Calibri'
            # run2.underline = True
            # r2 = run2._element
            # #run2.font.color.rgb = RGBColor.from_string('0563C1')
            # run2.font.color.rgb = RGBColor.from_string('2d3fd6')
            # r2.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        else:
            run2 = p2.add_run(valor)
            run2.font.size = Pt(10)
            run2.font.name = 'Arial'
            r2 = run2._element
            r2.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')


    # -- Ajustar el ancho de cada columna en toda la tabla --
    for row in tabla.rows:
        for i, width in enumerate(col_widths):
            row.cells[i].width = Cm(width)

    # 9. Firma fuera de la tabla
    doc.add_paragraph('')
    doc.add_paragraph('')
    p = doc.add_paragraph()
    # Línea 1: Nombre
    run1 = p.add_run('DAYANA LISBETH ZAMBRANO MACIAS\n')
    run1.bold = True
    run1.font.name = 'Times New Roman'
    run1.font.size = Pt(11)
    run1.font.color.rgb = RGBColor.from_string('1A365D')
    r1 = run1._element
    r1.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Línea 2: Cargo
    run2 = p.add_run('REPRESENTANTE LEGAL\n')
    run2.bold = False
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(11)
    # (por defecto el color es negro)
    r2 = run2._element
    r2.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Línea 3: RUC
    run3 = p.add_run('RUC: 2350621211001')
    run3.bold = False
    run3.font.name = 'Times New Roman'
    run3.font.size = Pt(11)
    r3 = run3._element
    r3.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.save(archivo_salida)
    return archivo_salida

