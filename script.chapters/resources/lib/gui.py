import sys
import os
import xbmc
import xbmcgui
import urllib
import re
from chapterparser import ChapterParser
import xml.dom.minidom
import xbmcaddon

_ = sys.modules[ "__main__" ].__language__
#__scriptname__ = sys.modules[ "__main__" ].__scriptname__
#__version__ = sys.modules[ "__main__" ].__version__
__settings__ = xbmcaddon.Addon('script.chapters')

STATUS_LABEL = 100
LOADING_IMAGE = 110
LIST_CHAPTERS = 30050
LIST_CHAPTERS_LABEL2 = 30051
LIST_CHAPTERS_THUMBS = 30052


class GUI( xbmcgui.WindowXMLDialog ):
        
    def __init__( self, *args, **kwargs ):
        #xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        pass
        

    def setParameters(self, path, chaptersFile, debug):
        self.debug = debug
        self.chaptersFile = chaptersFile
        self.file_original_path = urllib.unquote ( path )
        self.file_path = urllib.unquote( path )
               
        if self.debug : 
            LOG( LOG_INFO, "setParameters : [%s]" , self.chaptersFile )
        return True

        

    def onInit( self ):
        if self.debug : LOG( LOG_INFO, "onInit" )
        self.init_chapters()
    
    
    def init_chapters( self ):
        
        viewmode=__settings__ .getSetting("viewmode")
        #print "####view:" + viewmode
        # Parse Chapter Files and get each chapter as map
        chapters = ChapterParser(self.chaptersFile)
        
        if self.getCtrl( LIST_CHAPTERS ): self.getControl( LIST_CHAPTERS ).reset()
        if self.getCtrl( LIST_CHAPTERS_THUMBS ): self.getControl( LIST_CHAPTERS_THUMBS ).reset()
        if self.getCtrl( LIST_CHAPTERS_LABEL2 ): self.getControl( LIST_CHAPTERS_LABEL2 ).reset()
        
        listItems = []
        hasThumb = False
        hasLabel2 = False
        for chapter in chapters.get_chapters():
            li = xbmcgui.ListItem(label=chapter[ 'ChapterName' ].encode('utf-8'), thumbnailImage=chapter[ 'ChapterThumb' ])
            li.setLabel2( chapter[ 'ChapterName2' ].encode('utf-8') )
            li.setProperty('chaptermark', str(chapter['MarkSeconds']))
            li.setProperty('chaptermarkhuman', chapter['MarkTime'])
            print chapter['ChapterThumb']
            if chapter['ChapterThumb']  <> '' and not hasThumb and viewmode == "0" : 
                hasThumb = True
                self.getControl( 30001 ).setLabel( "hasthumb" ) # set fake label before switching views
            if chapter['ChapterName2']  <> '' and not hasLabel2 and (viewmode == "0" or viewmode == "2") : 
                hasLabel2 = True
                self.getControl( 30002 ).setLabel( "haslabel2" ) # set fake label before switching views
            listItems.append( li )
        
        if self.getCtrl( 30010 ): self.getCtrl( 30010 ).setLabel( _( 50000 ) )
        if self.getCtrl( LIST_CHAPTERS_LABEL2 ): self.getCtrl( LIST_CHAPTERS_LABEL2 ).addItems( listItems )
        if self.getCtrl( LIST_CHAPTERS ): self.getCtrl( LIST_CHAPTERS ).addItems( listItems )
        if self.getCtrl( LIST_CHAPTERS_THUMBS ) : self.getCtrl( LIST_CHAPTERS_THUMBS ).addItems( listItems )
        if hasThumb and self.getCtrl( LIST_CHAPTERS_THUMBS ):
            xbmc.executebuiltin('Container.SetViewMode('+str(LIST_CHAPTERS_THUMBS)+')')
            xbmc.executebuiltin('SetFocus('+str(LIST_CHAPTERS_THUMBS)+',0)')
            
        elif hasLabel2 and self.getCtrl( LIST_CHAPTERS_LABEL2 ):
            xbmc.executebuiltin('Container.SetViewMode('+str(LIST_CHAPTERS_LABEL2)+')')
            xbmc.executebuiltin('SetFocus('+str(LIST_CHAPTERS_LABEL2)+',0)')
            
        elif self.getCtrl( LIST_CHAPTERS ):
            xbmc.executebuiltin('Container.SetViewMode('+str(LIST_CHAPTERS)+')')
            xbmc.executebuiltin('SetFocus('+str(LIST_CHAPTERS)+',0)')
        else :
            self.exit_script()

    def getCtrl(self, id):
        try:
           return  self.getControl( id )
        except:
            return False
        
    def exit_script( self ):
        self.close()

    def onClick( self, controlId ):
        # Get Selected Item marker, Seek and exit
        selected = self.getControl( self.controlId ).getSelectedItem()
        self.exit_script()
        xbmc.Player().seekTime(float(selected.getProperty('chaptermark')))        
        
    
    def onFocus( self, controlId ):
        self.controlId = controlId
        #print "Focus ", controlId


        
    def onAction( self, action ):
         #keycode= action.getButtonCode()
         #keycode= action.getId()
         #print "#####keycode: " + hex(keycode)
         if ( action.getId() == 0x5c ) or ( action.getId() == 0x0a ):  # backspace(Back) or escape(PreviousMenu)
            self.exit_script()
         elif ( action.getId() == 0x01 ) or ( action.getId() == 0x02 ):  # left-arrow(left) or right-arrow(right)
            self.exit_script()
            __settings__.openSettings()
            xbmc.executebuiltin('RunScript(script.chapters)')


