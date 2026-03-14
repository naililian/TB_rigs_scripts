/**
 * LP_newPaletteRecolorSelColors
 *
 * Creates a new palette from the currently selected palette.
 * A dialog lets the user:
 *   - Name the new palette / asset (defaults to the current palette name).
 *   - Choose which individual colors get NEW color IDs and have all drawings
 *     recolored to the new palette (checked items).
 *   - Leave the remaining colors as shared clones (same ID as original, no
 *     drawing recolor needed).
 *
 * Based on PAL_Copy_Palette_With_New_Color_IDs by Yu Ueda.
 * Extended by Lilian Penzo.
 */

function LP_newPaletteRecolorSelColors() {

    MessageLog.trace("=== LP_newPaletteRecolorSelColors START ===");

    var paletteList = PaletteObjectManager.getScenePaletteList();
    var OGPalID    = PaletteManager.getCurrentPaletteId();
    var OGPal      = paletteList.getPaletteById(OGPalID);

    MessageLog.trace("Current palette ID: " + OGPalID);
    MessageLog.trace("Current palette nColors: " + OGPal.nColors);

    if (OGPal.nColors === 0) {
        MessageBox.information("Selected palette has no colors.");
        return;
    }

    var palName = PaletteManager.getCurrentPaletteName();
    MessageLog.trace("Palette name: " + palName);

    // ── Show dialog ──────────────────────────────────────────────────────────
    MessageLog.trace("Opening dialog...");
    var result = _showRecolorDialog(OGPal, palName);
    MessageLog.trace("Dialog closed. result is: " + (result ? "OK" : "null/cancelled"));

    if (!result) {
        MessageLog.trace("User cancelled. Exiting.");
        return;
    }

    var assetName       = result.assetName;
    var selectedIndices = result.selectedIndices;

    MessageLog.trace("Asset name: " + assetName);
    MessageLog.trace("Selected indices count: " + selectedIndices.length + "  -> [" + selectedIndices.join(", ") + "]");

    if (selectedIndices.length === 0) {
        MessageBox.information("No colors were checked — nothing to recolor.");
        return;
    }

    // ── Find Colour Selector nodes that reference any of the selected colors ─
    var CSNodes = _getRelativeColorSelectors(OGPal, selectedIndices);
    MessageLog.trace("Colour Selector nodes found: " + CSNodes.length);

    scene.beginUndoRedoAccum("Recolor Selected Colors – " + assetName);

    // ── Create new palette ───────────────────────────────────────────────────
    var newPalPath = paletteList.getPath() + "/palette-library/" + assetName;
    MessageLog.trace("Creating new palette at: " + newPalPath);
    var newPalFile = paletteList.createPalette(newPalPath, 0);
    MessageLog.trace("New palette file id: " + newPalFile.id);
    var newPal     = paletteList.getPaletteById(newPalFile.id);

    // Remove the "Default" color Harmony creates automatically
    var defaultColor = newPal.getColorByIndex(0);
    newPal.removeColor(defaultColor.id);
    MessageLog.trace("Removed default color from new palette.");

    // ── Process each color ───────────────────────────────────────────────────
    var nColorsCaptured = OGPal.nColors;
    MessageLog.trace("Processing " + nColorsCaptured + " colors...");

    for (var c = 0; c < nColorsCaptured; c++) {
        var OGColor    = OGPal.getColorByIndex(c);
        var isSelected = (selectedIndices.indexOf(c) !== -1);

        MessageLog.trace("Color [" + c + "] '" + OGColor.name + "' id=" + OGColor.id + "  recolor=" + isSelected);

        if (isSelected) {
            // Duplicate → clone to new palette → recolor drawings
            var copiedColor = OGPal.duplicateColor(OGColor);
            MessageLog.trace("  Duplicated -> new id: " + copiedColor.id);
            newPal.cloneColor(copiedColor);
            OGPal.removeColor(copiedColor.id);

            var drawKeys = _getNodeColors(OGColor.id);
            MessageLog.trace("  Draw keys found: " + drawKeys.length);
            for (var d = 0; d < drawKeys.length; d++) {
                DrawingTools.recolorDrawing(drawKeys[d], [{ from: OGColor.id, to: copiedColor.id }]);
                MessageLog.trace("  Recolored draw key " + d + " node=" + drawKeys[d].node + " frame=" + drawKeys[d].frame);
            }

            if (CSNodes.length > 0)
                _recolorColorSelectorItems(OGColor.id, copiedColor.id, CSNodes);

            MessageLog.trace("[RECOLORED] " + OGColor.name + "  (old id: " + OGColor.id + "  -> new id: " + copiedColor.id + ")");

        } else {
            // Not selected — skip entirely, do not add to new palette
            MessageLog.trace("[SKIPPED]   " + OGColor.name + "  (id: " + OGColor.id + ")");
        }
    }

    scene.endUndoRedoAccum();
    MessageLog.trace("=== Done. New palette created: " + assetName + " ===");
}


