import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pyvis import network as net
from data_interface import Ui_MainWindow as Data_MainWindow
from main_interface import Ui_MainWindow
from qt_material import apply_stylesheet
import sys
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QCheckBox, QGraphicsScene, \
    QGraphicsView, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QFileSystemWatcher
from mpl_toolkits.mplot3d import Axes3D

import os
import matplotlib
from PyQt6.QtWebEngineCore import QWebEngineSettings
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from QueryIntegrationUIKiwi import initializeRetrieval, retrievePaintings
from ColorComparison import get_main_colors
matplotlib.use('QtAgg')
url = []

currentImagePath = ""

# Global variable to store the last clicked QLabel
last_clicked_label = None

painting_dic = {}
painting_info_list = []


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
        self.webview.load(QUrl.fromLocalFile(
            '/Users/yeyuan/Desktop/Multimedia-Analytics-master/dist/index.html'))
        layout = QHBoxLayout(self.frame)
        layout.addWidget(self.webview)
        layout.setContentsMargins(0, 0, 0, 0)

        self.myColorLayout = None

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
            # Adjust spacing between images if needed
            grid_layout.setSpacing(10)
            self.myImageGridLayout = grid_layout

        # Set the number of columns for the grid layout
        num_columns = 3
        for index, image_path in enumerate(url):
            # Create a QLabel for the image
            label = ClickableLabel(image_path)
            # Adjust the size of the QLabel as desired
            label.setFixedSize(150, 150)
            # Add a border to the QLabel if desired
            label.setStyleSheet("border: 1px solid gray")
            label.clicked.connect(self.label_clicked)

            # Load and set the image pixmap for the QLabel
            pixmap = QPixmap(image_path)
            print(pixmap.isNull())
            label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
            # Enable scaling of the image within the QLabel
            label.setScaledContents(True)

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
        self.showImageText()
        print("show text")
        self.drawPieChart()

    def handlUserInput(self):
        input_text = self.searchEdit.text()

        return input_text

    def queryOnImages(self, df, model, loaded_embeddings, neigh):
        global painting_dic
        global url
        global painting_info_list

        userQuery = self.handlUserInput()
        retrievedPaintings = retrievePaintings(userInput=userQuery, df=df, model=model,
                                               loaded_embeddings=loaded_embeddings,
                                               neigh=neigh)
        painting_dic = retrievedPaintings
        print(painting_dic)
        if painting_dic is None:
            self.reloadImages(False)
            return
        file_paths = painting_dic['image_paths']
        processed_paths = [path.replace('images/', '') for path in file_paths]
        # print(painting_dic['image_paths'])
        # print(processed_paths)
        url = []
        painting_info_list = []
        load_image_paths("./images", url, processed_paths)

        dates_list = painting_dic['dates']
        names_list = painting_dic['names']
        nationalities_list = painting_dic['nationalities']
        styles_list = painting_dic['styles']
        tags_list = painting_dic['tags']
        medias_list = painting_dic['medias']
        titles_list = painting_dic['titles']

        print("done")

        for i in range(0, len(processed_paths)):
            new_dict = {}
            new_dict['path'] = str(processed_paths[i])
            new_dict['date'] = str(int(dates_list[i]))
            new_dict['name'] = str(names_list[i])
            new_dict['nationality'] = str(nationalities_list[i])
            new_dict['style'] = str(styles_list[i])
            new_dict['tag'] = str(tags_list[i])
            new_dict['media'] = str(medias_list[i])
            new_dict['title'] = str(titles_list[i])
            painting_info_list.append(new_dict)

        print(painting_info_list)
        self.textBrowser.setText("")
        self.reloadImages(True)
        self.webview.load(QUrl.fromLocalFile(
            '/Users/yeyuan/Desktop/Multimedia-Analytics-master/dist/index.html'))

    def showImageText(self):
        key_value_pairs = []
        for dict in painting_info_list:
            if dict['path'] in currentImagePath:
                keys = list(dict.keys())
                values = list(dict.values())

                for i in range(1, len(keys)):
                    key = keys[i]
                    value = values[i]
                    key_value_pairs.append(f"{key}: {value}")

                key_value_pairs = "\n\n".join(key_value_pairs)

        text = ""
        for i in key_value_pairs:
            text += i

        self.textBrowser.setText(text)
        font = self.textBrowser.font()
        font.setPointSize(14)  # Set the desired font size
        self.textBrowser.setFont(font)

    def drawPieChart(self):
        self.removeColorGraph()

        # Extract main colors from the image
        colors, counts = get_main_colors(currentImagePath)
        # Normalize
        proportions = counts / counts.sum()
        fig = Figure(figsize=(5, 5))
        if self.myColorLayout is None:
            layout = QVBoxLayout(self.frame_2)
            self.myColorLayout = layout

        sorted_indices = np.argsort(-proportions)
        sorted_colors = colors[sorted_indices]
        sorted_proportions = proportions[sorted_indices]

        # Select the top 5 colors
        top_colors = sorted_colors[:6]
        top_proportions = sorted_proportions[:6]
        cmap = plt.cm.get_cmap("tab20c", len(top_colors))

        ax = fig.add_subplot(111)
        explode_index = np.argmax(top_proportions)

        # Create an explode array with zeros for all slices except the one with the highest proportion
        explode = np.zeros(len(top_proportions))
        explode[explode_index] = 0.1
        ax.pie(top_proportions, explode=explode, autopct='%1.1f%%', colors=cmap(np.arange(len(top_colors))),
               shadow=True, startangle=45)
        ax.set_title("The Top 6 Colors of the Left Paintings")
        fig.savefig("./color.png")
        # if self.frame_2.layout() is None:
        # layout = QVBoxLayout(self.frame_2)
        print(self.frame_2 is None)
        # Remove previous widgets from the layout
        # for i in reversed(range(self.frame_2.layout().count())):

        canvas = FigureCanvas(fig)
        # widget = self.frame_2.layout().itemAt(0).widget()
        # if widget is not None:
        #     widget.deleteLater()

        self.myColorLayout.addWidget(canvas)

    def removeColorGraph(self):
        if self.myColorLayout is not None:
            widget = self.myColorLayout.itemAt(0).widget()
            if widget is not None:
                widget.deleteLater()


