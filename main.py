import os
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QPainter
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


def load_image_paths(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            file_path = os.path.join(folder_path, filename)
            url.append(file_path)



class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.showImages()
        self.showLabels()

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


    def showLabels(self):
        grid_layout = QGridLayout(self.scrollAreaWidgetContents_2)
        grid_layout.setSpacing(30)  # Adjust spacing between images if needed

        # Set the number of columns for the grid layout
        num_columns = 3

        for i in range(18):
            checkbox = QCheckBox("tree", self.scrollAreaWidgetContents_2)
            checkbox.setStyleSheet("border-radius: 50%;")
            checkbox.setAutoFillBackground(True)

            row = i // num_columns
            column = i % num_columns

            # Add the checkbox to the grid layout
            grid_layout.addWidget(checkbox, row, column)

    def showImages(self):
        grid_layout = QGridLayout(self.scrollAreaWidgetContents)
        grid_layout.setSpacing(10)  # Adjust spacing between images if needed

        # Set the number of columns for the grid layout
        num_columns = 3
        for index, image_path in enumerate(url):
            # Create a QLabel for the image
            label = QLabel(self.scrollAreaWidgetContents)
            label.setFixedSize(150, 150)  # Adjust the size of the QLabel as desired
            label.setStyleSheet("border: 1px solid gray")  # Add a border to the QLabel if desired

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
            grid_layout.addWidget(label, row, column)

class DataWindow(QMainWindow, Data_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_image_paths('G:\Desktop\multimedia_project\images')
    print(url)
    myWindow = MyWindow()
    dataWindow = DataWindow()
    myWindow.pushButton_2.clicked.connect(
        lambda: {myWindow.close(), dataWindow.show()}
    )
    extra = {

        # Density Scale
        'density_scale': '-1',
    }
    apply_stylesheet(app, theme='dark_blue.xml', extra=extra)


    sys.exit(app.exec())


