import xml.dom.minidom
import time
import os
import sys
import re
import xbmc
import urllib
import codecs
import xbmcvfs

class ChapterParser(object):
    def __init__(self, chapterfile = None):
        if not chapterfile:
            return False
        self.chapters = []
        self.chaptersFile = chapterfile # Don't need this for now, but reserved for future use
        fileExtension = self.getExtension(chapterfile)
        #print fileExtension
        #print "chapter-file:" + chapterfile
        if fileExtension == 'xml':
            self.chapters = self.processXmlFile(chapterfile)
        elif fileExtension == 'txt':
            self.chapters = self.processTxtFile(urllib.unquote(chapterfile))
        else:
            return True
    
    def get_chapters(self):
        return self.chapters
        
    def secToHuman(self, seconds):
        if seconds < 1:
            return "00:00:00"
        hours = seconds / 3600
        seconds -= 3600*hours
        minutes = seconds / 60
        seconds -= 60*minutes
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    
    def getTimeInSeconds(self, time):
        try:
            Seconds = float(time)
        except:
            Seconds = False
        if not Seconds:
            try:
                Hours, Minutes, Seconds = time.split(':')
                Seconds = float(Seconds) + (float(Minutes) * 60) + ( float(Hours) * 60 * 60)
            except:
                Seconds = False
        if not Seconds:
            try:
                Minutes, Seconds = time.split(':')
                Seconds = float(Seconds) + (float(Minutes) * 60)
            except:
                Seconds = False
        if not Seconds:
            return 0
        return Seconds
    
    def getExtension(self, filename):
        list = filename.split(".")
        return list[len(list) - 1]

    def conv_decoding(self, data):
        lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
                    'shift_jis', 'shift_jis_2004','shift_jisx0213',
                    'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
                    'iso2022_jp_ext','latin_1', 'ascii')
        encoding = ''
        for encoding in lookup:
            try:
                data = data.decode(encoding)
                break
            except:
                pass
        return data, encoding
        
    
    def processTxtFile(self, filename):
        xbmc.log( "%s: %s\n" % ( "INFO", "Processing File " + filename  ) )
        #Try with SVCD Format
        chapters = []
        chapretfile = xbmcvfs.File(filename.decode('utf-8')).read().splitlines()
        try:
            for chapter in chapretfile:
                try:
                    ChapterName, MarkTime = chapter.split('=')
                    ChapterName = ChapterName.strip()
                    #print "ChapterName1:" + ((ChapterName))                                                                                   #debug (Japanese text)
                    #print "ChapterName2:" + (urllib.unquote((ChapterName)).decode('shift_jis')).encode('utf-8')   #debug (Japanese text)
                    #ChapterName = urllib.unquote((ChapterName)).decode('shift_jis')                                              #debug (Japanese text)
                    data,encoding= None,None                                                                   
                    data,encoding = self.conv_decoding(ChapterName)                             
                    #print "###data  :" + data.encode('utf-8')                                                                                     #debug (Japanese text)
                    #print "#encoding:" + encoding                                                                                                       #debug (Japanese text)
                    ChapterName = data            
                    if MarkTime:
                        MarkSeconds = self.getTimeInSeconds(MarkTime.strip())
                        chapters.append({'MarkTime':self.secToHuman(MarkSeconds), 'ChapterName':ChapterName, 'ChapterName2':"", 'ChapterThumb':"", 'MarkSeconds':MarkSeconds})
                except:
                    pass
        except:
            return False
            
        return chapters
        
    
    def processXmlFile(self, filename):
        xbmc.log( "%s: %s\n" % ( "INFO", "Processing File " + filename  ) )
        chapters = []
        try:
            chapretfile = xml.dom.minidom.parse( xbmcvfs.File(filename.decode('utf-8')))
            chaptersDoc = chapretfile.getElementsByTagName("chapter")
            
            for chapter in chaptersDoc:
                MarkTime = chapter.attributes.get("mark") and  chapter.attributes["mark"].value or Null
                ChapterName = chapter.attributes.get("title") and chapter.attributes["title"].value or ""
                ChapterName2 = chapter.attributes.get("title2") and chapter.attributes["title2"].value or ""
                ChapterThumb = chapter.attributes.get("thumb") and chapter.attributes["thumb"].value or ""
                if ChapterThumb <> "":
                    ChapterThumb = str(xbmc.translatePath(os.path.dirname(filename).decode('utf-8') + "/" + ChapterThumb)) #.replace('\\', '\\\\')
                # xbmc.log( "%s: %s\n" % ( "INFO", "MARKTIME " + filename  ) )
                if MarkTime:
                    #print "ChapterName:" + ChapterName.encode('utf-8')                           #debug
                    MarkSeconds = self.getTimeInSeconds(MarkTime)
                    chapters.append({'MarkTime':MarkTime, 'ChapterName':ChapterName, 'ChapterName2':ChapterName2, 'ChapterThumb':ChapterThumb, 'MarkSeconds':MarkSeconds})
            
            
        except:
            return False
            
        return chapters
        