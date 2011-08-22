import PyUnseen
from msgs import *
import pyui.locals

from pyui.renderer3d import Renderer3DBase
from pyui.desktop import getDesktop

messageMap = \
[ 
    WM_KEYDOWN,
    WM_KEYUP,
    WM_CHAR,
    WM_MOUSEMOVE,
    WM_LBUTTONDOWN,
    WM_LBUTTONUP, 
    WM_LBUTTONDBLCLK, 
    WM_RBUTTONDOWN, 
    WM_RBUTTONUP, 
    WM_RBUTTONDBLCLK,
    WM_MBUTTONDOWN,
    WM_MBUTTONUP,
    WM_MBUTTONDBLCLK,
    WM_MOUSEWHEEL,
    WM_CLOSE,
]

mouseMsgs = \
[
    WM_MOUSEMOVE,
    WM_LBUTTONDOWN,
    WM_LBUTTONUP, 
    WM_LBUTTONDBLCLK, 
    WM_RBUTTONDOWN, 
    WM_RBUTTONUP, 
    WM_RBUTTONDBLCLK,
    WM_MBUTTONDOWN,
    WM_MBUTTONUP,
    WM_MBUTTONDBLCLK,
    WM_MOUSEWHEEL,
]

VK_LBUTTON      = 0x01
VK_RBUTTON      = 0x02
VK_CANCEL       = 0x03
VK_MBUTTON      = 0x04

VK_BACK         = 0x08
VK_TAB          = 0x09

VK_CLEAR        = 0x0C
VK_RETURN       = 0x0D

VK_SHIFT        = 0x10
VK_CONTROL      = 0x11
VK_MENU         = 0x12
VK_PAUSE        = 0x13
VK_CAPITAL      = 0x14
VK_ESCAPE       = 0x1B

VK_SPACE        = 0x20
VK_PRIOR        = 0x21
VK_NEXT         = 0x22
VK_END          = 0x23
VK_HOME         = 0x24
VK_LEFT         = 0x25
VK_UP           = 0x26
VK_RIGHT        = 0x27
VK_DOWN         = 0x28
VK_SELECT       = 0x29
VK_PRINT        = 0x2A
VK_EXECUTE      = 0x2B
VK_SNAPSHOT     = 0x2C
VK_INSERT       = 0x2D
VK_DELETE       = 0x2E
VK_HELP         = 0x2F

#/* VK_0 thru VK_9 are the same as ASCII '0' thru '9' (0x30 - 0x39) */
#/* VK_A thru VK_Z are the same as ASCII 'A' thru 'Z' (0x41 - 0x5A) */

VK_LWIN         = 0x5B
VK_RWIN         = 0x5C
VK_APPS         = 0x5D

VK_NUMPAD0      = 0x60
VK_NUMPAD1      = 0x61
VK_NUMPAD2      = 0x62
VK_NUMPAD3      = 0x63
VK_NUMPAD4      = 0x64
VK_NUMPAD5      = 0x65
VK_NUMPAD6      = 0x66
VK_NUMPAD7      = 0x67
VK_NUMPAD8      = 0x68
VK_NUMPAD9      = 0x69
VK_MULTIPLY     = 0x6A
VK_ADD          = 0x6B
VK_SEPARATOR    = 0x6C
VK_SUBTRACT     = 0x6D
VK_DECIMAL      = 0x6E
VK_DIVIDE       = 0x6F
VK_F1           = 0x70
VK_F2           = 0x71
VK_F3           = 0x72
VK_F4           = 0x73
VK_F5           = 0x74
VK_F6           = 0x75
VK_F7           = 0x76
VK_F8           = 0x77
VK_F9           = 0x78
VK_F10          = 0x79
VK_F11          = 0x7A
VK_F12          = 0x7B
VK_F13          = 0x7C
VK_F14          = 0x7D
VK_F15          = 0x7E
VK_F16          = 0x7F
VK_F17          = 0x80
VK_F18          = 0x81
VK_F19          = 0x82
VK_F20          = 0x83
VK_F21          = 0x84
VK_F22          = 0x85
VK_F23          = 0x86
VK_F24          = 0x87
VK_NUMLOCK      = 0x90
VK_SCROLL       = 0x91

