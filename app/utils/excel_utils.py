import openpyxl
from copy import copy
import tempfile
import os

def generar_excel_proforma(data: dict, template_path="app/utils/template.xlsx") -> str:
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    #  <<<
    num_infima = data.get("txt_infimaNro", "")
    if num_infima:
        solo_numero = num_infima.split('-')[-1]
        ws['A1'] = f"PROFORMA {solo_numero}"
    else:
        ws['A1'] = "PROFORMA"
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
        ws[cell] = data.get(k, "")

    n_items = len(data['items'])
    item_start_row = 14
    total_row_original = 15
    max_col = 7

    def save_merges(ws):
        merges = []
        for cr in ws.merged_cells.ranges:
            merges.append({
                'min_row': cr.min_row,
                'max_row': cr.max_row,
                'min_col': cr.min_col,
                'max_col': cr.max_col,
            })
        return merges

    def restore_merges(ws, merges, insert_at, n_rows, item_start_row, new_total_row, max_col):
        for m in merges:
            min_row = m['min_row']
            max_row = m['max_row']
            min_col = m['min_col']
            max_col_merge = m['max_col']
            if min_row >= insert_at:
                min_row += n_rows
                max_row += n_rows
            if insert_at <= m['min_row'] <= m['max_row'] <= insert_at:
                continue
            if (
                max_row >= item_start_row and
                min_row <= new_total_row and
                min_col <= max_col and
                max_col_merge >= 1
            ):
                continue
            try:
                ws.merge_cells(
                    start_row=min_row, start_column=min_col,
                    end_row=max_row, end_column=max_col_merge
                )
            except:
                pass

    merges_orig = save_merges(ws)
    rows_to_insert = max(0, n_items - 2)
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
    to_unmerge = []
    for cr in list(ws.merged_cells.ranges):
        if (
            cr.max_row >= item_start_row and
            cr.min_row <= new_total_row and
            cr.max_col >= 1 and
            cr.min_col <= max_col
        ):
            to_unmerge.append(str(cr))
    for ref in to_unmerge:
        try:
            ws.unmerge_cells(ref)
        except:
            pass

    for i in range(n_items):
        src_row = item_start_row
        dst_row = item_start_row + i
        if i > 0:
            for col in range(1, max_col+1):
                src_cell = ws.cell(row=src_row, column=col)
                dst_cell = ws.cell(row=dst_row, column=col)
                if not isinstance(dst_cell, openpyxl.cell.cell.MergedCell):
                    dst_cell._style = copy(src_cell._style)
                    dst_cell.number_format = src_cell.number_format
                    dst_cell.alignment = copy(src_cell.alignment)
                    dst_cell.font = copy(src_cell.font)
                    dst_cell.border = copy(src_cell.border)
                    dst_cell.fill = copy(src_cell.fill)

    tmp_path = tempfile.mktemp(suffix=".xlsx", prefix="proforma_", dir=".")
    wb.save(tmp_path)
    wb2 = openpyxl.load_workbook(tmp_path)
    ws2 = wb2.active

    for idx, item in enumerate(data['items']):
        row = item_start_row + idx
        ws2[f'A{row}'] = idx + 1
        ws2[f'B{row}'] = item['txt_cpc']
        ws2[f'C{row}'] = item['txt_unidad']
        ws2[f'D{row}'] = item['txt_especificaciones']
        ws2[f'E{row}'] = item['int_cantidad']
        ws2[f'F{row}'] = item['flo_precioUnitario']
        ws2[f'G{row}'] = item['flo_precioTotal']

    ws2.merge_cells(start_row=new_total_row, start_column=1, end_row=new_total_row, end_column=6)
    ws2[f'A{new_total_row}'] = "TOTAL"
    ws2[f'G{new_total_row}'] = sum(float(item['flo_precioTotal']) for item in data['items'])

    for col in range(1, max_col+1):
        src_cell = ws2.cell(row=total_row_original, column=col)
        dst_cell = ws2.cell(row=new_total_row, column=col)
        dst_cell._style = copy(src_cell._style)
        dst_cell.number_format = src_cell.number_format
        dst_cell.alignment = copy(src_cell.alignment)
        dst_cell.font = copy(src_cell.font)
        dst_cell.border = copy(src_cell.border)
        dst_cell.fill = copy(src_cell.fill)

    campos_finales = {
        "txt_plazoEntrega":      "D20",
        "txt_vigenciaOferta":    "D21",
        "txt_garantia":          "D22",
        "txt_formaPago":         "D23",
        "txt_metodologiaTrabajo":"D24",
        "txt_enlace":            "D25",
    }
    for k, cell in campos_finales.items():
        ws2[cell] = data.get(k, "")

    wb2.save(tmp_path)
    return tmp_path
