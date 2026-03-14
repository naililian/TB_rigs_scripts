
function LP_exposeAllSubstitutions() {
    scene.beginUndoRedoAccum("------- exposeAllSubstitutions --------");

    var numSelected = selection.numberOfNodesSelected();

    if (numSelected === 0) {
        MessageLog.trace("Please, select a node drawing (READ).");
        scene.endUndoRedoAccum();
        return;
    }

    var currentFrame = frame.current();

    for (var s = 0; s < numSelected; s++) {
        var selectedNode = selection.selectedNode(s);

        if (selectedNode === "" || node.type(selectedNode) !== "READ") {
            MessageLog.trace("Ignored node(no READ): " + selectedNode);
            continue;
        }

        // 2. Obtener el Element ID y el nombre de la columna
        var elementId = node.getElementId(selectedNode);

        MessageLog.trace("PATH READ : " + selectedNode);
        MessageLog.trace("ElementID: " + elementId);

        var drawingColumn = node.linkedColumn(selectedNode, "DRAWING.ELEMENT");

        var exposure = column.getEntry(drawingColumn, 1, currentFrame);
        MessageLog.trace("Exposure: " + exposure);

        if (!drawingColumn) {
            MessageLog.trace("The node has not linked column: " + selectedNode);
            continue;
        }

        // 3. Obtener la cantidad total de dibujos en ese elemento
        var drawingCount = Drawing.numberOf(elementId);
        MessageLog.trace("Total de dibujos encontrados: " + drawingCount);

        // 4. Iterar sobre los dibujos y exponerlos uno tras otro desde el frame actual
        for (var i = 0; i < drawingCount; i++) {
            var drawingName = Drawing.name(elementId, i);
            var targetFrame = currentFrame + i;

            column.setEntry(drawingColumn, 1, targetFrame, drawingName);

            MessageLog.trace("Frame " + targetFrame + ": " + drawingName);
        }

        MessageLog.trace("Processed node: " + selectedNode);
    }

    scene.endUndoRedoAccum();
    MessageLog.trace("Process finished with success.");
}

