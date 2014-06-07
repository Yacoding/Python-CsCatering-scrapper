import threading
import time
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import *
import sys
from works.CsTest import CsTest
from works.NisbetCat import NisbetCat
from works.NisbetProduct import NisbetProduct
from works.CsBrands import CsBrands
from works.CsCat import CsCat
from works.CsProduct import CsProduct

__author__ = 'Rabbi'

class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.createGui()

    def createGui(self):
        self.btnScrapCat = QPushButton('&Scrap Category')
        self.btnScrapCat.clicked.connect(self.scrapCategoryAction)
        self.browserCat = QTextBrowser()

        self.btnScrapProduct = QPushButton('&Scrap Product')
        self.btnScrapProduct.clicked.connect(self.scrapProductAction)
        self.browserProduct = QTextBrowser()

        self.btnScrapBrand = QPushButton('&Scrap Brand')
        self.btnScrapBrand.clicked.connect(self.scrapBrandAction)
        self.browserBrand = QTextBrowser()

        layout = QGridLayout()
        layout.addWidget(self.btnScrapCat, 0, 0)
        layout.addWidget(self.browserCat, 0, 1)
        layout.addWidget(self.btnScrapProduct, 1, 0)
        layout.addWidget(self.browserProduct, 1, 1)
        layout.addWidget(self.btnScrapBrand, 2, 0)
        layout.addWidget(self.browserBrand, 2, 1)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('Cs Catering.')
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() - 150, screen.height() - 150)

    def scrapCategoryAction(self):
        self.csCat = CsCat()
        self.csCat.start()
        self.csCat.notifyCategory.connect(self.categoryStatus)

    def scrapProductAction(self):
#        self.csProduct = CsProduct()
        self.csProduct = CsTest()
        self.csProduct.start()
        self.csProduct.notifyProduct.connect(self.productStatus)

    def scrapBrandAction(self):
        self.csBrand = CsBrands()
        self.csBrand.start()
        self.csBrand.notifyBrand.connect(self.brandStatus)

    def categoryStatus(self, data):
        self.browserCat.append(data)

    def productStatus(self, data):
        self.browserProduct.append(data)

    def brandStatus(self, data):
        self.browserBrand.append(data)


class MainView:
    def __init__(self):
        pass

    def showMainView(self):
        app = QApplication(sys.argv)
        #        form = Form()
        form = Form()
        form.show()
        sys.exit(app.exec_())
