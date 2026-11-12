"""Build native monochrome icon fonts, optionally importing named PNG masters.

artwork/icon-masters/<name>.png overrides only that icon. Reviewed, size-specific
pixel hints live beside the masters and are bound to the master SHA-256.
No master or hint file is referenced by the device resource tree.
"""
from pathlib import Path
import argparse
import hashlib
import json, math
from PIL import Image, ImageDraw, ImageOps
P=Path(__file__).resolve().parents[1]
# Coordinates inside 16x16, shared by Monkey C and the offline preview.
icons={
'steps':[['ellipse',2,1,5,7],['ellipse',8,4,12,11],['poly',[[3,9],[6,8],[7,13],[4,15]]],['poly',[[10,12],[13,11],[14,14],[12,15]]]],
'flag':[['line',3,1,3,15],['poly',[[4,2],[10,2],[12,4],[15,4],[15,10],[10,10],[8,8],[4,8]]]],
'pin':[['ellipse',3,0,13,10],['poly',[[3,6],[13,6],[8,16]]],['hole',6,3,10,7]],
'flame':[['poly',[[7,0],[12,6],[14,11],[12,15],[4,15],[2,10],[5,5],[5,10],[8,7]]],['cutpoly',[[8,8],[11,12],[9,14],[6,13]]]],
'stairs':[['line',1,14,5,14],['line',5,14,5,10],['line',5,10,9,10],['line',9,10,9,6],['line',9,6,13,6],['line',13,6,13,2]],
'heart':[['ellipse',1,3,8,10],['ellipse',7,3,14,10],['poly',[[1,7],[14,7],[8,15]]]],
'battery':[['rect',1,4,13,12],['line',14,6,14,10],['fill',3,6,9,10]],
'bolt':[['poly',[[9,0],[2,9],[7,9],[5,16],[14,6],[9,6]]]],
'drop':[['poly',[[8,0],[2,9],[3,13],[8,16],[13,13],[14,9]]]],
'lungs':[['line',8,0,8,8],['line',8,6,5,9],['line',8,6,11,9],['poly',[[5,4],[2,7],[1,13],[5,15],[6,10]]],['poly',[[11,4],[14,7],[15,13],[11,15],[10,10]]]],
'clock':[['circle',8,8,6],['line',8,3,8,8],['line',8,8,12,10]],
'gauge':[['circle',8,8,6],['line',8,8,12,4],['fill',3,13,13,15]],
'mountain':[['poly',[[0,14],[6,3],[10,9],[12,6],[16,14]]],['cutpoly',[[4,8],[6,5],[8,8]]]],
'weight':[['rect',2,5,14,15],['circle',8,4,3]],
'sun':[['circle',8,8,4],['line',8,0,8,2],['line',8,14,8,16],['line',0,8,2,8],['line',14,8,16,8],['line',2,2,4,4],['line',12,12,14,14],['line',2,14,4,12],['line',12,4,14,2]],
'thermo':[['circle',6,12,3],['rect',5,1,7,11]],
'cloud':[['ellipse',1,5,9,12],['ellipse',5,1,13,11],['ellipse',10,5,16,12],['fill',4,8,13,12]],
'wind':[['line',1,4,14,4],['line',1,8,11,8],['line',1,12,14,12],['line',14,4,12,2],['line',14,12,12,14]],
'down':[['line',8,0,8,13],['poly',[[2,8],[8,16],[14,8]]]],
'up':[['line',8,3,8,16],['poly',[[2,8],[8,0],[14,8]]]],
'bt':[['line',7,0,7,16],['line',7,0,13,5],['line',13,5,3,13],['line',3,3,13,11],['line',13,11,7,16]],
'alarm':[['circle',8,9,5],['line',8,5,8,9],['line',8,9,11,9],['line',1,3,4,1],['line',12,1,15,3],['line',4,14,3,16],['line',12,14,13,16]],
'bell':[['ellipse',4,3,12,13],['poly',[[4,7],[12,7],[14,13],[2,13]]],['fill',7,0,9,3],['fill',7,14,9,16]],
'dnd':[['rect',2,2,14,14],['line',0,16,16,0]],
'rise':[['line',0,14,16,14],['line',2,11,14,11],['circle',8,10,4],['poly',[[5,3],[8,0],[11,3]]]],
'set':[['line',0,14,16,14],['line',2,11,14,11],['circle',8,10,4],['poly',[[5,0],[8,3],[11,0]]]],
}

