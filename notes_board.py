from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QPalette

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

        self.ask_before_accept_checkbox = QCheckBox("Ask before create a note")
        layout.addWidget(self.ask_before_accept_checkbox)

        self.color_button = QPushButton("Select Fill Color")
        self.color_button.clicked.connect(self.select_fill_color)
        layout.addWidget(self.color_button)

        self.color_display = QLabel()
        self.color_display.setFixedSize(50, 50)
        layout.addWidget(self.color_display)
        
        self.setWidget(main_widget)
        self.is_active = False
        self.notes_layer = None
        self.notes_layer2 = None
        self.original_width = 0
        self.original_height = 0
        self.offset_x = 0
        self.offset_y = 0
        self.fill_color = QColor(128, 128, 128, 255)  # Default gray color
        self.update_color_display()

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

        # Obtener dimensiones originales
        self.original_width = doc.width()
        self.original_height = doc.height()

        # Duplicar el tamaño del documento
        new_width = self.original_width * 2
        new_height = self.original_height * 2

        # Cambiar el tamaño del documento
        self.offset_x = int(-abs((new_width - self.original_width) / 2))
        self.offset_y = int(-abs((new_height - self.original_height) / 2))
        doc.resizeImage(self.offset_x, self.offset_y, new_width, new_height)

        # Crear la primera capa de notas
        self.notes_layer = doc.createNode("notes", "paintlayer")
        doc.rootNode().addChildNode(self.notes_layer, None)
        self.fill_layer_with_color(self.notes_layer, new_width, new_height, self.fill_color)
        #self.create_middle_hole(self.notes_layer, self.original_width, self.original_height)

        # Crear la segunda capa de notas
        self.notes_layer2 = doc.createNode("notes2", "paintlayer")
        doc.rootNode().addChildNode(self.notes_layer2, None)

        # Actualizar la proyección del documento
        doc.refreshProjection()

        doc.setActiveNode(self.notes_layer)
        self.status_label.setText("Status: Active")
        self.is_active = True
        self.toggle_button.setText("Deactivate Notes Board")

    def fill_layer_with_color(self, layer, width, height, color, rect=None):
        if rect:
            x, y, rect_width, rect_height = rect
        else:
            x, y, rect_width, rect_height = 0, 0, width, height

        # Crear una imagen temporal para dibujar
        image = QImage(rect_width, rect_height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        # Usar QPainter para rellenar el rectángulo
        painter = QPainter(image)
        painter.fillRect(0, 0, rect_width, rect_height, QColor(color.red(), color.green(), color.blue(), color.alpha()))
        painter.end()

        # Convertir la imagen a datos de píxeles y establecer en la capa
        pixel_data = image.bits().asstring(rect_width * rect_height * 4)
        layer.setPixelData(pixel_data, x, y, rect_width, rect_height)



    def fill_layer_with_color(self, layer, width, height, color, rect=None):
        if rect:
            x, y, rect_width, rect_height = rect
        else:
            x, y, rect_width, rect_height = 0, 0, width, height

        # Crear una imagen temporal para dibujar
        image = QImage(rect_width, rect_height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        # Usar QPainter para rellenar el rectángulo
        painter = QPainter(image)
        painter.fillRect(0, 0, rect_width, rect_height, QColor(color.red(), color.green(), color.blue(), color.alpha()))

        # Crear el "hueco" en el medio
        original_width = rect_width // 2
        original_height = rect_height // 2
        offset_x = (rect_width - original_width) // 2
        offset_y = (rect_height - original_height) // 2
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(offset_x, offset_y, original_width, original_height, QColor(0, 0, 0, 0))
        painter.end()

        # Convertir la imagen a datos de píxeles y establecer en la capa
        pixel_data = image.bits().asstring(rect_width * rect_height * 4)
        layer.setPixelData(pixel_data, x, y, rect_width, rect_height)

    def deactivate_notes_board(self):
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc or not self.notes_layer or not self.notes_layer2:
            self.status_label.setText("Error: No active document or notes layers")
            return

        if not self.ask_before_accept_checkbox.isChecked():
            self.process_deactivation()
        else:
            result = QMessageBox.question(None, "Deactivate Notes Board", "Do you want to continue?", QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                self.process_deactivation()
            else:
                doc.setActiveNode(self.notes_layer)

    def process_deactivation(self):
        app = Krita.instance()
        doc = app.activeDocument()

        self.copy_as_reference(self.notes_layer2)
        doc.rootNode().removeChildNode(self.notes_layer)
        doc.rootNode().removeChildNode(self.notes_layer2)
        self.notes_layer = None
        self.notes_layer2 = None

        #doc.resizeImage(-self.offset_x, -self.offset_y, self.original_width, self.original_height)
        #doc.refreshProjection()

        self.status_label.setText("Status: Inactive")
        self.is_active = False
        self.toggle_button.setText("Activate Notes Board")

    def copy_as_reference(self, layer):
        doc = Krita.instance().activeDocument()
        if doc and layer:
            offset_x, offset_y = self.offset_x, self.offset_y
            
            # Obtener los datos de la selección
            sel = Selection()
            sel.selectAll(layer, 255)

            sel.copy(layer)

            #Create a black pixel on the right corner


            pixel_data = layer.pixelData(doc.width(), doc.height(), doc.width(), doc.height())
            new_pixel_data = bytearray(pixel_data)
            
            # Agregar un píxel negro en la esquina inferior derecha
            i = ((doc.height() - 1) * doc.width() + (doc.width() - 1)) * 4
            new_pixel_data[i] = 0
            new_pixel_data[i + 1] = 0
            new_pixel_data[i + 2] = 0
            new_pixel_data[i + 3] = 255
            
            layer.setPixelData(bytes(new_pixel_data), 0, 0, doc.width(), doc.height())
            
            sel.selectAll(layer, 255)
            if sel:
                # Redimensionar la imagen con las nuevas dimensiones
                doc.resizeImage((2*self.original_width)-sel.width(), (2*self.original_height)-sel.height(), sel.width(), sel.height())
                
                # Copiar como referencia
                Krita.instance().action('paste_as_reference').trigger()
                
                doc.resizeImage( (-abs((2*self.original_width)-sel.width()))-offset_x, (-abs((2*self.original_height)-sel.height()))-offset_y, self.original_width, self.original_height)
                doc.refreshProjection()

    def select_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color
            self.update_color_display()

    def update_color_display(self):
        self.color_display.setStyleSheet(f'background-color: {self.fill_color.name()};')

class NotesBoard(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("notes_board", DockWidgetFactoryBase.DockRight, NotesBoardDocker))
Krita.instance().addExtension(NotesBoard(Krita.instance()))
