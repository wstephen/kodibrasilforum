import sys
import os
import xbmc
import struct
DEBUG_MODE = 10

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

# comapatble versions
SETTINGS_VERSIONS = ( "1.0", )
# base paths
BASE_DATA_PATH = os.path.join( "special://temp", "script_data", __scriptname__ )
BASE_SETTINGS_PATH = os.path.join( "special://profile", "script_data", __scriptname__ )

BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
# special action codes
SELECT_ITEM = ( 11, 256, 61453, )
EXIT_SCRIPT = ( 6, 10, 247, 275, 61467, 216, 257, 61448, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
GET_EXCEPTION = ( 216, 260, 61448, )
SELECT_BUTTON = ( 229, 259, 261, 61453, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )
# Log status codes
LOG_INFO, LOG_ERROR, LOG_NOTICE, LOG_DEBUG = range( 1, 5 )

def LOG( status, format, *args ):
    if ( DEBUG_MODE >= status ):
        xbmc.output( "%s: %s\n" % ( ( "INFO", "ERROR", "NOTICE", "DEBUG", )[ status - 1 ], format % args, ) )

#
# String => Integer
#
def toInteger (string):
    try:
        return int( string )
    except :
        return 0

#
# Detect movie title and year from file name...
#
def getMovieTitleAndYear( filename ):
    name = os.path.splitext( filename )[0]

    cutoffs = ['dvdrip', 'dvdscr', 'cam', 'r5', 'limited',
               'xvid', 'h264', 'x264', 'h.264', 'x.264',
               'dvd', 'screener', 'unrated', 'repack', 'rerip', 
               'proper', '720p', '1080p', '1080i', 'bluray', 'hdtv']

    # Clean file name from all kinds of crap...
    for char in ['[', ']', '_', '(', ')','.','-']:
        name = name.replace(char, ' ')
    
    # remove extra and duplicate spaces!
    name = name.strip()
    while name.find('  ') != -1:
        name = name.replace('  ', ' ')
        
    # split to parts
    parts = name.split(' ')
    year = 0
    cut_pos = 256
    for part in parts:
        # check for year
        if part.isdigit():
            n = int(part)
            if n>1930 and n<2050:
                year = part
                if parts.index(part) < cut_pos:
                    cut_pos = parts.index(part)
                
        # if length > 3 and whole word in uppers, consider as cutword (most likelly a group name)
        if len(part) > 3 and part.isupper() and part.isalpha():
            if parts.index(part) < cut_pos:
                cut_pos = parts.index(part)
                
        # check for cutoff words
        if part.lower() in cutoffs:
            if parts.index(part) < cut_pos:
                cut_pos = parts.index(part)
        
    # make cut
    name = ' '.join(parts[:cut_pos])
    return name, year