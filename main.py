from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QPushButton, QLabel, QLineEdit
from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsPointXY,
    QgsFeature,
    QgsWkbTypes,
    Qgis,
    QgsVectorLayer
)
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.utils import iface

class SelectAreaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Doğal Gaz Hat ve Boru Seçimi")

        self.polygon_path_edit = QLineEdit()
        self.line_path_edit = QLineEdit()

        self.select_polygon_button = QPushButton("Poligon Seç")
        self.select_polygon_button.clicked.connect(self.select_polygon)

        self.select_line_button = QPushButton("Çizgi Seç")
        self.select_line_button.clicked.connect(self.select_line)

        self.upload_layers_button = QPushButton("Aktar")
        self.upload_layers_button.clicked.connect(self.upload_layers)

        self.select_area_button = QPushButton("Alan Seç")
        self.select_area_button.setEnabled(False)
        self.select_area_button.clicked.connect(self.select_area)

        self.add_lines_button = QPushButton("Line Ekle")
        self.add_lines_button.setEnabled(False)
        self.add_lines_button.clicked.connect(self.add_lines)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Poligon Shapefile:"))
        layout.addWidget(self.polygon_path_edit)
        layout.addWidget(self.select_polygon_button)
        layout.addWidget(QLabel("Çizgi Shapefile:"))
        layout.addWidget(self.line_path_edit)
        layout.addWidget(self.select_line_button)
        layout.addWidget(self.upload_layers_button)
        layout.addWidget(self.select_area_button)
        layout.addWidget(self.add_lines_button)
        self.setLayout(layout)

        self.polygon_layer = None
        self.line_layer = None
        self.selectTool = None

    def select_polygon(self):
        polygon_path, _ = QFileDialog.getOpenFileName(self, "Poligon Shapefile Seçin", "", "Shapefiles (*.shp)")
        if polygon_path:
            self.polygon_path_edit.setText(polygon_path)

    def select_line(self):
        line_path, _ = QFileDialog.getOpenFileName(self, "Çizgi Shapefile Seçin", "", "Shapefiles (*.shp)")
        if line_path:
            self.line_path_edit.setText(line_path)

    def upload_layers(self):
        polygon_path = self.polygon_path_edit.text()
        line_path = self.line_path_edit.text()

        if not polygon_path or not line_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen poligon ve çizgi shapefile dosyalarını seçin.")
            return

        self.polygon_layer = QgsVectorLayer(polygon_path, "Poligon Katmanı", "ogr")
        self.line_layer = QgsVectorLayer(line_path, "Çizgi Katmanı", "ogr")

        if not self.polygon_layer.isValid() or not self.line_layer.isValid():
            QMessageBox.critical(self, "Hata", "Shapefile dosyaları yüklenemedi.")
            return

        QgsProject.instance().addMapLayer(self.polygon_layer)
        QgsProject.instance().addMapLayer(self.line_layer)

        self.selectTool = SelectAreaTool(iface.mapCanvas())
        self.selectTool.set_layers(self.polygon_layer, self.line_layer)
        self.selectTool.set_dialog(self)

        self.select_area_button.setEnabled(True)
        self.add_lines_button.setEnabled(True)
        iface.messageBar().pushMessage("Bilgi", "Katmanlar başarıyla yüklendi.", level=Qgis.Info)

    def select_area(self):
        iface.mapCanvas().setMapTool(self.selectTool)
        iface.messageBar().pushMessage("Bilgi", "Lütfen poligonları seçin. İşlemi bitirmek için sağ tıklayın.", level=Qgis.Info)

    def add_lines(self):
        if self.selectTool:
            added_lines_count = self.selectTool.processSelectedArea()
            QMessageBox.information(self, "Bilgi", f"İşlem tamamlandı ve harita güncellendi. {added_lines_count} line eklendi.")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce poligon ve çizgi shapefile dosyalarını seçin ve aktarın.")

class SelectAreaTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.rubberBand = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(2)
        self.rubberBand.setFillColor(Qt.transparent)
        self.points = []
        self.polygon_layer = None
        self.line_layer = None
        self.dialog = None

    def set_layers(self, polygon_layer, line_layer):
        self.polygon_layer = polygon_layer
        self.line_layer = line_layer

    def set_dialog(self, dialog):
        self.dialog = dialog

    def canvasPressEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.points.append(point)
        self.rubberBand.addPoint(point, True)
        iface.messageBar().pushMessage("Bilgi", f"Nokta eklendi: {point}", level=Qgis.Info)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rubberBand.closePoints()
            self.deactivate()
            iface.actionPan().trigger()
            iface.messageBar().clearWidgets()
            iface.messageBar().pushMessage("Bilgi", "Alan seçimi tamamlandı. Şimdi 'Line Ekle' butonuna tıklayabilirsiniz.", level=Qgis.Info)
            if self.dialog:
                self.dialog.raise_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.rubberBand.reset(True)
            self.points = []
            iface.messageBar().pushMessage("Bilgi", "Seçim sıfırlandı", level=Qgis.Info)

    def processSelectedArea(self):
        iface.messageBar().pushMessage("Bilgi", "Seçili alan işleniyor", level=Qgis.Info)
        if len(self.points) < 3:
            QMessageBox.warning(None, "Uyarı", "Geçerli bir poligon çizmediniz. Lütfen alanı tekrar seçin.")
            return 0

        polygon = QgsGeometry.fromPolygonXY([self.points])

        if not self.polygon_layer or not self.line_layer:
            QMessageBox.critical(None, "Hata", "Katmanlar yüklenemedi.")
            return 0

        if self.polygon_layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            QMessageBox.critical(None, "Hata", "Seçilen katman bir poligon katmanı değil. Lütfen doğru katmanı seçtiğinizden emin olun.")
            return 0

        self.line_layer.startEditing()

        added_lines_count = 0
        for polygon_feature in self.polygon_layer.getFeatures():
            polygon_geometry = polygon_feature.geometry()

            if polygon_geometry.isMultipart():
                polygons = polygon_geometry.asMultiPolygon()
            else:
                polygons = [polygon_geometry.asPolygon()]

            min_distance = float('inf')
            nearest_line = None
            start_point = None
            end_point = None

            for poly in polygons:
                for i in range(len(poly[0]) - 1):
                    point1 = QgsPointXY(poly[0][i])
                    point2 = QgsPointXY(poly[0][i + 1])
                    midpoint = QgsPointXY((point1.x() + point2.x()) / 2, (point1.y() + point2.y()) / 2)
                    for line_feature in self.line_layer.getFeatures():
                        line_geometry = line_feature.geometry()
                        distance = line_geometry.distance(QgsGeometry.fromPointXY(midpoint))
                        if distance < min_distance:
                            min_distance = distance
                            nearest_line = line_feature
                            start_point = point1
                            end_point = point2

            if nearest_line and start_point and end_point:
                line_geometry = nearest_line.geometry()
                midpoint = QgsPointXY((start_point.x() + end_point.x()) / 2, (start_point.y() + end_point.y()) / 2)
                nearest_point = line_geometry.nearestPoint(QgsGeometry.fromPointXY(midpoint)).asPoint()
                new_line = QgsGeometry.fromPolylineXY([midpoint, QgsPointXY(nearest_point)])
                new_feature = QgsFeature(self.line_layer.fields())
                new_feature.setGeometry(new_line)
                new_feature.setAttributes(nearest_line.attributes())
                self.line_layer.addFeature(new_feature)

                added_lines_count += 1

                # Add vertex at the intersection point
                self.add_vertex_at_intersection(self.line_layer, nearest_line, new_line)

        self.line_layer.commitChanges()
        self.line_layer.updateExtents()
        iface.mapCanvas().refreshAllLayers()
        iface.messageBar().pushMessage("Bilgi", f"İşlem tamamlandı ve harita güncellendi. {added_lines_count} line eklendi.", level=Qgis.Info)
        return added_lines_count

    def add_vertex_at_intersection(self, layer, line_feature, new_line_geometry):
        intersection = line_feature.geometry().intersection(new_line_geometry)
        if intersection.isEmpty():
            return
        if intersection.type() == QgsWkbTypes.PointGeometry:
            intersection_point = intersection.asPoint()
            line_geometry = line_feature.geometry()
            line_geometry.insertVertex(intersection_point.x(), intersection_point.y(), line_geometry.closestVertex(intersection_point)[1])
            line_feature.setGeometry(line_geometry)
            layer.updateFeature(line_feature)
        elif intersection.type() == QgsWkbTypes.MultiPoint:
            for point in intersection.asMultiPoint():
                line_geometry = line_feature.geometry()
                line_geometry.insertVertex(point.x(), point.y(), line_geometry.closestVertex(point)[1])
                line_feature.setGeometry(line_geometry)
                layer.updateFeature(line_feature)

class SelectAreaPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction("Alan Seç", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Alan Seçme Eklentisi", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&Alan Seçme Eklentisi", self.action)

    def run(self):
        self.dialog = SelectAreaDialog(self.iface.mainWindow())
        self.dialog.show()
