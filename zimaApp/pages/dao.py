import json


class ChangeExcelToHtml:
    def __init__(self, excel):
        self.excel = json.loads(excel)["excel"]

    @classmethod
    def change_method(self, excel):
        # Создадим структуру для новой формы

        self.excel = json.loads(excel["excel"])
        merged_cells = self.excel["merged_cells"]
        rowHeights = self.excel['rowHeights']
        excel_data = {}
        cell_positions = []

        for row_idx, row in self.excel["data"].items():
            if row_idx != 'image':
                row_idx = int(row_idx) - 1

                rows_dict = {}

                rows_dict["height"] = 30 if rowHeights[row_idx] is None else rowHeights[row_idx]
                cells = []
                for col_idx, cell in enumerate(row):
                    # В реальности эти данные должны идти из вашего источника
                    for merge_index, merge in merged_cells.items():
                        rowSpan = 1
                        colSpan = 1
                        if merge[1] == int(row_idx) and int(col_idx) == merge[0]:
                            row_span = merge[3] - merge[1]
                            if row_span > 0:
                                rowSpan = row_span + 1
                            col_span = merge[2] - merge[0]
                            if col_span > 0:
                                colSpan = col_span + 1

                    cells.append({
                        "col": col_idx,
                        "row": row_idx,
                        "colSpan": colSpan,
                        "rowSpan": rowSpan,
                        "content": cell["value"],
                        "style": {}
                    })

                rows_dict["cells"] = cells
                cell_positions.append(rows_dict)
        excel_data["row"] = cell_positions

        return json.dumps(excel_data, ensure_ascii=False, indent=4)
