# -*- coding: utf-8 -*-
"""
Primary interface layer for terminal control

This module provides a semi-portable interface between the various methods of
terminal control as the ANSI and win32 methods are quite different.


"""
import sys
import os
import abstract

__all__ = ['DISPLAY_CODES', 'COLORS', 'display', 'reset']

class Control(object):
    """A basic control class.
    
    Used when terminal support can not be determined.
    """
    
    DISPLAY_CODES = ('default', 'bright', 'dim', 'underline', 'blink',
                  'reverse', 'hidden')
    
    # Yellow is a bit weird, xterm and rxvt display dark yellow, while linux and 
    # Windows display a more brown-ish color. Bright yellow is always yellow.
    # order is important here
    COLORS = ('black', 'red', 'green', 'yellow', 'blue', 'magenta',
               'cyan', 'white')
    
    # setf from curses uses the colors in a different order for 
    
    def display(self, codes=[], fg=None, bg=None):
        """Sets the display attributes on the terminal.
        
        For details on arguments see documentation for color function
        in the abstract module.
        """
        return self._display(*Control.formatcodes(codes, fg, bg))
    
    def _display(self, codes, fg, bg):
        pass
    
    def reset(self):
        pass
    
    @staticmethod
    def formatcodes(codes=[], fg=None, bg=None):
        """Makes sure all arguments are valid"""
        if isinstance(codes, basestring):
            codes=[codes]
        else:
            codes = list(codes)
        for code in codes:
            if code not in Control.DISPLAY_CODES:
                raise ValueError, ("'%s' not a valid display value" % code)
        for color in (fg, bg):
            if color != None:
                if color not in Control.COLORS:
                    raise ValueError, ("'%s' not a valid color" % color)
        return [codes, fg, bg]

class ANSI(Control):
    """ANSI version of terminal control.
    
    Based on the ANSI X3.64 standard. See http://en.wikipedia.org/wiki/ANSI_X3.64
    """
    
    # Don't use these alone
    # see http://vt100.net/docs/vt100-ug/chapter3.html
    ESCAPE = "\x1b"
    CSI = ESCAPE +"["
    
    # see the reset method
    RESET_CODE = ESCAPE + "c"
    
    # Display attributes are handled by sending a series of numbers
    # along with special characters. For example \x1b[0m will reset
    # the display back to the default colors and \x1b[1;4;33;41m will
    # result in a very painful underlined bright yellow with red
    # background.
    CODES={
    'default':0,
    'bright':1,
    'dim':2,
    'underline':4,
    'blink':5,
    'reverse':7,
    'hidden':8,
    }
    FG={
    'black':30,
    'red':31,
    'green':32,
    'yellow':33,
    'blue':34,
    'magenta':35,
    'cyan':36,
    'white':37,
    }
    BG={
    'black':40,
    'red':41,
    'green':42,
    'yellow':43,
    'blue':44,
    'magenta':45,
    'cyan':46,
    'white':47
    }
    
    def _display(self, codes, fg, bg):
        abstract.stdout.raw_write(ANSI.displaycode(codes, fg, bg))
        abstract.stdout.flush()
    
    def reset(self):
        """Resets the terminal screen.
        
        Avoid using this method, it will probably
        be moved in the next version.
        """
        abstract.stdout.raw_write(self.RESET_CODE)
        
    @staticmethod
    def displaycode(codes=[], fg=None, bg=None):
        """Generates the proper ANSI code"""
        codes, fg, bg = Control.formatcodes(codes, fg, bg)
        codes = [str(ANSI.CODES[code]) for code in codes]
        if fg != None: codes.append(str(ANSI.FG[fg]))
        if bg != None: codes.append(str(ANSI.BG[bg]))
        return ANSI.CSI + ";".join(codes) + 'm'
    
    @staticmethod
    def readcodes(codes):
        """Reads a list of codes and generates dict"""
        dcodes=[]
        fg = bg = None
        for code in codes:
            code = int(code)
            if code in ANSI.FG.values():
                fg = code % 10
            elif code in ANSI.BG.values():
                bg = code % 10
            elif code in ANSI.CODES.values():
                dcodes.append(code)
            else:
                pass # drop unhandled values
        r = {}
        if len(codes): r['codes'] = [Control.DISPLAY_CODES[c] for c in dcodes]
        if fg != None: r['fg'] = Control.COLORS[fg]
        if bg != None: r['bg'] = Control.COLORS[bg]
        return r