VK_LSHIFT       = 0xA0
VK_RSHIFT       = 0xA1
VK_LCONTROL     = 0xA2
VK_RCONTROL     = 0xA3
VK_LMENU        = 0xA4
VK_RMENU        = 0xA5

DEBUG_KEY		= VK_F1

keydown = {}
keystate = [0] * 0x100
debugEnabled = 1

def gotEvent(event, wParam, lParam):
    global keydown, keystate, debugEnabled
    if event in mouseMsgs:
        x = lParam & 0xffff
        y = lParam >> 16
        #print "Mouse Event: %d (%d,%d)" % (event, x, y)
        mods = pyui.locals.MOD_NONE
        if event in [WM_LBUTTONDOWN, WM_LBUTTONUP, WM_RBUTTONDOWN, WM_RBUTTONUP, WM_MOUSEMOVE]:
            if keystate[VK_SHIFT]:
                mods |= pyui.locals.MOD_SHIFT
            if keystate[VK_CONTROL]:
                mods |= pyui.locals.MOD_CONTROL
            if keystate[VK_MENU]:
                mods |= pyui.locals.MOD_ALT
        if getDesktop():
            getDesktop().postUserEvent(event, x, y, wParam, mods)
        return

    # mods for key events
    if event in [WM_CHAR, WM_KEYDOWN, WM_KEYUP]:
        mods = pyui.locals.MOD_NONE
        if keystate[VK_SHIFT]:
            mods |= pyui.locals.MOD_SHIFT
        if keystate[VK_CONTROL]:
            mods |= pyui.locals.MOD_CONTROL
        if keystate[VK_MENU]:
            mods |= pyui.locals.MOD_ALT

    # This is the handler for character keys.
    if event == WM_CHAR:
        getDesktop().postUserEvent(pyui.locals.CHAR, 0, 0, chr(wParam), mods)
        return

    if event == WM_KEYDOWN:
        if debugEnabled and (DEBUG_KEY == wParam):
            PyUnseen.debug(0)
            return
        global keydown, keystate
        keystate[wParam] += 1
        getDesktop().postUserEvent(pyui.locals.KEYDOWN, 0, 0, wParam, mods)
        return

    if event == WM_KEYUP:
        global keydown, keystate
        keystate[wParam] = 0
        getDesktop().postUserEvent(pyui.locals.KEYUP, 0, 0, wParam, mods)
        return
        
    # special event handlers
    if event == WM_CLOSE:
        getDesktop().postUserEvent(pyui.locals.QUIT, 0, 0, 0)
        return
        
