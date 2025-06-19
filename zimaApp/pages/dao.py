import json


class ChangeExcelToHtml:
    def __init__(self, excel):
        self.excel = json.loads(excel)["excel"]

    @classmethod
    def change_method(cls, excel):

        excel = json.loads(excel["excel"])
        merged_cells = excel["merged_cells"]
        rowHeights = excel['rowHeights']
        excel_data = {}
        cell_positions = []
        numeration = 1

        for row_idx, row in excel["data"].items():
            if row_idx != 'image':
                row_idx = int(row_idx)
                rows_dict = {}

                rows_dict["height"] = 30 if rowHeights[row_idx] is None else rowHeights[row_idx]
                cells = []
                for col_idx, cell in enumerate(row):
                    # В реальности эти данные должны идти из вашего источника
                    for merge_index, merge in merged_cells.items():
                        rowSpan = 1
                        colSpan = 1
                        if merge[1] == int(row_idx) and int(col_idx) + 1 == merge[0]:
                            row_span = merge[3] - merge[1]
                            if row_span > 1:
                                rowSpan = row_span + 1
                                break
                    for merge_index, merge in merged_cells.items():
                        if merge[1] == int(row_idx) and int(col_idx) + 1 == merge[0]:
                            col_span = merge[2] - merge[0]
                            if col_span > 1:
                                colSpan = col_span + 1
                                break
                    border_left = cell['borders']["left"]["style"]
                    border_right = cell['borders']["right"]["style"]
                    border_top = cell['borders']["top"]["style"]
                    border_bottom = cell['borders']["bottom"]["style"]

                    alignment = cell['alignment']['horizontal']
                    if "=COUNTA($" in str(cell["value"]):
                        cell["value"] = numeration
                        numeration += 1

                    cells.append({
                        "col": col_idx,
                        "row": row_idx - 1,
                        "colSpan": colSpan,
                        "rowSpan": rowSpan,
                        "content": cell["value"],
                        "style": {},
                        'alignment': alignment,
                        "border": {
                            "left": border_left,
                            "right": border_right,
                            "top": border_top,
                            "bottom": border_bottom
                        }
                    })

                rows_dict["cells"] = cells
                cell_positions.append(rows_dict)
        excel_data["row"] = cell_positions

        return excel_data

