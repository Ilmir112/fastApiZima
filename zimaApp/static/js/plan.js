function generateTableHTML(tableData) {
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';

    const occupied = {};

    tableData.row.forEach((rowData, rowIndex) => {
        const tr = document.createElement('tr');
        tr.style.height = rowData.height + 'px';

        rowData.cells.forEach(cell => {
            const {
                col,
                row: r,
                colSpan = 1,
                rowSpan = 1,
                content = '',
                style = {},
                alignment = 'left',
                border = {}
            } = cell;

            if (occupied[`${r},${col}`]) return;

            const td = document.createElement('td');
            td.innerHTML = content;

            // Применяем стили
            for (const [key, value] of Object.entries(style)) {
                td.style[key] = value;
            }

            // Выравнивание текста
            if (['left', 'center', 'right'].includes(alignment)) {
                td.style.textAlign = alignment;
            }

            // Обработка границ снизу
            if (border && typeof border === 'object') {
                for (const [borderSide, borderStyle] of Object.entries(border)) {
                    let side = borderSide;
                    if (side === 'border') side = 'border';

                    if (borderStyle === 'thin' || borderStyle === 'medium') {
                        td.style['border-' + side] = '1px solid #000';

                    }
                }
            }

            // Объединения ячеек
            if (colSpan > 1) td.colSpan = colSpan;
            if (rowSpan > 1) td.rowSpan = rowSpan;

            tr.appendChild(td);

            // Помечаем занятые ячейки из-за объединений
            for (let rOffset = 0; rOffset < rowSpan; rOffset++) {
                for (let cOffset = 0; cOffset < colSpan; cOffset++) {
                    if (rOffset === 0 && cOffset === 0) continue;
                    occupied[`${r + rOffset},${col + cOffset}`] = true;
                }
            }
        });

        table.appendChild(tr);
    });

    // Вставляем таблицу в контейнер
    const container = document.getElementById('tableContainer');
    container.innerHTML = '';
    container.appendChild(table);
}