class Unseen(Renderer3DBase):
    """Direct3D Renderer using PyUnseen engine.
    """

    name = "PyUnseen"
    
    def __init__(self, w, h, fullscreen, title="Unseen"):
        Renderer3DBase.__init__(self, w, h, fullscreen)
        PyUnseen.initialize(w, h, gotEvent, messageMap, title )
        self.font1 = PyUnseen.createFont( "Arial", 9, 0 )
        self.fixedFont = PyUnseen.createFont( "Courier", 7, 0 )        
        self.populateConstants()

        # store the actual height and width surface created (might be less than requested)
        #(getDesktop().width, getDesktop().height) = PyUnseen.getDesktopSize()
        
        (w, pyui.locals.TEXT_HEIGHT) = self.getTextSize(" ")
        self.images = {}

        self.cache = {} # tracks all objects by Handle. useful for debugging

    def draw(self, windows):
        """run the python widgets drawing code. This calls describeWindow on any windows
        that have changed. The actual drawing is done within PyUnseen.render.
        """
        for w in windows:
            w.drawWindow(self)

        PyUnseen.render()
        PyUnseen.messagepump()
        
        self.mustFill = 0
        self.dirtyRects = []

    def populateConstants(self):
        """Populate pyui.constants with the values from msgs.py which are win32 message types.
        """
        pyui.locals.LMOUSEBUTTONDOWN    = WM_LBUTTONDOWN
        pyui.locals.RMOUSEBUTTONDOWN    = WM_RBUTTONDOWN
        pyui.locals.MMOUSEBUTTONDOWN    = WM_MBUTTONDOWN
        pyui.locals.LMOUSEBUTTONUP      = WM_LBUTTONUP
        pyui.locals.RMOUSEBUTTONUP      = WM_RBUTTONUP
        pyui.locals.MMOUSEBUTTONUP      = WM_MBUTTONUP
        pyui.locals.MOUSEMOVE           = WM_MOUSEMOVE
        pyui.locals.MOUSEWHEEL          = WM_MOUSEWHEEL
        pyui.locals.QUIT                = WM_CLOSE
        pyui.locals.LMOUSEDBLCLICK       = WM_LBUTTONDBLCLK
        pyui.locals.RMOUSEDBLCLICK       = WM_RBUTTONDBLCLK
        pyui.locals.MMOUSEDBLCLICK       = WM_MBUTTONDBLCLK        

        global keydown
        pyui.locals.K_BACKSPACE = VK_BACK
        pyui.locals.K_TAB       = VK_TAB
        pyui.locals.K_RETURN    = VK_RETURN
        pyui.locals.K_SHIFT     = VK_SHIFT
        pyui.locals.K_CONTROL   = VK_CONTROL
        pyui.locals.K_ALT       = VK_MENU
        pyui.locals.K_ESCAPE    = VK_ESCAPE
        pyui.locals.K_SPACE     = VK_SPACE
        pyui.locals.K_PAGEUP    = VK_PRIOR
        pyui.locals.K_PAGEDOWN  = VK_NEXT
        pyui.locals.K_END       = VK_END
        pyui.locals.K_HOME      = VK_HOME
        
        pyui.locals.K_LEFT      = VK_LEFT
        pyui.locals.K_RIGHT     = VK_RIGHT
        pyui.locals.K_UP        = VK_UP
        pyui.locals.K_DOWN      = VK_DOWN

        pyui.locals.K_INSERT    = VK_INSERT
        pyui.locals.K_DELETE    = VK_DELETE

        pyui.locals.K_F1        = VK_F1
        pyui.locals.K_F2        = VK_F2
        pyui.locals.K_F3        = VK_F3
        pyui.locals.K_F4        = VK_F4
        pyui.locals.K_F5        = VK_F5
        pyui.locals.K_F6        = VK_F6
        pyui.locals.K_F7        = VK_F7
        pyui.locals.K_F8        = VK_F8
        pyui.locals.K_F9        = VK_F9
        pyui.locals.K_F10       = VK_F10
        pyui.locals.K_F11       = VK_F11
        pyui.locals.K_F12       = VK_F12


    ###############################################################################
    ### PyUnseen interface functions
    ###############################################################################

    def setWindowTitle(self, title=""):
        """Sets the title on the Win32 main window.
        """
        return PyUnseen.setWindowTitle(title)
    
    def createWindow(self, title = None):
        handle = PyUnseen.createWindow()
        self.cache[handle] = "window %s" % title
        return handle

    def describeWindow(self, handle, drawList):
        if not handle:
            return
        #print "Describing window (%d): %s" % (handle, drawList)
        #print "Describing window ",  handle
        #for d in drawList:
        #    print d
        return PyUnseen.describeWindow(handle, drawList)

    def destroyWindow(self, handle):
        del self.cache[handle]
        return PyUnseen.destroyWindow(handle)

    def moveWindow(self, handle, x, y):
        return PyUnseen.moveWindow(handle, x, y)

    def moveToFront(self, handle):
        return PyUnseen.moveToFront(handle)
    
    ###############################################################################
    ### Draw Primitives functions
    ###############################################################################

    def drawRect(self, color, rect):
        """Fills a rectangle with the specified color."""
        #skip empty rects
        if rect[2] == 0 or rect[3] == 0:
            return
        self.drawList.append( (pyui.locals.RECT, rect[0], rect[1], rect[2], rect[3], color ) ) 

    def drawText(self, text, pos, color, font = None):
        """Draws the text on the screen in the specified position"""
        if font == 'fixed':
            font = self.fixedFont
        elif font == None:
            font = self.font1
        self.drawList.append( (pyui.locals.TEXT, pos[0], pos[1], color, font, text))
        
    def drawGradient(self, rect, c1, c2, c3, c4):
        """Draws a gradient rectangle"""
        #skip empty rects
        if rect[2] == 0 or rect[3] == 0:
            return
        self.drawList.append( (pyui.locals.GRADIENT, rect[0], rect[1], rect[2], rect[3], c1, c2, c3, c4) )
        
    def drawImage(self, rect, filename, pieceRect = None):
        """Draws an image at a position. NOTE: should take a texture handle"""
        #skip empty rects
        if rect[2] == 0 or rect[3] == 0:
            return
        if not self.images.has_key(filename):
            self.loadImage(filename)
        if not pieceRect:
            pieceRect = (0,0,1,1)
        self.drawList.append( (pyui.locals.IMAGE, rect[0], rect[1], rect[2], rect[3], self.images[filename], 0,
         pieceRect[0], pieceRect[1], pieceRect[2], pieceRect[3]) )

    def drawImageRotated(self, rect, filename, rotation=0, textureEffect=0 ):
        """Draws an image at a position. NOTE: should take a texture handle"""
        #skip empty rects
        if rect[2] == 0 or rect[3] == 0:
            return
        if not self.images.has_key(filename):
            self.loadImage(filename)
        self.drawList.append( (pyui.locals.IMAGE, rect[0], rect[1], rect[2], rect[3], self.images[filename], rotation) )

    def drawLine(self, x1, y1, x2, y2, color):
        self.drawList.append( (pyui.locals.LINE, x1, y1, x2, y2, color) )
        
    def drawView(self, rect, handle):
        """Draws a viewport into a 3d World in the specified rectangle."""
        self.drawList.append( (pyui.locals.VIEW, rect[0], rect[1], rect[2], rect[3], handle) )
    
    def loadImage(self, filename, label = None):
        if label:
            handle = PyUnseen.createTexture(filename)
            self.images[label] = handle            
        else:
            handle = PyUnseen.createTexture(filename)
            self.images[filename] = handle            

    def getImageSize(self, filename):
        handle = self.images.get(filename)
        if not handle:
            handle = PyUnseen.createTexture(filename)
        return PyUnseen.getTextureSize(handle)
    
    def setClipping(self, rect = None):
        """set the clipping rectangle for the main screen. defaults to clearing the clipping rectangle."""
        #self.drawList.append( [pyui.locals.CLIP, (rect[0], rect[1], rect[2], rect[3]) ] )
        pass
    
    def quit(self):
        print "PyUnseen Quitting."
        PyUnseen.destroyFont(self.font1)
        PyUnseen.destroyFont(self.fixedFont)
        for filename in self.images.keys():
            handle = self.images[filename]
            PyUnseen.destroyTexture(handle)
        self.dumpCache()        
        PyUnseen.cleanup()

    def packColor(self, r, g, b, a = 255):
        """pack the rgb triplet into a color
        """
        return (r,g,b,a)

    def addRect(self, rect):
        """Dont do dirty rects in 3d!"""
        return

    def getMustFill(self):
        return 0

    def getTextSize(self, text, font = None):
        if font == 'fixed':
            font = self.fixedFont
        elif not font:
            font = self.font1
            
        return PyUnseen.getTextSize(font, text)
        
    def readTimer(self):
        return PyUnseen.getMilliseconds() * 0.001

    ### 3D interface

    def createView(self, world):
        """Create a view object and return the handle to it.
            Width and height ignored by PyUnseen
        """
        handle = PyUnseen.createView(world)
        self.cache[handle] = "view"
        return handle

    def destroyView(self, viewHandle):
        """Destroy a previously created view object.
        """
        del self.cache[viewHandle]
        return PyUnseen.destroyView(viewHandle)

    def createObject(self, model, info=(0.0,0.0,0.0)):
        handle =  PyUnseen.createObject(model, info)        
        self.cache[handle] = model
        return handle

    def destroyObject(self, objectHandle):
        del self.cache[objectHandle]
        return PyUnseen.destroyObject(objectHandle)

    def createWorld(self):
        handle =  PyUnseen.createWorld()
        self.cache[handle] = "world"
        return handle

    def destroyWorld(self, worldHandle):
        del self.cache[worldHandle]
        return PyUnseen.destroyWorld(worldHandle)

    def updateWorld(self, worldHandle, interval = None):
        return PyUnseen.updateWorld(worldHandle, interval)

    def addToWorld(self, worldHandle, objectHandle):
        return PyUnseen.addToWorld(worldHandle, objectHandle)

    def removeFromWorld(self, worldHandle, objectHandle):
        return PyUnseen.removeFromWorld(worldHandle, objectHandle)

    def getObjectPos(self, objectHandle):
        return PyUnseen.getObjectPos(objectHandle)
    
    def setObjectScale(self, objectHandle, scale):
        return PyUnseen.setObjectScale(objectHandle, scale)

    def setObjectPos(self, objectHandle, pos):
        return PyUnseen.setObjectPos(objectHandle, pos)

    def setObjectAnimation(self, objectHandle, animation, onCompleted = None, blendTime = 0.0, loop = 1):
        return PyUnseen.setObjectAnimation(objectHandle, animation, onCompleted, blendTime, loop)

    def loadAnimation(self, animation):
        return PyUnseen.loadAnimation(animation)

    def setObjectYPR(self, objectHandle, YPR):
        (y,p,r) = YPR
        return PyUnseen.setObjectYPR(objectHandle, (y,p,r) )

    def getObjectYPR(self, objectHandle):
        return PyUnseen.getObjectYPR(objectHandle)
    
    def moveObjectTo(self, objectHandle, location, moveRate, turnRate = 0, onCompleted = None):
        return PyUnseen.moveObjectTo(objectHandle, location, moveRate, turnRate, onCompleted)
        
    def moveObject(self, objectHandle, delta, moveRate, turnRate = 0, onCompleted = None):
        return PyUnseen.moveObject(objectHandle, delta, moveRate, turnRate, onCompleted)

    def rotateObjectTo(self, objectHandle, orientation, turnRate, onCompleted = None):
        return PyUnseen.rotateObjectTo(objectHandle, orientation, turnRate, onCompleted)

    def rotateObject(self, objectHandle, delta, turnRate, onCompleted = None):
        return PyUnseen.rotateObject(objectHandle, delta, turnRate, onCompleted)

    def attachObject(self, objectHandle, toObjectHandle, connectionPointName = "", toConnectionPointName = ""):
        return PyUnseen.attachObject(objectHandle, toObjectHandle, connectionPointName, toConnectionPointName)

    def detachObject(self, objectHandle, fromObjectHandle):
        return PyUnseen.detachObject(objectHandle, fromObjectHandle)

    def setViewProjectionMode(self, viewHandle, projectionMode):
        return PyUnseen.setViewProjectionMode(viewHandle, projectionMode)

    def setViewParameters(self, viewHandle, parameters):
        return PyUnseen.setViewParameters(viewHandle, parameters)

    def setCameraYPR(self, viewHandle, YPR):
        return PyUnseen.setCameraYPR(viewHandle, YPR)

    def setCameraPos(self, viewHandle, pos):
        return PyUnseen.setCameraPos(viewHandle, pos)

    def getCameraYPR(self, viewHandle):
        return PyUnseen.getCameraYPR(viewHandle)

    def getCameraPos(self, viewHandle):
        return PyUnseen.getCameraPos(viewHandle)

    def getCameraDir(self, viewHandle):
        return PyUnseen.getCameraDir(viewHandle)

    def moveCamera(self, viewHandle, offset):
        return PyUnseen.moveCamera(viewHandle, offset)

    def setLightParameters(self, viewHandle, YPR):
        return PyUnseen.setLightParameters(viewHandle, YPR)

    def getDesktopWindow(self):
        return PyUnseen.getDesktopWindow()

    def attachView(self, windowHandle, viewHandle):
        return PyUnseen.attachView(windowHandle, viewHandle)
    
    def pickView(self, viewHandle, xy):
        return PyUnseen.pickView(viewHandle, xy)

    def attachController(self, objectHandle, controllerType, boneName):
        return PyUnseen.attachController(objectHandle, controllerType, boneName)

    def setController(self, controllerHandle, **parms):
        return PyUnseen.setController(controllerHandle, parms)

    def detachController(self, objectHandle, controllerHandle):
        return PyUnseen.detachController(objectHandle, controllerHandle)
  
    def getObjectProjectedPos(self, objectHandle, viewHandle):
        return PyUnseen.getObjectProjectedPos(objectHandle, viewHandle)

    def getNodeProjectedPos(self, nodeHandle, viewHandle):
        return PyUnseen.getNodeProjectedPos(nodeHandle, viewHandle)

    def getObjectNode(self, objectHandle, nodeName, iLOD):
    	return PyUnseen.getObjectNode(objectHandle, nodeName, iLOD)

    def createFont(self, fontName, size, flag):
        handle = PyUnseen.createFont(fontName, size, flag)
        self.cache[handle] = "font %s %s" % ( fontName, size)
        return handle

    def destroyFont(self, fontHandle):
        del self.cache[fontHandle]
        return PyUnseen.destroyFont(fontHandle)

    def getScreenSize(self):
        return PyUnseen.getScreenSize()

    def playSound(self, waveFileName, completionCallback = None):
        return PyUnseen.playSound(waveFileName, completionCallback)

    def stopSound(self, waveFileName):
        return PyUnseen.stopSound(waveFileName)

    def loadSound(self, waveFileName):
        return PyUnseen.loadSound(waveFileName)

    def playMusic(self, waveFileName, completionCallback = None):
        return PyUnseen.playMusic(waveFileName, completionCallback)

    def stopMusic(self, waveFileName):
        return PyUnseen.stopMusic(waveFileName)

    def loadMusic(self, waveFileName):
        return PyUnseen.loadMusic(waveFileName)

    def toggleDebugInfo(self):
        return PyUnseen.togglePerfInfo()

    def setWindowEffect(self, windowHandle, effectName):
        return PyUnseen.setWindowViewEffect(windowHandle, effectName)

    def createEmptyBody(self, xyz=(0.0,0.0,0.0), label="emptyBody"):
        handle= PyUnseen.createEmptyBody(xyz)
        self.cache[handle] = label
        return handle
    
    def addGeometryNode(self, objectHandle, bone=0):
        return PyUnseen.addGeometryNode(objectHandle, bone)

    def addGeometryPiece(self, node, iType, info, offset, ypr, effect = "", effectParams = {}):
        return PyUnseen.addGeometryPiece(node, iType, info, offset, ypr, effect, effectParams)

    def getNodeEffect(self, node, num):
        return PyUnseen.getNodeEffect(node, num)

    def setEffectParameters(self, effect, parms):
        return PyUnseen.setEffectParameters(effect, parms)

    def dumpCache(self):
        print "====== DUMPING PYUNSEEN CACHE ======"
        for k in self.cache.keys():
            print "%s> %s" % (k, self.cache[k])