icons.update({
 'oxygen':[['circle',6,6,4],['line',11,9,14,9],['line',14,9,14,11],['line',14,11,11,14],['line',11,14,15,14]],
 'body':[['rect',1,3,14,13],['poly',[[8,4],[5,8],[8,8],[6,12],[11,7],[8,7]]]],
 'stress':[['line',1,9,4,9],['line',4,9,6,4],['line',6,4,9,13],['line',9,13,11,7],['line',11,7,15,7]],
 'bike':[['circle',4,11,3],['circle',12,11,3],['line',4,11,7,5],['line',7,5,12,11],['line',4,11,10,11],['line',10,11,12,3],['line',11,3,14,3]],
 'run':[['circle',10,2,1],['line',8,5,10,8],['line',8,5,5,8],['line',10,8,14,8],['line',8,6,7,10],['line',7,10,3,14],['line',7,10,11,11],['line',11,11,12,15]],
 'humidity':[['circle',4,4,2],['circle',12,12,2],['line',3,14,13,2]],
 'partly':[['circle',5,5,3],['line',5,0,5,1],['line',0,5,1,5],['ellipse',4,7,12,13],['ellipse',8,5,14,13],['fill',7,10,14,13]],
 'rain':[['ellipse',1,3,8,9],['ellipse',5,1,12,9],['ellipse',9,4,15,9],['fill',4,6,12,9],['line',4,11,2,14],['line',9,11,7,14],['line',14,11,12,14]],
 'snow':[['line',8,1,8,15],['line',2,4,14,12],['line',2,12,14,4],['line',6,2,8,4],['line',10,2,8,4],['line',6,14,8,12],['line',10,14,8,12]],
 'storm':[['ellipse',1,3,8,9],['ellipse',5,1,12,9],['ellipse',9,4,15,9],['fill',4,6,12,9],['poly',[[8,8],[5,12],[8,12],[6,15],[12,10],[9,10]]]],
 'fog':[['line',2,4,14,4],['line',0,8,11,8],['line',4,12,15,12]],
 'unknown':[['line',5,3,11,3],['line',11,3,12,5],['line',12,5,8,9],['line',8,9,8,11],['fill',8,14,8,14]],
 'move':[['circle',9,2,1],['line',8,5,7,10],['line',7,10,3,15],['line',7,10,12,14],['line',5,7,8,5],['line',8,5,12,8]],
})
icons['weather_sun']=icons['sun']
names = list(icons)  # Never derive IDs from directory order or the set of imports.


def draw_original(commands, size, label=None):
    """The previous drawing definitions and quantization, unchanged."""
    tile = Image.new('L', (size, size))
    d = ImageDraw.Draw(tile)
    def q(v):
        return 1 + round(v * (size - 3) / 16)
    width = 1 if size == 16 else 2
    for cmd in commands:
        op, *v = cmd
        col = 0 if op in ('hole', 'cutpoly') else 255
        if op == 'line':
            d.line(tuple(q(z) for z in v), fill=col, width=width)
        elif op in ('rect', 'fill', 'ellipse', 'hole'):
            box = tuple(q(z) for z in v)
            if op == 'rect':
                d.rectangle(box, outline=col, width=width)
            elif op == 'fill':
                d.rectangle(box, fill=col)
            else:
                d.ellipse(box, fill=col)
        elif op == 'circle':
            x, y, r = v
            d.ellipse((q(x-r), q(y-r), q(x+r), q(y+r)), outline=col, width=width)
        else:
            d.polygon([(q(x), q(y)) for x, y in v[0]], fill=col)
    # Preserve the shipped 3.1.x polygon edge tie-breaks across Pillow versions.
    # The original commands stay unchanged; some Pillow builds fill these three
    # boundary pixels differently. They are transparent in the supplied atlas.
    edge_pixels = {('bolt', 16): (4, 14), ('bolt', 24): (7, 22), ('body', 16): (5, 11)}
    if (label, size) in edge_pixels:
        tile.putpixel(edge_pixels[(label, size)], 0)
    return tile


def master_mask(path):
    with Image.open(path) as image:
        rgba = image.convert('RGBA')
    alpha = rgba.getchannel('A')
    if alpha.getextrema()[0] == 255:
        # Also accept flat opaque black/white artwork. Infer the background from
        # the border; transparency remains preferable for coloured artwork.
        alpha = ImageOps.grayscale(rgba)
        border = list(alpha.crop((0, 0, alpha.width, 1)).getdata())
        border += list(alpha.crop((0, alpha.height-1, alpha.width, alpha.height)).getdata())
        if sum(border) / len(border) > 127:
            alpha = ImageOps.invert(alpha)
    box = alpha.point(lambda v: 255 if v >= 32 else 0).getbbox()
    if box is None:
        raise ValueError(f'Empty icon master: {path}')
    return alpha.crop(box)