class DataWindow(QMainWindow, Data_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.myLayout = None
        self.myImageLabel = None
        self.myColorLayout = None

        self.webview = QWebEngineView(self.frame_3)
        self.webview.setZoomFactor(0.7)
        self.webview.load(QUrl.fromLocalFile(
            'G:\\Desktop\\multimedia_project\\map\\index.html'))
        layout = QHBoxLayout(self.frame_3)
        layout.addWidget(self.webview)
        layout.setContentsMargins(1, 1, 1, 1)

    # def loadImage(self):
    #     global currentImagePath
    #
    #     if self.myLayout is None:
    #         layout = QHBoxLayout(self.frame)
    #         self.myLayout = layout
    #
    #     image_label = QLabel()
    #     image_path = currentImagePath  # Replace with the actual path to your image
    #     print(currentImagePath)
    #     pixmap = QPixmap(image_path)
    #     image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
    #                                         Qt.TransformationMode.SmoothTransformation))
    #     # Enable scaling of the image within the QLabel
    #     image_label.setScaledContents(True)
    #
    #     self.myLayout.addWidget(image_label)
    #     self.myImageLabel = image_label
    #     print(self.myLayout.count())

    # def removeImage(self):
    #     self.frame.layout().removeWidget(self.myImageLabel)
    #     widget = self.myColorLayout.itemAt(0).widget()
    #     if widget is not None:
    #         widget.deleteLater()

    # def drawPieChart(self):
    #     # Extract main colors from the image
    #     colors, counts = get_main_colors(currentImagePath)
    #     # Normalize
    #     proportions = counts / counts.sum()
    #     fig = Figure(figsize=(5, 5))
    #     if self.myColorLayout is None:
    #         layout = QVBoxLayout(self.frame_2)
    #         self.myColorLayout = layout
    #
    #     sorted_indices = np.argsort(-proportions)
    #     sorted_colors = colors[sorted_indices]
    #     sorted_proportions = proportions[sorted_indices]
    #
    #     # Select the top 5 colors
    #     top_colors = sorted_colors[:6]
    #     top_proportions = sorted_proportions[:6]
    #     cmap = plt.cm.get_cmap("tab20c", len(top_colors))
    #
    #     ax = fig.add_subplot(111)
    #     explode_index = np.argmax(top_proportions)
    #
    # # Create an explode array with zeros for all slices except the one with the highest proportion
    #     explode = np.zeros(len(top_proportions))
    #     explode[explode_index] = 0.1
    #     ax.pie(top_proportions, explode= explode, autopct='%1.1f%%', colors=cmap(np.arange(len(top_colors))), shadow=True,startangle=45)
    #     ax.set_title("The Top 6 Colors of the Left Paintings")
    #     fig.savefig("./color.png")
    #     # if self.frame_2.layout() is None:
    #     # layout = QVBoxLayout(self.frame_2)
    #     print(self.frame_2 is None)
    #     # Remove previous widgets from the layout
    #     # for i in reversed(range(self.frame_2.layout().count())):
    #
    #
    #
    #
    #     canvas = FigureCanvas(fig)
    #     # widget = self.frame_2.layout().itemAt(0).widget()
    #     # if widget is not None:
    #     #     widget.deleteLater()
    #
    #     self.myColorLayout.addWidget(canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    df, model, loaded_embeddings, neigh = initializeRetrieval()
    print(url)
    myWindow = MyWindow()
    dataWindow = DataWindow()

    myWindow.pushButton_2.clicked.connect(
        lambda: {myWindow.close(),  dataWindow.show()}
    )

    myWindow.searchButton.clicked.connect(
        lambda: {myWindow.queryOnImages(df, model, loaded_embeddings, neigh)}
    )

    dataWindow.pushButton.clicked.connect(
        lambda: {dataWindow.close(), myWindow.show()}
    )
    extra = {

        # Density Scale
        'density_scale': '-1',
    }
    apply_stylesheet(app, theme='dark_blue.xml', extra=extra)
    sys.exit(app.exec())