// ─────────────────────────────────────────────────────────────────────────────
//  Dialog
// ─────────────────────────────────────────────────────────────────────────────

function _showRecolorDialog(palette, defaultName) {

    var dialog = new QDialog();
    dialog.windowTitle = "New Palette – Recolor Selected Colors";
    dialog.minimumWidth = 440;

    var mainLayout = new QVBoxLayout();
    mainLayout.setSpacing(10);

    // ── Asset / palette name ─────────────────────────────────────────────────
    var nameGroup  = new QGroupBox("New Palette Name");
    var nameLayout = new QHBoxLayout();
    var nameInput  = new QLineEdit();
    nameInput.text            = defaultName;
    nameInput.placeholderText = "e.g. Char_A_Night";
    nameLayout.addWidget(nameInput, 0, Qt.AlignTop);
    nameGroup.setLayout(nameLayout);
    mainLayout.addWidget(nameGroup, 0, Qt.AlignTop);

    // ── Color list ───────────────────────────────────────────────────────────
    var listGroup  = new QGroupBox("Colors to Recolor   (checked = new ID  +  recolor drawings)");
    var listLayout = new QVBoxLayout();

    var listWidget = new QListWidget();

    for (var i = 0; i < palette.nColors; i++) {
        var color = palette.getColorByIndex(i);
        var label = color.name || ("Color " + i);

        var item = new QListWidgetItem("   " + label);
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable);
        item.setCheckState(Qt.Checked);

        // Color swatch: set item background for solid colors
        if (color.colorType === 0) {   // 0 = SOLID_COLOR
            try {
                var cd        = color.colorData;
                var luminance = 0.299 * cd.r + 0.587 * cd.g + 0.114 * cd.b;
                item.setBackground(new QColor(cd.r, cd.g, cd.b, 255));
                item.setForeground(luminance > 128
                    ? new QColor(0,   0,   0,   255)
                    : new QColor(255, 255, 255, 255));
            } catch (e) { /* gradient or bitmap — leave default colors */ }
        } else if (color.colorType === 1 || color.colorType === 2) {
            // Mark gradients visually
            item.setText("   " + label + "  [gradient]");
        }

        listWidget.addItem(item);
    }

    // Select All / Select None
    var selBtnLayout  = new QHBoxLayout();
    var selectAllBtn  = new QPushButton("Select All");
    var selectNoneBtn = new QPushButton("Select None");
    selBtnLayout.addWidget(selectAllBtn, 0, Qt.AlignTop);
    selBtnLayout.addWidget(selectNoneBtn, 0, Qt.AlignTop);

    listLayout.addWidget(listWidget, 0, Qt.AlignTop);
    listLayout.addLayout(selBtnLayout);
    listGroup.setLayout(listLayout);
    mainLayout.addWidget(listGroup, 0, Qt.AlignTop);

    // ── OK / Cancel ──────────────────────────────────────────────────────────
    var okCancelLayout = new QHBoxLayout();
    okCancelLayout.addStretch();
    var cancelBtn = new QPushButton("Cancel");
    var okBtn     = new QPushButton("OK");
    okCancelLayout.addWidget(cancelBtn, 0, Qt.AlignTop);
    okCancelLayout.addWidget(okBtn, 0, Qt.AlignTop);
    mainLayout.addLayout(okCancelLayout);

    dialog.setLayout(mainLayout);

    // Connections
    selectAllBtn.clicked.connect(function () {
        for (var i = 0; i < listWidget.count; i++)
            listWidget.item(i).setCheckState(Qt.Checked);
    });
    selectNoneBtn.clicked.connect(function () {
        for (var i = 0; i < listWidget.count; i++)
            listWidget.item(i).setCheckState(Qt.Unchecked);
    });
    okBtn.clicked.connect(dialog,     dialog.accept);
    cancelBtn.clicked.connect(dialog, dialog.reject);

    var execResult = dialog.exec();
    MessageLog.trace("dialog.exec() returned: " + execResult + " (Accepted=1, Rejected=0)");
    if (execResult !== 1) return null;

    var selectedIndices = [];
    for (var i = 0; i < listWidget.count; i++) {
        if (listWidget.item(i).checkState() === Qt.Checked)
            selectedIndices.push(i);
    }

    return {
        assetName:       (nameInput.text.trim() || defaultName),
        selectedIndices: selectedIndices
    };
}


