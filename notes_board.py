from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class NotesBoardDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notes Board")

        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)

        self.status_label = QLabel("Status: Inactive")
        layout.addWidget(self.status_label)

        self.toggle_button = QPushButton("Activate Notes Board")
        self.toggle_button.clicked.connect(self.toggle_notes_board)
        layout.addWidget(self.toggle_button)

        self.setWidget(main_widget)
        self.is_active = False
        self.notes_layer = None

    def canvasChanged(self, canvas):
        pass

    def toggle_notes_board(self):
        if self.is_active:
            self.deactivate_notes_board()
        else:
            self.activate_notes_board()

    def activate_notes_board(self):
        app = Krita.instance()
        doc = app.activeDocument()
        
        if not doc:
            self.status_label.setText("Error: There is no active document")
            return

        # Crear la capa de notas
        self.notes_layer = doc.createNode("notes", "paintlayer")
        doc.rootNode().addChildNode(self.notes_layer, None)
        doc.setActiveNode(self.notes_layer)
        self.status_label.setText("Status: Active")
        self.is_active = True
        self.toggle_button.setText("Deactivate Notes Board")

    def deactivate_notes_board(self):
        app = Krita.instance()
        doc = app.activeDocument()
        
        if not doc or not self.notes_layer:
            self.status_label.setText("Error: No active document or notes layer")
            return

        result = QMessageBox.question(None, "Deactivate Notes Board", "¿Do you want to contiunue?", QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            # Copiar la capa de notas como referencia y luego eliminarla
            self.copy_as_reference(self.notes_layer)
            doc.rootNode().removeChildNode(self.notes_layer)
            self.notes_layer = None
            self.status_label.setText("Status: Inactive")
            self.is_active = False
            self.toggle_button.setText("Activate Notes Board")
        else:
            doc.setActiveNode(self.notes_layer)

    def copy_as_reference(self, layer):
        """Función para copiar el contenido de una capa como referencia."""
        doc = Krita.instance().activeDocument()
        if doc and layer:
            # Seleccionamos toda la capa de notas y la copiamos como referencia
            selection = Selection()
            selection.selectAll(layer, 255)
            selection.copy(layer)
            Krita.instance().action('paste_as_reference').trigger()

class NotesBoard(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("notes_board", DockWidgetFactoryBase.DockRight, NotesBoardDocker))
Krita.instance().addExtension(NotesBoard(Krita.instance()))