def import_master(path, size, profile):
    """Resample each native size from the master, then apply reviewed pixel hints."""
    mask = master_mask(path)
    settings = profile.get('sizes', {}).get(str(size), {})
    margin = 1 if size == 16 else 2
    extent = settings.get('extent', size - 2 * margin)
    threshold = settings.get('threshold', 128)
    if not margin <= extent <= size - 2 * margin or not 1 <= threshold <= 254:
        raise ValueError(f'Invalid import profile for {path.stem}/{size}')
    scale = extent / max(mask.size)
    dims = tuple(max(1, round(v * scale)) for v in mask.size)
    resized = mask.resize(dims, Image.Resampling.LANCZOS)
    resized = resized.point(lambda v: 255 if v >= threshold else 0)
    tile = Image.new('L', (size, size))
    tile.paste(resized, ((size-dims[0])//2, (size-dims[1])//2))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    # A replacement master must not inherit pixel edits meant for the old art.
    hints_match = profile.get('sha256') == digest
    if hints_match:
        for key, value in [('set', 255), ('clear', 0)]:
            for x, y in settings.get(key, []):
                if not margin <= x < size-margin or not margin <= y < size-margin:
                    raise ValueError(f'Pixel hint outside safe area: {path}/{size}/{x},{y}')
                tile.putpixel((x, y), value)
    box = tile.getbbox()
    if box is None or not (box[0] >= margin and box[1] >= margin and
                           box[2] <= size-margin and box[3] <= size-margin):
        raise ValueError(f'Empty glyph or missing transparent margins: {path}/{size}')
    return tile, {'master': path.name, 'sha256': digest, 'bbox': list(box),
                  'threshold': threshold, 'extent': extent,
                  'hints_applied': hints_match,
                  'set': settings.get('set', []) if hints_match else [],
                  'clear': settings.get('clear', []) if hints_match else []}


def generate(masters_dir):
    contract = json.loads((P/'tools/icons.json').read_text(encoding='utf-8'))
    if contract['names'] != names or contract['commands'] != icons:
        raise ValueError('Icon IDs/definitions differ from tools/icons.json; review the mapping first')
    font_meta = json.loads((P/'tools/font-metrics.json').read_text(encoding='utf-8'))
    profile_path = masters_dir/'pixel-hints.json'
    profiles = json.loads(profile_path.read_text(encoding='utf-8')) if profile_path.exists() else {}
    unknown = sorted(p.stem for p in masters_dir.glob('*.png') if p.stem not in icons)
    if unknown:
        print('WARNING: unrecognized masters ignored:', ', '.join(unknown))
    report = {'names': names, 'sizes': {}}
    # Build both sizes before writing any runtime resources.
    outputs = []
    native_tiles = []
    for size in (16, 24):
        name = f'Icons{size}'
        cols = 8
        atlas = Image.new('RGBA', (cols*size, math.ceil(len(icons)/cols)*size))
        meta = {}
        entries = {}
        lines = [f'info face="AuroraIcons" size={size} unicode=1 smooth=0 aa=1',
                 f'common lineHeight={size} base={size} scaleW={atlas.width} scaleH={atlas.height} pages=1 packed=0',
                 f'page id=0 file="{name}.png"', f'chars count={len(icons)}']
        for i, (label, commands) in enumerate(icons.items()):
            master = masters_dir/f'{label}.png'
            if master.is_file():
                tile, entry = import_master(master, size, profiles.get(label, {}))
                entries[label] = {'id': i, 'source': 'png', **entry}
            else:
                tile = draw_original(commands, size, label)
                entries[label] = {'id': i, 'source': 'original', 'bbox': list(tile.getbbox())}
            assert set(tile.getdata()) <= {0, 255}
            x, y = i % cols * size, i // cols * size
            white = Image.new('RGBA', (size, size), 'white')
            white.putalpha(tile)
            atlas.paste(white, (x, y))
            if master.is_file():
                native_tiles.append((size, label, white))
            c = chr(0xe000+i)
            meta[c] = {'x': x, 'y': y, 'w': size, 'h': size, 'xo': 0, 'yo': 0, 'a': size}
            lines.append(f'char id={ord(c)} x={x} y={y} width={size} height={size} xoffset=0 yoffset=0 xadvance={size} page=0 chnl=15')
        outputs.append((name, atlas, '\n'.join(lines)))
        font_meta[name] = {'height': size, 'chars': meta}
        report['sizes'][str(size)] = entries
    for name, atlas, fnt in outputs:
        atlas.save(P/f'resources/fonts/{name}.png')
        (P/f'resources/fonts/{name}.fnt').write_text(fnt, encoding='utf-8')
    for size, label, tile in native_tiles:
        target = P/f'artwork/icon-pixels/{size}'
        target.mkdir(parents=True, exist_ok=True)
        tile.save(target/f'{label}.png')
    (P/'tools/font-metrics.json').write_text(json.dumps(font_meta, ensure_ascii=False), encoding='utf-8')
    # Keep font resources registered after on-watch/typography regeneration.
    (P/'resources/fonts/fonts.xml').write_text('<fonts>'+''.join(f'<font id="{n}" filename="{n}.fnt"/>' for n in font_meta)+'</fonts>', encoding='utf-8')
    # Existing FaceIcons.mc and icons.json define the stable runtime IDs.
    (P/'tools/icon-import-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    count = sum(v['source'] == 'png' for v in report['sizes']['16'].values())
    print(f'Generated {len(names)} icons at native 16/24 px: {count} PNG masters, {len(names)-count} original definitions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--masters-dir', type=Path, default=P/'artwork/icon-masters',
                        help='Named PNG masters directory (default: artwork/icon-masters)')
    args = parser.parse_args()
    generate(args.masters_dir)
