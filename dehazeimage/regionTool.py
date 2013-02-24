
from qgis.core import *
from qgis.gui import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

cursor = QCursor(QPixmap(["16 16 3 1","# c None","a c #000000",". c #ffffff",".###############","...#############",".aa..###########","#.aaa..a.a.a.a.#","#.aaaaa..#####a#","#a.aaaaaa..###.#","#..aaaaaa...##a#","#a.aaaaa.#####.#","#.#.aaaaa.####a#","#a#.aa.aaa.###.#","#.##..#..aa.##a#","#a##.####.aa.#.#","#.########.aa.a#","#a#########.aa..","#.a.a.a.a.a..a.#","#############.##"]))

class regionTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.dragging=False
        self.selectRect = QRect()
        self.rubberBand = 0
        self.canvas=canvas
        self.ll = None
        self.ur = None
        self.o = QObject()

    def canvasPressEvent(self,event):
        print "got an event"
        self.selectRect.setRect(event.pos().x(),event.pos().y(),0,0)

    def canvasMoveEvent(self,event):
        if not event.buttons() == Qt.LeftButton:
            return
        if not self.dragging:
            self.dragging=True
            self.rubberBand = QRubberBand(QRubberBand.Rectangle,self.canvas)
        self.selectRect.setBottomRight(event.pos())
        self.rubberBand.setGeometry(self.selectRect.normalized())
        self.rubberBand.autoFillBackground()
        self.rubberBand.show()

    def canvasReleaseEvent(self,e):
        if not self.dragging:
            return
        self.rubberBand.hide()
        self.selectRect.setRight(e.pos().x())
        self.selectRect.setBottom(e.pos().y())
        transform = self.canvas.getCoordinateTransform()
        ll = transform.toMapCoordinates(self.selectRect.left(),self.selectRect.bottom())
        ur = transform.toMapCoordinates(self.selectRect.right(),self.selectRect.top())
        self.bb = QgsRectangle(
            QgsPoint(ll.x(),ll.y()),
            QgsPoint(ur.x(),ur.y())
            )
        self.o.emit(SIGNAL("finished(PyQt_PyObject)"),self.bb)
        #self.msg.hide()
        
    def activate(self):
        # self.msg = QLabel("Draw rectangle on canvas")
        # self.msg.show()
        self.canvas.setCursor(cursor)

    def deactivate(self):
        # self.rubberBand.hide()
        print "Deactivate!"


    def isZoomTool(self):
        return False





