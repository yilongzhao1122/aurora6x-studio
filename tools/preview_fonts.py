"""Find a caption font on Windows/Linux without regenerating watch fonts."""
import os
from pathlib import Path
from PIL import ImageFont


def caption_font(size):
    for path in [os.environ.get('AURORA_PREVIEW_FONT', ''),
                 'C:/Windows/Fonts/arial.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if path and Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()
