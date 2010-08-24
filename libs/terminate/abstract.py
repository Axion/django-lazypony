# -*- coding: utf-8 -*-
"""
Secondary abstractions for terminal control

The code here is mostly a front-end to the ``control`` module. The OutputStream class
acts as a wrapper for tty pseudo files like sys.stdout and sys.stder and can 
handle several ANSI control codes on multiple platforms.

Here is an example usage.

.. code-block:: Python

    import os
    stdout.write('spam' + 
        color('bright','yellow','white') + 
        'eggs' + 
        color('default') + os.linesep
    )

Warning: on IPython setting sys.stdout to the stdout object in this
module will break readline.
"""

__all__ = ['color', 'OutputStream', 'stdout', 'stderr']

import sys
import os
import re
import control

escape_parts = re.compile('\x01?\x1b\\[([0-9;]*)m\x02?')

def color(codes=[], fg=None, bg=None):
    """
    Returns an ANSI control code. This is useful when writing to an OutputStream.
    
    codes
        A list containing strings. The strings should one of the keys in
        the DISPLAY_CODES constant in the ``control`` module. It can also
        be just a single string.
    fg, bg
        A string. Explicitly for setting the foreground or background. Use
        one of the keys in the COLORS constant in the ``control`` module.
        
    color(('bright','underline'),'blue','white')
        give bright blue foreground and white background with underline
    color(fg='blue')
        gives a blue foreground
    color('default')
        resets the color to the default.
    
    Avoid using black or white. Depending on the situation the default
    background/foreground is normally black or white, but it's hard to
    tell which. Bare terminals are normally white on black, but virtual
    terminals run from X or another GUI system are often black on white.
    This can lead to unpredicatble results. If you want reversed
    colours, use the 'reverse' code, and if you want to set the
    colors back to their original colors, use the 'default' code.
    
    Also, be prudent with your use of 'hidden' and 'blink'. Several terminals
    do not support them (and for good reason too), they can be really
    annoying and make reading difficult.
    """
    return control.ANSI.displaycode(codes, fg, bg)

class OutputStream(object):
    
    def __init__(self, stream):
        self.stream = stream
    
    def raw_write(self, text):
        self.stream.write(text)
    
    # methods below here are also methods of the file object
    
    def write(self, text):
        chunks = escape_parts.split(text)
        i = 0
        for chunk in chunks:
            if chunk != '':
                if i % 2 == 0:
                    self.stream.write(chunk)
                else:
                    c=chunk.split(';')
                    r=control.ANSI.readcodes(c)
                    control.display(**r)
                # failure to flush after ouput can cause weird ordering behaviour
                # when writting to stdout and stderr simutaniously. This should
                # fix the worst of it, but application developers should be warned
                # not to really on the state of things between call between one method
                # call and another
                self.flush()
            i += 1
    
    def writelines(self, lines):
        self.write(lines.join(os.linesep))
    
    def flush(self):
        return self.stream.flush()
    
    def isatty(self,*args,**kwargs):
        return self.stream.isatty(*args,**kwargs)
    
    # these should really never be called, they are here for API
    # compatibility puposes (although I doubt it makes any difference)
    def tell(self,*args,**kwargs):
        return self.stream.tell(*args,**kwargs)
    def truncate(self,*args,**kwargs):
        return self.stream.truncate(*args,**kwargs)
    def readinto(self,*args,**kwargs):
        return self.stream.readinto(*args,**kwargs)
    def readline(self,*args,**kwargs):
        return self.stream.readline(*args,**kwargs)
    def readlines(self,*args,**kwargs):
        return self.stream.readlines(*args,**kwargs)
    def next(self,*args,**kwargs):
        return self.stream.next(*args,**kwargs)
    def read(self,*args,**kwargs):
        return self.stream.read(*args,**kwargs)
    def close(self,*args,**kwargs):
        return self.stream.close(*args,**kwargs)
    def fileno(self,*args,**kwargs):
        return self.stream.fileno(*args,**kwargs)
    def xreadlines(self,*args,**kwargs):
        return self.stream.xreadlines(*args,**kwargs)
    
    def _get_mode(self): return self.stream.mode
    def _set_mode(self, value): self.stream.mode = value
    mode = property(_get_mode, _set_mode)
    
    def _get_newlines(self): return self.stream.newlines
    def _set_newlines(self, value): self.stream.newlines = value
    newlines = property(_get_newlines, _set_newlines)
    
    def _get_encoding(self): return self.stream.encoding
    def _set_encoding(self, value): self.stream.encoding = value
    encoding = property(_get_encoding, _set_encoding)
    
    def _get_softspace(self): return self.stream.softspace
    def _set_softspace(self, value): self.stream.softspace = value
    softspace = property(_get_softspace, _set_softspace)
    
    def _get_name(self): return self.stream.name
    def _set_name(self, value): self.stream.name = value
    name = property(_get_name, _set_name)

# wrapper for sys.stdout
stdout = OutputStream(sys.stdout)

# wrapper for sys.stderr
stderr = OutputStream(sys.stderr)