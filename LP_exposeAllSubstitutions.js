
function LP_exposeAllSubstitutions() {
    scene.beginUndoRedoAccum("------- exposeAllSubstitutions --------");

    // 1. Obtener el nodo seleccionado (asegúrate de tener uno seleccionado)
    var selectedNode = selection.selectedNode(0);

    if (selectedNode === "" || node.type(selectedNode) !== "READ") {
        MessageLog.trace("Por favor, selecciona un nodo de dibujo (READ).");
        scene.endUndoRedoAccum();
        return;
    }

    // 2. Obtener el Element ID y el nombre de la columna
    var elementId = node.getElementId(selectedNode);

    MessageLog.trace("PATH READ : "+ selectedNode )
    MessageLog.trace("ElementID: "+ elementId)

    var drawingColumn = node.linkedColumn(selectedNode, "DRAWING.ELEMENT");

    var exposure = column.getEntry(drawingColumn, 1,frame.current() )
    MessageLog.trace("Exposure: " + exposure);

    if (!drawingColumn) {
        MessageLog.trace("El nodo no tiene una columna de dibujo vinculada.");
        scene.endUndoRedoAccum();
        return;
    }

    // 3. Obtener la cantidad total de dibujos en ese elemento
    var drawingCount = Drawing.numberOf(elementId);
    MessageLog.trace("Total de dibujos encontrados: " + drawingCount);

    // 4. Obtener el frame actual
    var currentFrame = frame.current();
    
    // 5. Iterar sobre los dibujos y exponerlos uno tras otro desde el frame actual
    for (var i = 0; i < drawingCount; i++) {
        // Obtenemos el nombre real del dibujo por su índice
        var drawingName = Drawing.name(elementId, i);
        var targetFrame = currentFrame + i;

        // Exponemos el dibujo en el frame correspondiente
        column.setEntry(drawingColumn, 1, targetFrame, drawingName);
        
        MessageLog.trace("Frame " + targetFrame + ": " + drawingName);
    }

    scene.endUndoRedoAccum();
    MessageLog.trace("Proceso finalizado con éxito.");
}

