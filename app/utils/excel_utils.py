import openpyxl
from copy import copy
from openpyxl.styles import Alignment, Font
import tempfile
import os


def generar_excel_proforma(data: dict, template_path="app/utils/template.xlsx") -> str:
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # --- Título ---
    num_infima = data.get("txt_numeroProforma", "")
    if num_infima:
        solo_numero = num_infima.split('-')[-1]
        ws['A1'] = f"PROFORMA {solo_numero}"
    else:
        ws['A1'] = "PROFORMA"

    # --- Cabecera fija ---
    cabecera_map = {
        'txt_cliente':     'D2',
        'txt_ruc':         'D3',
        'txt_direccion':   'D4',
        'txt_fecha':       'D5',
        'txt_telefono':    'D6',
        'txt_necesidad':   'D7',
        'txt_funcionario': 'D8',
        'txt_correo':      'D9',
        'tHora_maxina':    'D10',
    }
    for k, cell in cabecera_map.items():
        #imprime para ver el resultado de txt_direccion
        ws[cell] = data.get(k, "")

    # --- OBJETO DE COMPRA (A12:G12) ---
    valor_objetivo = data.get("txt_objetivoCompra", "")
    if valor_objetivo:
        try:
            ws.merge_cells("A12:G12")
        except Exception:
            pass
        ws["A12"] = valor_objetivo

    # --- Ítems ---
    items = data.get('items', [])
    n_items = max(1, len(items))  # al menos 1
    item_start_row = 14
    total_row_original = 15
    max_col = 7  # A..G

    def save_merges(ws_):
        merges = []
        for cr in ws_.merged_cells.ranges:
            merges.append({
                'min_row': cr.min_row,
                'max_row': cr.max_row,
                'min_col': cr.min_col,
                'max_col': cr.max_col,
            })
        return merges

    def restore_merges(ws_, merges, insert_at, n_rows, item_start_row, new_total_row, max_col):
        for m in merges:
            min_row = m['min_row']
            max_row = m['max_row']
            min_col = m['min_col']
            max_col_merge = m['max_col']
            if min_row >= insert_at:
                min_row += n_rows
                max_row += n_rows
            if (max_row >= item_start_row and min_row <= new_total_row and min_col <= max_col and max_col_merge >= 1):
                continue
            try:
                ws_.merge_cells(
                    start_row=min_row, start_column=min_col,
                    end_row=max_row, end_column=max_col_merge
                )
            except:
                pass

    merges_orig = save_merges(ws)

    rows_to_insert = max(0, n_items - 1)
    if rows_to_insert:
        ws.insert_rows(total_row_original, rows_to_insert)

    new_total_row = item_start_row + n_items

    for rng in list(ws.merged_cells.ranges):
        try:
            ws.unmerge_cells(str(rng))
        except:
            pass

    restore_merges(
        ws, merges_orig,
        insert_at=total_row_original,
        n_rows=rows_to_insert,
        item_start_row=item_start_row,
        new_total_row=new_total_row,
        max_col=max_col
    )

    # Guardar temporal para reiniciar estilos
    tmp_path = tempfile.mktemp(suffix=".xlsx", prefix="proforma_", dir=".")
    wb.save(tmp_path)
    wb2 = openpyxl.load_workbook(tmp_path)
    ws2 = wb2.active

    # Copiar estilo base de ítems (fila 14) a todas las filas nuevas
    for idx in range(n_items):
        src_row = item_start_row
        dst_row = item_start_row + idx
        for col in range(1, max_col + 1):
            src_cell = ws2.cell(row=src_row, column=col)
            dst_cell = ws2.cell(row=dst_row, column=col)
            dst_cell._style = copy(src_cell._style)
            dst_cell.number_format = src_cell.number_format
            dst_cell.alignment = copy(src_cell.alignment)
            dst_cell.font = copy(src_cell.font)
            dst_cell.border = copy(src_cell.border)
            dst_cell.fill = copy(src_cell.fill)

    # Escribir ítems
    for idx, item in enumerate(items):
        row = item_start_row + idx
        ws2[f'A{row}'] = idx + 1
        ws2[f'B{row}'] = item.get('txt_cpc', '')
        ws2[f'C{row}'] = item.get('txt_unidad', '')
        ws2[f'D{row}'] = item.get('txt_especificaciones', '')
        ws2[f'E{row}'] = item.get('int_cantidad', 0)
        ws2[f'F{row}'] = item.get('flo_precioUnitario', 0)
        ws2[f'G{row}'] = item.get('flo_precioTotal', 0)

    # TOTAL
    ws2.merge_cells(start_row=new_total_row, start_column=1, end_row=new_total_row, end_column=6)
    ws2[f'A{new_total_row}'] = "TOTAL"
    ws2[f'G{new_total_row}'] = sum(float(it.get('flo_precioTotal', 0) or 0) for it in items)

    # Copiar estilos desde fila original de total (fila 15)
    for col in range(1, max_col + 1):
        src_cell = ws2.cell(row=total_row_original, column=col)
        dst_cell = ws2.cell(row=new_total_row, column=col)
        dst_cell._style = copy(src_cell._style)
        dst_cell.number_format = src_cell.number_format
        dst_cell.alignment = copy(src_cell.alignment)
        dst_cell.font = copy(src_cell.font)
        dst_cell.border = copy(src_cell.border)
        dst_cell.fill = copy(src_cell.fill)

    # Forzar centrado y negrita para "TOTAL"
    ws2[f'A{new_total_row}'].alignment = Alignment(horizontal="center", vertical="center")
    ws2[f'A{new_total_row}'].font = Font(bold=True)

    # Fila "NO GRAVAMOS IVA…"
    fila_no_gravamos = new_total_row + 1
    ws2.merge_cells(start_row=fila_no_gravamos, start_column=1, end_row=fila_no_gravamos, end_column=7)
    cell_no_iva = ws2[f"A{fila_no_gravamos}"]
    cell_no_iva.value = "NO GRAVAMOS IVA - SOMOS REGIMEN RIMPE - NEGOCIO POPULAR"
    cell_no_iva.alignment = Alignment(horizontal="center", vertical="center")
    cell_no_iva.font = Font(bold=True,color="FF0000")

    # Campos finales
    start_final_row = new_total_row + 2
    campos_finales = {
        "txt_plazoEntrega":       f"D{start_final_row}",
        "txt_vigenciaOferta":     f"D{start_final_row + 1}",
        "txt_garantia":           f"D{start_final_row + 2}",
        "txt_formaPago":          f"D{start_final_row + 3}",
        "txt_metodologiaTrabajo": f"D{start_final_row + 4}",
        "txt_enlace":             f"D{start_final_row + 5}",
    }

    for k, cell in campos_finales.items():
        valor = data.get(k, "")
        target_cell = ws2[cell]

        # Si está en celda combinada, obtener la celda superior izquierda
        if isinstance(target_cell, openpyxl.cell.cell.MergedCell):
            for merged_range in ws2.merged_cells.ranges:
                if target_cell.coordinate in merged_range:
                    target_cell = ws2.cell(merged_range.min_row, merged_range.min_col)
                    break

        if k == "txt_enlace" and valor:
            # Hacer que sea un hipervínculo
            target_cell.value = valor
            target_cell.hyperlink = valor
            target_cell.style = "Hyperlink"
        else:
            target_cell.value = str(valor) if valor is not None else ""


    wb2.save(tmp_path)
    return tmp_path
