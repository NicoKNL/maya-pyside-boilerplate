import os
import sys

import xml.etree.ElementTree as xml
from cStringIO import StringIO

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import pysideuic
import shiboken

import maya.OpenMayaUI
import maya.cmds as mc


def get_pyside_class(ui_file):
    parsed = xml.parse(ui_file)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(ui_file, 'r') as f:
        o = StringIO()
        frame = {}

        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        form_class = frame['Ui_{0}'.format(form_class)]
        base_class = eval('QtGui.{0}'.format(widget_class))

    return form_class, base_class


def wrapinstance(ptr, base=None):
   if ptr is None:
      return None

   ptr = long( ptr ) #Ensure type
   if globals().has_key( 'shiboken' ):
      if base is None:
         qObj = shiboken.wrapInstance( long( ptr ), QtCore.QObject )
         metaObj = qObj.metaObject()
         cls = metaObj.className()
         superCls = metaObj.superClass().className()
         if hasattr( QtGui, cls ):
            base = getattr( QtGui, cls )

         elif hasattr( QtGui, superCls ):
            base = getattr( QtGui, superCls )

         else:
            base = QtGui.QWidget

      return shiboken.wrapInstance( long( ptr ), base )

   elif globals().has_key( 'sip' ):
      base = QtCore.QObject

      return sip.wrapinstance( long( ptr ), base )

   else:
      return None


def get_maya_window():
    maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
    maya_window = wrapinstance(long(maya_window_util), QtGui.QWidget)

    return maya_window

WINDOW_TITLE = "Example ui"
WINDOW_NAME = "example"

TOOLPATH = os.path.dirname(__file__)
UI_FILE = os.path.join(TOOLPATH, "Example.ui")
UI_OBJECT, BASE_CLASS = get_pyside_class(UI_FILE)


class Example(BASE_CLASS, UI_OBJECT):
    def __init__(self, parent=get_maya_window()):
        super(Example, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle(WINDOW_TITLE)

        self.helloworld = "Hello World!"

        self.btn_sayhello.clicked.connect(self.hello_world)

        self.show()

    def hello_world(self):
        print self.helloworld


def show():
    if mc.window(WINDOW_NAME, exists=True, q=True):
        mc.deleteUI(WINDOW_NAME)

    Example()