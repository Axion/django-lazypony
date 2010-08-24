# -*- coding: utf-8 -*-
"""Input and output functions
"""
import sys
import os
import os.path
from terminate.abstract import color, stdout, stderr

__all__ = ["rl", "casts", "queries",
           "input_object","query","query_list","file_chooser","error_message"]

# this constant is here because float() and int() give error messages
# that would confuse most sane users.

ERROR_MESSAGE = ( color('bright','red') + 'Error: ' + color('default') +
                 '%s' + '\a' + os.linesep )
NICE_INPUT_ERRORS = {
    float: "The input ('%s') must be a number",
    int: "The input ('%s') must be an integer (-1, 0, 1, 2, etc.)"
}

DEFAULT_INPUT_ERRORS = "Bad input (%s)"

def input_object(prompt_text, cast, default=None, castarg=[], castkwarg={}):
    """Gets input from the command line and validates it.
    
    prompt_text
        A string. Used to prompt the user.
    cast
        This can be any callable object (class, function, type, etc). It
        simply calls the cast with the given arguements and returns the 
        result. If a ValueError is raised, it
        will output an error message and prompt the user again.

        Because some builtin python objects don't do casting in the way
        that we might like you can easily write a wrapper function that
        looks and the input and returns the appropriate object or exception.
        Look in the cast submodule for examples.
    default
        function returns this value if the user types nothing in. This is
        can be used to cancel the input so-to-speek
    castarg, castkwarg
        list and dictionary. Extra arguments passed on to the cast.
    """
    while True:
        try:
            t = raw_input(prompt_text)
            if t == '': return default
            value = cast(t, *castarg, **castkwarg)
        except ValueError, details:
            if cast in NICE_INPUT_ERRORS: # see comment above this constant
                stdout.write(ERROR_MESSAGE % (NICE_INPUT_ERRORS[cast] % t))
            else: stdout.write(ERROR_MESSAGE % (DEFAULT_INPUT_ERRORS % str(details)))
            continue
        except EOFError:
            return false
        return value

def query(prompt_text, answers, default=None, list_values = False, ignorecase = True ):
    """Preset a few options
    
    The prompt_text argument is a string, nothing magical.
    
    The answers argument accepts input in two different forms. The simpler form
    (a tuple with strings) looks like:
    
        .. code-block:: Python
        
            ('Male','Female')
    
    And it will pop up a question asking the user for a gender and requiring
    the user to enter either 'male' or 'female' (case doesn't matter unless
    you set the third arguement to false).
    The other form is something like:
    
        .. code-block:: Python
        
            ({'values':('Male','M'),'fg':'cyan'},
            {'values':('Female','F'),'fg':'magenta'})
    
    This will pop up a question with Male/Female (each with appropriate
    colouring). Additionally, if the user types in just 'M', it will be
    treated as if 'Male' was typed in. The first item in the 'values' tuple
    is treated as default and is the one that is returned by the function
    if the user chooses one in that group.
    In addition the function can handle non-string objects quite fine. It
    simple displays the output object.__str__() and compares the user's input
    against that. So the the code
    
        .. code-block:: Python
        
            query("Python rocks? ",(True, False))
    
    will return a bool (True) when the user types in the string 'True' (Of
    course there isn't any other reasonable answer than True anyways :P)
    
    ``default`` is the value function returns if the user types nothing in. This is
    can be used to cancel the input so-to-speek
    
    Using list_values = False will display a list, with descriptions printed out
    from the 'desc' keyword
    """
    answers = list(answers)
    for i in range(len(answers)):
        if not isinstance(answers[i], dict):
            answers[i] = {'values': [answers[i]]}
    try:
        import readline
        import rl
        wordlist = [ str(values) for answer in answers
                    for values in answer['values']]
        completer = rl.ListCompleter(wordlist, ignorecase)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)
    except ImportError:
        pass
    answerslist = []
    if list_values:
        for item in answers:
            answerslist.append(
                color('bright', fg=item.get('fg'), bg=item.get('bg')) +
                str(item['values'][0]) +
                color('default') +
                ' : ' + item['desc'])
        prompt_text += os.linesep + os.linesep.join(answerslist) + os.linesep
    else:
        for item in answers:
            answerslist.append(
                color('bright', fg=item.get('fg'), bg=item.get('bg')) +
                str(item['values'][0]) +
                color('default'))
        prompt_text += '[' + '/'.join(answerslist) + ']'
    while True:
        stdout.write(prompt_text)
        t = raw_input(': ')
        if t == '': return default
        if ignorecase: response = t.lower()
        else: response = t
        for item in answers:
            for a in item['values']:
                if ignorecase and (response == str(a).lower()):
                    return item['values'][0]
                if response == a:
                    return item['values'][0]
        stdout.write(ERROR_MESSAGE % (
                      "Response '%s' not understood, please try again." % t))

def file_chooser(prompt_text = "Enter File: ", default=None, filearg=[], filekwarg={}):
    """A simple tool to get a file from the user. Takes keyworded arguemnts
    and passes them to open().
    
    If the user enters nothing the function will return the ``default`` value.
    Otherwise it continues to prompt the user until it get's a decent response.
    
    filekwarg may contain arguements passed on to ``open()``.
    """
    try:
        import readline
        import rl
        completer = rl.PathCompleter()
        readline.set_completer_delims(completer.delims)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)
    except ImportError:
        pass
    while True:
        f = raw_input(prompt_text)
        if f == '': return default
        f = os.path.expanduser(f)
        if len(f) != 0 and f[0] == os.path.sep:
            f = os.path.abspath(f)
        try:
            return open(f, *filearg, **filekwarg)
        except IOError, e:
            stdout.write(ERROR_MESSAGE % ("unable to open %s : %s" % (f, e)))