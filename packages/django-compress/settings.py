SETTINGS['base'] = """

COMPRESS_VERSION = True
COMPRESS_AUTO = False

COMPRESS_JS = {
    'all': {
        'source_filenames': (
                            # js files
                            ),                             
        'output_filename': 'js/all_compressed.r?.js',
    }
}

COMPRESS_CSS = {
    'all': {
        'source_filenames': (
                            # css files
                            ),
                             
        'output_filename': 'html/css/all_compressed.r?.css',
    }        
}
"""

SETTINGS['user'] = """
COMPRESS = False
"""

SETTINGS['production'] = """
COMPRESS = True
"""





