import logging
import settings
import json
from os import listdir
from os.path import isfile, join, splitext

I18N_DIR = 'i18n'
EXT = '.json'
DEFAULT_LANG = 'en-US'

log = logging.getLogger('ironbot')
msg_map = {}
_ch2lang = {}


def initialize():
    i18n_dir = join(settings.PROJECT_ROOT, I18N_DIR)

    log.debug('Scanning i18n files in {}'.format(i18n_dir))
    f = [(*splitext(f), join(i18n_dir, f)) for f in listdir(i18n_dir) if isfile(join(i18n_dir, f)) and f.endswith(EXT)]

    for lang, ext, full_path in f:
        with open(full_path) as data:
            msg_map[lang] = json.load(data)
            log.debug('File {} loaded'.format(full_path))


def get(key: str, channel_id: int = None) -> str:
    if channel_id is None or channel_id not in _ch2lang:
        lang = DEFAULT_LANG
    else:
        lang = _ch2lang[channel_id]

    if key in msg_map[lang]:
        return msg_map[lang][key]
    else:
        raise ValueError('Key {} not found for language {}'.format(key, lang))
