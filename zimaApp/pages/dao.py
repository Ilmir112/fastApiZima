import json



class ChangeExcelToHtml:
    def __init__(self, excel):
        self.excel = json.loads(excel)["excel"]

    @staticmethod
    # Вспомогательная функция для определения span
    def get_span(merge, row_idx, col_idx):
        """
        Проверяет, входит ли текущая ячейка в объединённый диапазон.
        Возвращает (rowSpan, colSpan), если входит, иначе (1, 1).
        """
        start_col = merge[0]
        start_row = merge[1]
        end_col = merge[2]
        end_row = merge[3]
        if start_row == row_idx and start_col == col_idx:
            rowSpan = end_row - start_row + 1
            colSpan = end_col - start_col + 1
            return rowSpan, colSpan
        return 1, 1

    @classmethod
    def change_method(cls, excel):

        excel = json.loads(excel["excel"])
        merged_cells = excel["merged_cells"]
        rowHeights = excel['rowHeights']
        excel_data = {}
        cell_positions = []
        numeration = 1

        for row_idx_str, row in excel["data"].items():
            if row_idx_str != 'image':
                row_idx = int(row_idx_str)
                rows_dict = {}

                height = 30 if (rowHeights is None or len(rowHeights) < row_idx or rowHeights[row_idx - 1] is None) else \
                rowHeights[row_idx - 1]
                rows_dict["height"] = height

                cells = []

                for col_idx, cell in enumerate(row):
                    rowSpan = 1
                    colSpan = 1

                    # Проверка на объединение по строке и колонке
                    for merge in merged_cells.values():
                        merge_start_col = merge[0]
                        merge_start_row = merge[1]
                        merge_end_col = merge[2]
                        merge_end_row = merge[3]

                        # Объединение по колонке
                        if merge_start_row == row_idx and (merge_start_col) == (col_idx + 1):
                            row_span = merge_end_row - merge_start_row
                            col_span = merge_end_col - merge_start_col

                            if row_span > 0:
                                rowSpan = row_span + 1
                            if col_span > 0:
                                colSpan = col_span + 1

                    # Проверка на необходимость повторной установки span
                    # (если есть дополнительные условия или уточнения, их можно добавить)

                    # Получение стилей границ
                    border_left = cell['borders']["left"]["style"]
                    border_right = cell['borders']["right"]["style"]
                    border_top = cell['borders']["top"]["style"]
                    border_bottom = cell['borders']["bottom"]["style"]

                    # Получение выравнивания
                    alignment = cell['alignment']['horizontal']

                    # Обработка формулы COUNTA
                    cell_value = cell["value"]
                    if isinstance(cell_value, str) and "=COUNTA($" in cell_value:
                        cell_value = numeration
                        numeration += 1

                    cell_dict = {
                        "col": col_idx,
                        "row": row_idx - 1,
                        "colSpan": colSpan,
                        "rowSpan": rowSpan,
                        "content": cell_value,
                        "style": {},  # сюда можно добавить стили
                        "alignment": alignment,
                        "border": {
                            "left": border_left,
                            "right": border_right,
                            "top": border_top,
                            "bottom": border_bottom
                        }
                    }

                    cells.append(cell_dict)

                rows_dict["cells"] = cells
                cell_positions.append(rows_dict)

        excel_data["row"] = cell_positions

        return excel_data