// ─────────────────────────────────────────────────────────────────────────────
//  Helper functions  (adapted from PAL_Copy_Palette_With_New_Color_IDs)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Return Colour Selector nodes that reference any of the selected colors.
 */
function _getRelativeColorSelectors(palette, selectedIndices) {
    var colorIdList = [];
    for (var i = 0; i < selectedIndices.length; i++)
        colorIdList.push(palette.getColorByIndex(selectedIndices[i]).id);

    var relativeCSNodes = [];
    var csNodes = node.getNodes(["TbdColorSelector"]);

    for (var n in csNodes) {
        for (var idx = 0; idx < colorIdList.length; idx++) {
            var csAttr = node.getTextAttr(csNodes[n], 1, "selectedcolors");
            if (csAttr.indexOf(colorIdList[idx]) !== -1) {
                relativeCSNodes.push(csNodes[n]);
                break;
            }
        }
    }
    return relativeCSNodes;
}


/**
 * Swap old color ID for new color ID inside Colour Selector nodes.
 */
function _recolorColorSelectorItems(OGId, newId, CS) {
    for (var n in CS) {
        var csAttr    = node.getTextAttr(CS[n], 1, "selectedcolors");
        var colorArray = JSON.parse(csAttr);
        for (var c in colorArray) {
            if (colorArray[c].colorId === OGId)
                colorArray[c].colorId = newId;
        }
        node.setTextAttr(CS[n], "selectedcolors", 1, JSON.stringify(colorArray));
    }
}


/**
 * Return all {node, frame} draw keys that use a given color ID.
 */
function _getNodeColors(colorId) {
    var nodes   = node.getNodes(["READ"]);
    var drawKey = [];

    for (var n in nodes) {
        var useTiming  = node.getAttr(nodes[n], 1, "drawing.elementMode").boolValue();
        var drawColumn = node.linkedColumn(nodes[n],
            useTiming ? "drawing.element" : "drawing.customName.timing");
        var frames = _getFrames(drawColumn);

        for (var f in frames) {
            var drawingColors = DrawingTools.getDrawingUsedColors({ node: nodes[n], frame: frames[f] });
            for (var c in drawingColors) {
                if (drawingColors[c] === colorId)
                    drawKey.push({ node: nodes[n], frame: frames[f] });
            }
        }
    }
    return drawKey;
}


/**
 * Return one representative frame per unique cel in a drawing column.
 */
function _getFrames(drawColumn) {
    var checkedCels = [], frameList = [];
    for (var f = 1; f <= frame.numberOf(); f++) {
        var curCel = column.getEntry(drawColumn, 1, f);
        if (checkedCels.indexOf(curCel) === -1) {
            checkedCels.push(curCel);
            frameList.push(f);
        }
    }
    return frameList;
}
