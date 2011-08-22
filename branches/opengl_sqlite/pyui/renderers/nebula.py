import npython
from npython import *
import os.path
from pyui import rendererBase, desktop
import pyui
def orig():
    set('/usr/lookat.txyz',0,0,0)
    set('/usr/lookat.rxyz',-25,45,0)
    set('/usr/camera.tz',5)

class RendererNeb(rendererBase.RendererBase):
    name = "Nebula"

    def __init__(self, w, h, fullscreen, title='Nebula'):
        new('nglserver','/sys/servers/gfx')
        new('ninputserver', '/sys/servers/input')

        new('nscenegraph2','/sys/servers/sgraph2')
        new('nsbufshadowserver','/sys/servers/shadow')
        new('nchannelserver','/sys/servers/channel')
        new('nconserver','/sys/servers/console')
        new('nmathserver','/sys/servers/math')
        new('nparticleserver','/sys/servers/particle')
        new('nspecialfxserver','/sys/servers/specialfx')
        new('nfileserver2','/sys/servers/file2')

        set('/sys/servers/gfx.setdisplaymode','w(%s)-h(%s)-type(%s)' % (w, h, (fullscreen and 'full') or 'win'))
        set('/sys/servers/gfx.setviewvolume',  -0.1, +0.1, -0.075, 0.075, +0.1 ,+2500)

        set('/sys/servers/gfx.setclearcolor', 0.0, 0.1, 0.3, 0)
        set('/sys/servers/gfx.opendisplay')

        set('/sys/servers/input.beginmap')
        set('/sys/servers/input.map', 'mouse0:btn0.down', 'script:mouse0down()')
        set('/sys/servers/input.map', 'mouse0:btn0.up',  'script:mouse0up()')

        set('/sys/servers/input.map', 'mouse1:btn1.down', 'script:mouse1down()')
        set('/sys/servers/input.map', 'mouse1:btn1.up',  'script:mouse1up()')

        set('/sys/servers/input.map', 'mouse0:btn1.pressed', 'script:print "clunk!"')
        set('/sys/servers/input.map', 'keyb0:space.down', "script:orig()")
        set('/sys/servers/input.map', 'keyb0:esc.down',"script:set('/sys/servers/console.toggle')")

        #setup more keys
        set('/sys/servers/input.map', 'keyb0:return.down',"script:onReturnDown")
        
        set('/sys/servers/input.endmap')

        new('n3dnode','/usr/scene')
        new('n3dnode','/usr/camera')
        new('n3dnode','/usr/lookat')
        orig()
        new('nobserver','/observer')
        # this restricts framerate, to be OS friendly
        set('/observer.setsleep', 0.02)
        # Turn on/off grid here
        set('/observer.setgrid', 0)
        sel('/')
        new('nroot','lib')
        sel('/lib')
        shader=new ('nshadernode','nuiuntex')
	sel ('nuiuntex')
        self.shaderInit(shader)
	sel ('..')
        texshader=new ('nshadernode','nuitex')
	sel ('nuitex')
        self.shaderInit(texshader)
        sel('/usr/scene')
        new('nui','pyui')
        self.pyui = sel('pyui')
        set('setUntexturedShader','/lib/nuiuntex')
        set('setTextureShader','/lib/nuitex')
	tex=new ('ntexarraynode','tex')
        # evil, but hey! i could have done this the hard way

        npython.mouseMotion =  self.mouseMotion
        __builtins__['mouse0down'] = self.mouse0down
        __builtins__['mouse0up'] = self.mouse0up
        __builtins__['mouse1down'] = self.mouse1down
        __builtins__['mouse1up'] = self.mouse1up

        self.drawlist = []
        rendererBase.RendererBase.__init__(self, float(w), float(h),fullscreen,title)

        self.drawBackMethod = self.clear
        
    def shaderInit(self, shader):
        set('.setrenderpri', 0)
        set('.setnumstages', 1)
        set('.setcolorop', 0, "mul prim prev")
        #set('.setalphaop', 0, "mul prim prev")
        set('.setconst', 0, 0.000000, 0.000000, 0.000000, 0.000000)
        set('.setdiffuse', 1.000000, 1.000000, 1.000000, 0.000000)
        set('.setemissive', 0.000000, 0.000000, 0.000000, 0.000000)
        set('.setambient', 0.000000, 0.000000, 0.000000, 0.000000)
        set('.setlightenable', 0)
        set('.setalphaenable', 1)
        set( '.setzwriteenable', 0)
        set('.setfogenable', 1)
        set('.setalphablend', "srcalpha", "invsrcalpha")
        set('.setzfunc', "always")
        set('.setcullmode', "ccw")
        set('.setcolormaterial', "material")
        set('.setalphatestenable', 0)
        set('.setalpharef', 0.000000)
        set('.setalphafunc', "greater")

    def packColor(self, r,g,b,a=255):
        return (r/255.0,g/255.0,b/255.0,a/255.0)

    def unpackColor(self, color):
        return map(lambda x: x * 255.0, color)

    mouseX = None
    mouseY = None
    def mouseMotion(self,x,y):
        pyui.desktop.getDesktop().postUserEvent(pyui.locals.MOUSEMOVE,self.mouseX, self.mouseY)
        self.mouseX = x
        self.mouseY = y

    def mouse1down(self):
        pyui.desktop.getDesktop().postUserEvent(pyui.locals.RMOUSEBUTTONDOWN, self.mouseX, self.mouseY)

    def mouse1up(self):
        pyui.desktop.getDesktop().postUserEvent(pyui.locals.RMOUSEBUTTONUP, self.mouseX, self.mouseY)

    def mouse0down(self):
        pyui.desktop.getDesktop().postUserEvent(pyui.locals.LMOUSEBUTTONDOWN, self.mouseX, self.mouseY)

    def mouse0up(self):
        pyui.desktop.getDesktop().postUserEvent(pyui.locals.LMOUSEBUTTONUP, self.mouseX, self.mouseY)

        
    def clear(self):
        #TODO: make a clear method
        pass
    
    def draw(self, windows):
        apply(self.drawBackMethod, self.drawBackArgs)                

        import pdb
        #if __debug__: pdb.set_trace()
        if self.callback:
            self.callback()
        for w in windows:
            w.dirty =1
            self.windowPos = (w.posX, w.posY)
            w.drawWindow(self)
            self.drawlist.reverse()
            for dc in self.drawlist:
                apply(getattr(self, dc[0]), dc[1])

    def setDrawList(self, emptylist):
        self.drawlist = emptylist
        pass

    def drawRect(self, *args):
        self.drawlist.append(('doRect',args + (self.windowPos,)))
    def drawGradient(self,*args):  
        self.drawlist.append(('doGradient',args + (self.windowPos,)))
    def drawLine(self,*args):
        self.drawlist.append(('doLine',args +(self.windowPos,)))
    def drawText(self,text, coord, color, font=None):
        self.drawlist.append(('doText',(text, coord, color, font, self.windowPos)))
    def drawImage(self,*args):
        self.drawlist.append(('doImage',args +(self.windowPos,)))

    def doRect(self, color, (x,y,w,h), windowPos):
        x = x + windowPos[0]
        y = y + windowPos[1]
        x1,y1 = (x/self.w * 2)-1, 1-(2*y/self.h)
        x2,y2 = (2*(x+w)/self.w)-1 , 1-(2*(y+h)/self.h)
        #print "drawRect(",x,y,w,h,color,"): " ,x1,y2,x2,y1
        self.pyui.doRect(x1,y2,x2,y1,color[0],color[1],color[2],color[3])

    def doGradient(self, (x,y,w,h), c1,c2,c3,c4, windowPos):
        x = x + windowPos[0]
        y = y + windowPos[1]
        x1,y1 = (x/self.w * 2)-1, 1-(2*y/self.h)
        x2,y2 = (2*(x+w)/self.w)-1 , 1-(2*(y+h)/self.h)
        #print  "drawGrad(",x,y,w,h,"):",x1,y2,x2,y1,c1[0],c1[1],c1[2],c1[3],c2[0],c2[1],c2[2],c2[3],c4[0],c4[1],c4[2],c4[3],c3[0],c3[1],c3[2],c3[3]
        self.pyui.doGradient(x1,y2,x2,y1,c1[0],c1[1],c1[2],c1[3],c2[0],c2[1],c2[2],c2[3],c4[0],c4[1],c4[2],c4[3],c3[0],c3[1],c3[2],c3[3])

    def doLine(self, x1,y1,x2,y2, color, windowPos):
        x1 = x1 + windowPos[0]
        y1 = y1 + windowPos[1]
        x2 = x2 + windowPos[0]
        y2 = y2 + windowPos[1]
        X1,Y1 = (2*(x2)/self.w)-1,1-(2*(y2)/self.h)
        X2,Y2 = (x1/self.w* 2)-1, 1-(2*y1/self.h)
        #print  'drawLine(',x1,y1,x2,y2,color,')',X1,Y1,X2,Y2,color[0],color[1],color[2],color[3]
        self.pyui.doLine(X1,Y1,X2,Y2,color[0],color[1],color[2],color[3])

    def doText(self, text, (x,y), (r,g,b,a), font, windowPos):
        x = x + windowPos[0]
        y = y + windowPos[1] -4
        x1,y1 = (x/self.w* 2)-1, 1-(2*y/self.h)
        #print 'doText', text,x1,-y1,r,g,b,a
        #this assumes the coord given is the top right corner
        self.pyui.doText(text, x1,-y1,r,g,b,a)

    images = {}

    def loadImage(self, filename, label=None):
        if not os.path.exists(filename):
            raise IOError("Image file not found.")
        if not label:
            i = filename.rfind("/")
            if i != -1:
                label = filename[i+1:]
            else:
                label = filename
        stage = len(self.images)
        self.images[filename] = stage, label
        #print "calling loadImage(%s,%s)" % (filename, label)
        self.pyui.loadImage(filename,label,0)

    def doImage(self, (x,y,w,h), name, windowPos):
        x = x + windowPos[0]
        y = y + windowPos[1]
        x1,y1 = (x/self.w * 2)-1, 1-(2*(y+h)/self.h)
        x2,y2 = (2*(x+w)/self.w)-1, 1-(2*y/self.h)
        if not self.images.has_key(name):
            self.loadImage(name)
        stage, label = self.images[name]
        #print "calling doImage(%s,%f,%f,%f,%f)" %(label,x1,y1,x2,y2)
        self.pyui.doImage(label,x1,y1,x2,y2)

    def load1(self):
        self.loadImage("/home/washort/nebula-build/pyui/tests/max.bmp","max.bmp")

    def test1(self):
        self.drawRect((10,10,50,50),(1,0,0,1))
        self.drawImage((60,50,100,100),"/home/washort/nebula-build/pyui/tests/max.bmp")

    def load2(self):
        self.loadImage("/home/washort/nebula-build/pyui/tests/folder.bmp","folder.bmp")
        
    def test2(self):
        self.drawImage((300,200,100,100),"/home/washort/nebula-build/pyui/tests/folder.bmp")
        
    def test3(self):
        self.drawImage((500,100,100,100),"/home/washort/nebula-build/pyui/tests/max.bmp")
        
    def run(self, callback=None):
        self.callback=callback
        setTrigger(lambda: (desktop.getDesktop().draw(),desktop.getDesktop().update()))
        set("/sys/servers/input.setmousecallback", "mouseMotion")
        set('/observer.start')

    def getTextSize(self, text, font = None):
        return (len(text) * 8, 18)