class Win(Control):
    """Windows version of terminal control
    
    This class should not be used by itself, use either Win32 or WinCTypes
    classes that subclasses of this class.
    
    This class makes extensive use of the Windows API
    
    
    The official documentation for the API is on MSDN:
    http://msdn.microsoft.com/library/default.asp?url=/library/en-us/dllproc/base/console_functions.asp
    
    """
    
    STD_OUTPUT_HANDLE = -11
    
    # These contants are defined in PyWin32
    # You can combine the values by doing a bitwise or (|)
    # for example FG_BLUE | FG_RED would give magenta (0x05)
    #
    # these contants are just numbers, It's most useful to think of them in binary,
    # but python has no binary number thing, so I'm displaying them in hex
    FG_BLUE = 1 << 0
    FG_GREEN = 1 << 1
    FG_RED = 1 << 2
    FG_INTENSITY = 1 << 3
    BG_BLUE = 1 << 4
    BG_GREEN= 1 << 5
    BG_RED  = 1 << 6
    BG_INTENSITY = 1 << 7
    FG_ALL = FG_BLUE | FG_GREEN | FG_RED
    BG_ALL = BG_BLUE | BG_GREEN | BG_RED
    
    # there are also these codes, but according to tcsh's win32/console.c:
    # http://cvs.opensolaris.org/source/xref/sfw/usr/src/cmd/tcsh/tcsh-6.12.00/win32/console.c#568
    # COMMON_LVB_REVERSE_VIDEO is buggy, so I'm staying away from it. Future
    # versions should implement COMMON_LVB_UNDERSCORE.
    # COMMON_LVB_REVERSE_VIDEO = 0x4000
    # COMMON_LVB_UNDERSCORE      0x8000
    
    default_attributes = None
    hidden_output = False
    reverse_output = False
    reverse_input = False
    dim_output = False
    real_fg = None
    
    FG = {
    'black': 0,
    'red': FG_RED,
    'green': FG_GREEN,
    'yellow': FG_GREEN | FG_RED,
    'blue': FG_BLUE,
    'magenta': FG_BLUE | FG_RED,
    'cyan': FG_BLUE | FG_GREEN,
    'white': FG_BLUE | FG_GREEN | FG_RED,
    }
    BG = {
    'black':0,
    'red':BG_RED,
    'green':BG_GREEN,
    'yellow':BG_GREEN | BG_RED,
    'blue':BG_BLUE,
    'magenta':BG_BLUE | BG_RED,
    'cyan':BG_BLUE | BG_GREEN,
    'white':BG_BLUE | BG_GREEN | BG_RED,
    }

    def _set_attributes(self, code):
        """ Set console attributes with `code`
        
        Not implemented here. To be implemented by subclasses.
        """
        pass
    
    def _split_attributes(self, attrs):
        """Spilt attribute code
        
        Takes an attribute code and returns a tuple containing
        foreground (fg), foreground intensity (fgi), background (bg), and
        background intensity (bgi)
        """
        fg = attrs & self.FG_ALL
        fgi = attrs & self.FG_INTENSITY
        bg = attrs & self.BG_ALL
        bgi = attrs & self.BG_INTENSITY
        return fg, fgi, bg, bgi
    
    def _cat_attributes(self, fg, fgi, bg, bgi):
        return (fg | fgi | bg | bgi)
    
    def _undim(self):
        self.dim_output = False
        if self.reverse_input:
            a = self._get_attributes() & 0x8f
            self._set_attributes( (self.real_fg * 0x10) | a)
        else:
            a = self._get_attributes() & 0xf8
            self._set_attributes(self.real_fg | a)
    
    def _display_default(self):
        self.hidden_output = False
        self.reverse_output = False
        self.reverse_input = False
        self.dim_output = False
        self.real_fg = self.default_attributes & 0x7
        self._set_attributes(self.default_attributes)

    def _display_bright(self):
        self._undim()
        return self.FG_INTENSITY
    
    def _display_dim(self):
        self.dim_output = True
    
    def _display_reverse(self):
        self.reverse_output = True
    
    def _display_hidden(self):
        self.hidden_output = True
    
    def _display(self, codes, fg, bg):
        color = 0
        for c in codes:
            try:
                f = getattr(self, '_display_' + c)
                out = f()
                if out: color |= out
            except AttributeError:
                pass
        cfg, cfgi, cbg, cbgi = self._split_attributes(self._get_attributes())
        if self.reverse_input:
            cfg, cbg = (cbg // 0x10), (cfg * 0x10)
            cfgi, cbgi = (cbgi // 0x10), (cfgi * 0x10)
        if fg != None:
            color |= self.FG[fg]
            self.real_fg = self.FG[fg]
        else: color |= cfg
        if bg != None:
            color |= self.BG[bg]
        else: color |= cbg
        color |= (cfgi | cbgi)
        fg, fgi, bg, bgi = self._split_attributes(color)
        if self.dim_output:
            # intense black
            fg = 0
            fgi = self.FG_INTENSITY
        if self.reverse_output:
            fg, bg = (bg // 0x10), (fg * 0x10)
            fgi, bgi = (bgi // 0x10), (fgi * 0x10)
            self.reverse_input = True
        if self.hidden_output:
            fg = (bg // 0x10)
            fgi = (bgi // 0x10)
        self._set_attributes(self._cat_attributes(fg, fgi, bg, bgi))
        
    def reset(self):
        """Not yet implemented in the Windows version."""
        pass

class Win32(Win):
    """PyWin32 version of Windows terminal control.
    
    Uses the PyWin32 Libraries <http://sourceforge.net/projects/pywin32/>.
    
    ActiveState has good documentation for them:
    
    Main page:
    http://aspn.activestate.com/ASPN/docs/ActivePython/2.4/pywin32/PyWin32.html
    Console related objects and methods:
    http://aspn.activestate.com/ASPN/docs/ActivePython/2.4/pywin32/PyConsoleScreenBuffer.html
    """
   
    def __init__(self):
        self._stdout_handle = win32console.GetStdHandle(STD_OUTPUT_HANDLE)
        self.default_attributes = self._get_attributes()
        self.real_fg = self.default_attributes & 0x7

    def _set_attributes(self,code):
        self._stdout_handle.SetConsoleTextAttribute(code)
        
    def _get_attributes(self):
        return self._stdout_handle.GetConsoleScreenBufferInfo()['Attributes']

class WinCTypes(Win):
    """CTypes version of Windows terminal control.
    
    It requires the CTypes libraries <http://sourceforge.net/projects/ctypes/>
    
    As of Python 2.5, CTypes is included in Python by default. User's of
    previous version of Python will have to install it if they what to use
    this.
    """
    def __init__(self):
        self._stdout_handle = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        self.default_attributes = self._get_attributes()
        self.real_fg = self.default_attributes & 0x7
   
    def _get_attributes(self):
        # From IPython's winconsole.py, by Alexander Belchenko
        # http://projects.scipy.org/ipython/ipython/browser/ipython/trunk/IPython/winconsole.py
        import struct
        csbi = ctypes.create_string_buffer(22)
        res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self._stdout_handle, csbi)
        (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = \
            struct.unpack("hhhhHhhhhhh", csbi.raw)
        return wattr

    def _set_attributes(self,code):
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._stdout_handle, code)

def get_wrapper():
    """Returns a instance of the Control class (or one of it's sub classes)
    
    The particular class will depend on the platform, and it should have the proper
    methods for the features supported in this module.    
    """
    ANSI_TERMINALS = ('linux','xterm','rxvt')
    
    # check terminal capabilities
    if os.environ.get('TERM') in ANSI_TERMINALS: return ANSI()
    elif 'win32' in sys.platform:
        try:
            import ctypes
            __builtins__['ctypes'] = ctypes
            return WinCTypes()
        except ImportError:
            try:
                import win32console
                __builtins__['win32console'] = win32console
                return Win32()
            except ImportError: return Control()
    elif os.environ.get('TERM') == 'cygwin': return ANSI()
    else: return Control()
    
    
wrapper = get_wrapper()

# TODO: this old stuff needs some cleanup
DISPLAY_CODES = wrapper.DISPLAY_CODES
COLORS = wrapper.COLORS
display = wrapper.display
reset = wrapper.reset

# extra for furture versions

def _get_capabilities():
    """Returns None or a dictionary.
    
    Don't use this yet unless you are sure you know what your doing, it is 
    not well enough tested and is completely missing support for MS Windows.
    """
    
    try: import curses
    except ImportError: return
    
    # make sure sys.stdout hasn't be hijacked and redirected to a regular
    # file
    if not sys.stdout.isatty(): return
    
    try: curses.setupterm()
    except: return
    
    # bol, eol, bos = beginning/end of line/screen etc
    # for info on the values here, see capname's under the terminfo(5) manual
    strings = {
       'up':'cuu1', 'down':'cud1', 'left':'cub1', 'right':'cuf1',
       'bol':'cr', 'bos':'home',
       'clear':'clear', 'clear bol':'el1', 'clear eol':'el', 'clear eos':'ed',
           'clear line':'dl1',
       'bell':'bel',
               }
    
    # in the future this should really use sgr or something, but for now
    # it pretty much does nothing.
    display = {'default':'sgr0','bright':'bold','dim':'dim','reverse':'rev',
                       'underline':'smul'}
    
    # dictionary of terminal capabilities. format and display are filled with
    # items from format_strings and display_strings. Values are set to None
    # if they are not supported.
    cap = {
    'cols' : None, # if these are None, 75 is a fairly safe fall back to use
    'lines' : None,
    'fg' : None, # can change foreground
    'bg' : None, # can change background
    'strings' : dict((string, curses.tigetstr(capname))
                    for string, capname in strings.items()),
    'display' : dict((string, curses.tigetstr(capname))
                     for string, capname in display.items()),
    }
    
    for capability in ('cols','lines'):
        c = curses.tigetnum(capability)
        if c != -1: cap[capability] = c
    
    if curses.tigetstr('setf') != None: cap['fg'] = True
    if curses.tigetstr('setb') != None: cap['bg'] = True
    
    for string, capname in format_strings.items():
        c = curses.tigetstr(capname)
        cap['format'][string] = c
