import os
import sys

'''
Main app Section
'''
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, os.pardir))
DEBUG = bool(os.getenv('DEBUG', 0)) or 'pydevd' in sys.modules


'''
Bot Section
'''
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', 'token-placeholder')
BOT = {
    'description': 'A simple utility bot for MapleRoyals Maple Story server',
    'command_prefix': os.getenv('COMMAND_PREFIX', '!')
}


'''
Parsing Section
'''
BF4_PARSER = 'lxml'


'''
Logger Section
'''
LOGGER_IRONBOT = 'ironbot'
LOGGER_HIDDENSTREET = 'hiddenstreet'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)8s %(name)s %(module)s '
                      '%(process)d %(thread)d  %(message)s'
        },
        'timestamped': {
            'format': '%(asctime)s %(levelname)8s %(name)s  %(message)s'
        },
        'simple': {
            'format': '%(levelname)8s  %(message)s'
        },
        'performance': {
            'format': '%(asctime)s %(process)d | %(thread)d | %(message)s',
        },
    },
    'filters': {},
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'timestamped',
        },
    },
    'loggers': {
        LOGGER_IRONBOT: {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        LOGGER_HIDDENSTREET: {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}
