import sys
import os
import xbmc
import string
import xbmcaddon
import xbmcvfs

__addon__ = xbmcaddon.Addon('script.chapters')
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
__scriptname__ = __addon__.getAddonInfo('name')
__author__ = "Turhan Aydin, 999unreal"
__url__ = "http://code.google.com/p/xbmc-chapters/"
__svn_url__ = "http://xbmc-chapters.googlecode.com/svn/trunk/"
__version__ = str(__addon__.getAddonInfo('version'))
#__XBMC_Revision__ = "22240"
BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode('utf-8')
sys.path.append ( BASE_RESOURCE_PATH )
__settings__ = xbmcaddon.Addon('script.chapters')
__language__ = __settings__.getLocalizedString
_ = sys.modules[ "__main__" ].__language__

import gui
#############-----------------Is script runing from OSD? -------------------------------###############

if not xbmc.getCondVisibility('videoplayer.isfullscreen') or str(xbmc.getCondVisibility('Window.IsActive(main.xml)')) == "1":
    sys.modules.clear()
else:
    window = False
    skin = "main"
    skin1 = str(xbmc.getSkinDir().lower())
    skin1 = skin1.replace("-"," ")
    skin1 = skin1.replace("."," ")
    skin1 = skin1.replace("_"," ")
    if ( skin1.find( "g720" ) > -1 ):
         skin = "g720"
    if ( skin1.find( "confluence" ) > -1 ):
         skin = "confluence"     
  
    try: xbox = xbmc.getInfoLabel( "system.xboxversion" )
    except: xbox = ""
    if xbox != "" and len(skin) > 13:
      skin = skin.ljust(13)

    if __settings__.getSetting( "debug" ) == "true":     
        print "Chapters version [" +  __version__ +"]"
        print "Skin Folder: [ " + skin1 +" ]"
        print "Chapters skin XML: [ " + skin +" ]"
        debug = True
    else:
        debug = False   
    debug = False
 
    #splitlist = "foo.helloworld.exe".split(".")
    #>>> splitlist[len(splitlist) - 1]
    # '.'.join(splitlist[0: len(splitlist) - 1])
    mediafolder = xbmc.translatePath("special://home/scripts/" + __scriptname__ + "/resources/skins/Default/media")

    
    """
        path            - Full Path to Movie File (excluding filename)
        movieFullPath   - Full Path to Movie File (including filename)
        movieHalfPath   - Full Path to Movie File without extension
    """

    if ( __name__ == "__main__" ):   
        path = ""
        chaptersFile = ""
     
        movieFullPath = xbmc.Player().getPlayingFile()
        
        path = os.path.dirname( movieFullPath )
        passChapters = False
        xbmc.log( "%s: %s\n" % ( "INFO", "NOW PLAYING: " + movieFullPath  ) )
         # 16:30:42 T:1044 M:373161984  NOTICE: INFO: NOW PLAYING: stack://G:\data\babytv\The Cars\The Cars.CD1.avi , G:\data\babytv\The Cars\The Cars.CD2.avi
#16:30:42 T:1044 M:373002240  NOTICE: INFO: setParameters : [stack://G:\data\babytv\The Cars\The Cars.CD1.avi , G:\data\babytv\The Cars\The Cars.CD2.chapter.xml]
#16:30:42 T:1848 M:372908032   ERROR: XFILE::CDirectory::GetDirectory - Error getting ?
#16:30:42 T:1848 M:372903936   ERROR: CGUIMediaWindow::GetDirectory(?) failed
#16:30:42 T:1044 M:372330496   ERROR: CThread::staticThread : Access violation at 0x1e080ca8: Reading location 0x00000020
        
        # Pass Chapter search for particular locations
        
        if (movieFullPath.find("http://") > -1 ):
            passChapters = True

        if (movieFullPath.find("rar://") > -1 ):
            passChapters = True
        
        if (movieFullPath.find("stack://") > -1 ):
            movieFullPath = movieFullPath.replace('stack://', '').split(' , ')
            movieFullPath = movieFullPath[0]
                
        splitlist = movieFullPath.split(".")
        movieHalfPath = '.'.join(splitlist[0: len(splitlist) - 1])
#### ------------------------------ Get the main window going ---------------------------#####
        chapter_data = ""
        chaptersPath = movieFullPath + ".chapter.xml"
        # Look for XML Filees
        if xbmcvfs.exists(movieHalfPath.decode('utf-8') + ".chapter.xml"):
            chaptersFile = (movieHalfPath + ".chapter.xml")
        elif xbmcvfs.exists(movieFullPath.decode('utf-8') + ".chapter.xml" ):
            chaptersFile = movieFullPath + ".chapter.xml"
        elif xbmcvfs.exists(str(path).decode('utf-8') + "/chapter.xml"):
            chaptersFile = str(path) + "/chapter.xml"
        
        #Look For TXT Files
        elif xbmcvfs.exists(movieHalfPath.decode('utf-8') + ".chapter.txt"):
            chaptersFile = movieHalfPath + ".chapter.txt"
        elif xbmcvfs.exists(movieFullPath.decode('utf-8') + ".chapter.txt"):
            chaptersFile = movieFullPath + ".chapter.txt"
        elif xbmcvfs.exists(str(path).decode('utf-8') + "/chapter.txt"):
            chaptersFile = str(path) + "/chapter.txt"
        else :
            passChapters = True
        
        # Show Chapters Window if find some chapters
        if not passChapters:
            ui = gui.GUI( "main.xml" , __cwd__, "Default")
            #print "*****excute" , "half:"+movieHalfPath ,"full:"+movieFullPath, "Chapter:"+chaptersFile,  debug             #debug---------------------------------
            service_present = ui.setParameters ( movieFullPath, chaptersFile,  debug )
            if service_present > -1 : ui.doModal()
            #xbmc.executebuiltin('XBMC.ActivateWindow(20000)' )
            if xbmc.getCondVisibility('Player.Paused'): 
                xbmc.Player().pause() # Start Playing if Paused
            del ui
        else :
            #print " *****no-excute" , "half:"+movieHalfPath ,"full:"+movieFullPath, "Chapter:"+chaptersFile,  debug       #debug---------------------------------
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( "No Chapters", "No chapters available for video", 2000) )
        sys.modules.clear()
