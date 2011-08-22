# PyUI
# Copyright (C) 2001-2002 Sean C. Riley
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import pygame
import pygame.font
import pygame.image
import pygame.key
import pygame.draw
import pyui.core
import pygame.transform

from pygame.locals import *

from pyui.desktop import getDesktop

class Pygame2D(pyui.core.RendererBase):
    """Pygame 2D renderer.
    """
    name = "2D"
    
    def __init__(self, w, h, fullscreen, title):
        pyui.core.RendererBase.__init__(self, w, h, fullscreen, title)
        pygame.init()
        if fullscreen:
            self.screen = pygame.display.set_mode((w, h), FULLSCREEN | SWSURFACE)
        else:
            self.screen = pygame.display.set_mode((w, h))
        self.screen.set_alpha(255)
            
        pygame.key.set_mods(KMOD_NONE)

        pyui.locals.K_SHIFT     = 304
        pyui.locals.K_CONTROL   = 306
        pyui.locals.K_ALT       = 308

        pyui.locals.K_PAGEUP    = 280
        pyui.locals.K_PAGEDOWN  = 281
        pyui.locals.K_END       = 279
        pyui.locals.K_HOME      = 278

        pyui.locals.K_LEFT      = 276
        pyui.locals.K_UP        = 273
        pyui.locals.K_RIGHT     = 275
        pyui.locals.K_DOWN      = 274

        pyui.locals.K_INSERT    = 277
        pyui.locals.K_DELETE    = 127

        pyui.locals.K_F1        = 282
        pyui.locals.K_F2        = 283
        pyui.locals.K_F3        = 284
        pyui.locals.K_F4        = 285
        pyui.locals.K_F5        = 286
        pyui.locals.K_F6        = 287
        pyui.locals.K_F7        = 288
        pyui.locals.K_F8        = 289
        pyui.locals.K_F9        = 290
        pyui.locals.K_F10       = 291
        pyui.locals.K_F11       = 292
        pyui.locals.K_F12       = 293

        try:
            self.font = pygame.font.Font("font.ttf", 14)
        except:
            print "Couldn't find arial.ttf - resorting to default font"
            self.font = pygame.font.Font(None, 12)
        pyui.locals.TEXT_HEIGHT = self.font.get_height()
        self.lastID = 1000
        self.windows = {}
        self.images = {}

        self.drawBackMethod = self.clear
        
    def doesDirtyRects(self):
        return 1


    def clear(self):
        self.screen.fill((0,0,0, 255))
        
    def draw(self, windows):
        # draw back if required
        if self.drawBackMethod:
            self.windowPos = (0,0)
            self.drawList = []
            apply(self.drawBackMethod, self.drawBackArgs)
            for command in self.drawList:
                self.doDrawCommand(command)
            self.drawList = []
            
        for i in xrange(len(windows)-1, -1, -1):
            w = windows[i]
            w.setDirty(1)
            n =  w.drawWindow(self)
            if n:
                self.windowPos = (w.posX, w.posY)
                for command in w.drawCommands:
                    self.doDrawCommand(command)

        if self.mustFill:
            pygame.display.flip()
        else:
            pygame.display.update()#self.dirtyRects)

        self.mustFill = 0
        self.dirtyRects = []


    ###############################################################################
    ### Draw Primatives functions
    ###############################################################################
        
    def drawRect(self, color, rect):
        """Fills a rectangle with the specified color."""
        self.drawList.append( (pyui.locals.RECT, rect, color) )

    def drawText(self, text, pos, color, font = None):
        """Draws the text on the screen in the specified position"""
        self.drawList.append( (pyui.locals.TEXT, text, pos, color) )

    def drawGradient(self, rect, c1, c2, c3, c4):
        """Draws a gradient rectangle"""
        self.drawList.append( (pyui.locals.GRADIENT, rect, c1, c2, c3, c4 ) )

    def drawImage(self, rect, filename, pieceRect = None):
        """Draws an image at a position"""
        if not self.images.has_key(filename):
            self.loadImage(filename)
        self.drawList.append( (pyui.locals.IMAGE, rect, filename) )

    def drawLine(self, x1, y1, x2, y2, color):
        """Draws a line"""
        self.drawList.append( (pyui.locals.LINE, x1, y1, x2, y2, color) )

    def loadImage(self, filename, label = None):
        if label:
            self.images[label] = pygame.image.load(filename)
        else:
            self.images[filename] = pygame.image.load(filename)            

    def setClipping(self, rect = None):
        """set the clipping rectangle for the main screen. defaults to clearing the clipping rectangle."""
        self.drawList.append( (pyui.locals.CLIP, rect) )

    ###############################################################################
    ### actual drawing functions
    ###############################################################################

    def doDrawCommand(self, command):
        cmd = command[0]
        if cmd == pyui.locals.RECT:
            (cmd, rect, color) = command
            #print "pyui.locals.RECT: " ,command[1], command[2]
            rect = (self.windowPos[0]+rect[0], self.windowPos[1]+rect[1], rect[2], rect[3])
            self.screen.fill(color, rect)
            return 2
        elif cmd == pyui.locals.TEXT:
            (cmd, text, pos, color) = command
            if not text:
                return
            pos = (self.windowPos[0]+pos[0], self.windowPos[1]+pos[1])
            surf = self.font.render(text, 0, color, (0,0,0,255)) 
            surf.set_colorkey( (0,0,0,255))
            self.screen.blit(surf, pos)
            return len(text)
        elif cmd == pyui.locals.IMAGE:
            (cmd, rect, filename) = command
            rect = (self.windowPos[0]+rect[0], self.windowPos[1]+rect[1], rect[2], rect[3])
            img = self.images[filename]
            (w,h) = img.get_size()
            if (w,h) != (rect[2], rect[3]):
                img = pygame.transform.scale(img, (rect[2], rect[3]) )
            self.screen.blit(img, (rect[0], rect[1]) )
            return 2
        elif cmd == pyui.locals.GRADIENT:
            (cmd, rect, c1, c2, c3, c4 ) = command
            rect = (self.windowPos[0]+rect[0], self.windowPos[1]+rect[1], rect[2], rect[3])
            self.screen.fill(c3, rect)            
            return 2
        elif cmd == pyui.locals.CLIP:
            #(cmd, rect) = command
            #rect = (self.windowPos[0]+rect[0], self.windowPos[1]+rect[1], rect[2], rect[3])
            #self.screen.set_clip(rect)
            pass
        elif cmd == pyui.locals.LINE:
            (pyui.locals.LINE, x1, y1, x2, y2, color) = command
            pos1 = (self.windowPos[0] + x1, self.windowPos[1] + y1)
            pos2 = (self.windowPos[0] + x2, self.windowPos[1] + y2)
            pygame.draw.line(self.screen, color, pos1, pos2)
        return 0
        

    def update(self):
        ## process all pending system events.
        event = pygame.event.poll()
        while event.type != NOEVENT:
            
            # special case to handle multiple mouse buttons!
            if event.type == MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    getDesktop().postUserEvent(pyui.locals.LMOUSEBUTTONDOWN, event.pos[0], event.pos[1])
                elif event.dict['button'] == 3:
                    getDesktop().postUserEvent(pyui.locals.RMOUSEBUTTONDOWN, event.pos[0], event.pos[1])
                    
            elif event.type == MOUSEBUTTONUP:
                if event.dict['button'] == 1:
                    getDesktop().postUserEvent(pyui.locals.LMOUSEBUTTONUP, event.pos[0], event.pos[1])
                elif event.dict['button'] == 3:
                    getDesktop().postUserEvent(pyui.locals.RMOUSEBUTTONUP, event.pos[0], event.pos[1])
                    
            elif event.type == MOUSEMOTION:
                getDesktop().postUserEvent(pyui.locals.MOUSEMOVE, event.pos[0], event.pos[1])

            elif event.type == KEYDOWN:
                character = event.unicode
                code = 0
                if len(character) > 0:
                    code = ord(character)
                else:
                    code = event.key
                getDesktop().postUserEvent(pyui.locals.KEYDOWN, 0, 0, code, pygame.key.get_mods())
                if code >= 32 and code < 128:
                    getDesktop().postUserEvent(pyui.locals.CHAR, 0, 0, character.encode(), pygame.key.get_mods())

            elif event.type == KEYUP:
                code = event.key
                getDesktop().postUserEvent(pyui.locals.KEYUP, 0, 0, code, pygame.key.get_mods())
            else:
                try:
                    getDesktop().postUserEvent(event.type)
                except:
                    print "Error handling event %s" % repr(event)
            event = pygame.event.poll()


    def quit(self):
        pygame.quit()


    def packColor(self, r, g, b, a = 255):
        """pack the rgb triplet into a color
        """
        return (r, g, b, a)

    def getTextSize(self, text, font = None):
        return self.font.size(text)
