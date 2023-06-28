import os
import matplotlib
from PyQt6.QtWebEngineCore import QWebEngineSettings

from QueryIntegrationUIKiwi import initializeRetrieval, retrievePaintings

matplotlib.use('QtAgg')
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QFileSystemWatcher
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QCheckBox, QGraphicsScene, \
    QGraphicsView, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
from qt_material import apply_stylesheet
from main_interface import Ui_MainWindow
from data_interface import Ui_MainWindow as Data_MainWindow
from pyvis import network as net
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

url = []

currentImagePath = ""

# Global variable to store the last clicked QLabel
last_clicked_label = None

painting_dic = {}

def load_image_paths(folder_path, url_list, target_list):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            file_path = os.path.join(folder_path, filename)
            if filename in target_list:
                url_list.append(file_path)


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def get_image_path(self):
        return self.image_path

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.myImageGridLayout = None

        self.showImages()
        # self.showLabels()

        self.webview = QWebEngineView(self.frame)
        self.webview.load(QUrl.fromLocalFile('G:\Desktop\multimedia_project\dist\index.html'))
        layout = QHBoxLayout(self.frame)
        layout.addWidget(self.webview)
        layout.setContentsMargins(0, 0, 0, 0)

        # layout = QVBoxLayout()
        #
        # # Create a NetworkX graph
        # self.graph = nx.Graph()
        # self.graph.add_nodes_from([1, 2, 3])
        # self.graph.add_edges_from([(1, 2), (2, 3), (3, 1)])
        #
        # # Create a Matplotlib Figure and Axis
        # self.figure = plt.figure()
        # self.axis = self.figure.add_subplot(111)
        #
        # # Create a FigureCanvas
        # self.canvas = FigureCanvas(self.figure)
        # self.canvas.updateGeometry()
        #
        # layout.addWidget(self.canvas)
        # self.frame.setLayout(layout)
        #
        # # Call the plot method to draw the graph
        # self.plot()

        self.show()

    # def plot(self):
    #     self.axis.clear()
    #
    #     # Draw the network graph
    #     nx.draw(self.graph, with_labels=True, ax=self.axis)
    #
    #     # Update the canvas
    #     self.canvas.draw()

    # def showLabels(self):
    #     grid_layout = QGridLayout(self.scrollAreaWidgetContents_2)
    #     grid_layout.setSpacing(30)  # Adjust spacing between images if needed
    #
    #     # Set the number of columns for the grid layout
    #     num_columns = 3
    #
    #     for i in range(18):
    #         checkbox = QCheckBox("tree", self.scrollAreaWidgetContents_2)
    #         checkbox.setStyleSheet("border-radius: 50%;")
    #         checkbox.setAutoFillBackground(True)
    #
    #         row = i // num_columns
    #         column = i % num_columns
    #
    #         # Add the checkbox to the grid layout
    #         grid_layout.addWidget(checkbox, row, column)

    def showImages(self):
        if self.myImageGridLayout is None:
            grid_layout = QGridLayout(self.scrollAreaWidgetContents)
            grid_layout.setSpacing(10)  # Adjust spacing between images if needed
            self.myImageGridLayout = grid_layout

        # Set the number of columns for the grid layout
        num_columns = 3
        for index, image_path in enumerate(url):
            # Create a QLabel for the image
            label = ClickableLabel(image_path)
            label.setFixedSize(150, 150)  # Adjust the size of the QLabel as desired
            label.setStyleSheet("border: 1px solid gray")  # Add a border to the QLabel if desired
            label.clicked.connect(self.label_clicked)

            # Load and set the image pixmap for the QLabel
            pixmap = QPixmap(image_path)
            print(pixmap.isNull())
            label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
            label.setScaledContents(True)  # Enable scaling of the image within the QLabel

            # Calculate the row and column position for the current image
            row = index // num_columns
            column = index % num_columns
            # Add the QLabel to the grid layout at the calculated position
            self.myImageGridLayout.addWidget(label, row, column)

    def reloadImages(self, hasImage):
        global currentImagePath
        global last_clicked_label
        last_clicked_label = None
        currentImagePath = ""
        while self.myImageGridLayout.count():
            item = self.myImageGridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if hasImage:
            self.showImages()

    def label_clicked(self):
        global last_clicked_label
        global currentImagePath

        label = self.sender()

        if last_clicked_label is not None:
            last_clicked_label.setStyleSheet("border: 1px solid gray")

        border_color = QColor(255, 0, 0)  # RGB values for red
        border_style = f"border: 4px solid {border_color.name()};"
        label.setStyleSheet(border_style)

        currentImagePath = label.get_image_path()
        # print(currentImagePath)

        last_clicked_label = label

    def handlUserInput(self):
        input_text = self.searchEdit.text()

        return input_text

    def queryOnImages(self, df, model, loaded_embeddings, neigh):
        global painting_dic
        global url

        userQuery = self.handlUserInput()
        retrievedPaintings = retrievePaintings(userInput=userQuery, df=df, model=model, loaded_embeddings=loaded_embeddings,
                                               neigh=neigh)
        painting_dic = retrievedPaintings
        if painting_dic is None:
            self.reloadImages(False)
            return
        file_paths = painting_dic['image_paths']
        processed_paths = [path.replace('images/', '') for path in file_paths]
        print(painting_dic['image_paths'])
        print(processed_paths)
        url = []
        load_image_paths("G:\Desktop\multimedia_project\images", url, processed_paths)
        self.reloadImages(True)
        self.webview.load(QUrl.fromLocalFile('G:\Desktop\multimedia_project\dist\index.html'))


class DataWindow(QMainWindow, Data_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.myLayout = None
        self.myImageLabel = None

    def loadImage(self):
        global currentImagePath

        if self.myLayout is None:
            layout = QHBoxLayout(self.frame)
            self.myLayout = layout

        image_label = QLabel()
        image_path = currentImagePath  # Replace with the actual path to your image
        print(currentImagePath)
        pixmap = QPixmap(image_path)
        image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        image_label.setScaledContents(True)  # Enable scaling of the image within the QLabel

        self.myLayout.addWidget(image_label)
        self.myImageLabel = image_label
        print(self.myLayout.count())

    def removeImage(self):
        self.frame.layout().removeWidget(self.myImageLabel)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    df, model, loaded_embeddings, neigh = initializeRetrieval()
    print(url)
    myWindow = MyWindow()
    dataWindow = DataWindow()

    myWindow.pushButton_2.clicked.connect(
        lambda: {myWindow.close(), dataWindow.show(), dataWindow.loadImage()}
    )

    myWindow.searchButton.clicked.connect(
        lambda: { myWindow.queryOnImages(df, model, loaded_embeddings, neigh)}
    )

    dataWindow.pushButton.clicked.connect(
        lambda: {dataWindow.removeImage(), dataWindow.close(), myWindow.show()}
    )
    extra = {

        # Density Scale
        'density_scale': '-1',
    }
    apply_stylesheet(app, theme='dark_blue.xml', extra=extra)
    sys.exit(app.exec())
