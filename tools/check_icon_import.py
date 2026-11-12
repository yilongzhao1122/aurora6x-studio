"""Check imported pixel art, stable font coordinates and source-based overlap.

Also emits native-size/before-after comparison sheets. No simulator is emulated.
"""
from collections import deque
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw
from generate_icons import icons, import_master, master_mask
from preview_fonts import caption_font
from render_preview import render, ATLAS, META

P = Path(__file__).resolve().parents[1]
OUT = P/'docs/icon-validation'
NAMES = list(icons)
IMPORTED = ['steps', 'flame', 'heart', 'battery', 'mountain', 'sun']


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def glyph(name, size, before=False):
    i = NAMES.index('sun' if before and name=='weather_sun' else name)
    path = OUT/'before' if before else P/'resources/fonts'
    with Image.open(path/f'Icons{size}.png') as atlas:
        x, y = i % 8 * size, i // 8 * size
        return atlas.convert('RGBA').crop((x, y, x+size, y+size))


def regions(mask, foreground=True, diagonal=False):
    points = {(x, y) for y in range(mask.height) for x in range(mask.width)
              if bool(mask.getpixel((x, y))) == foreground}
    result = []
    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        offsets += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    while points:
        seed = points.pop()
        region = {seed}
        queue = deque([seed])
        while queue:
            x, y = queue.popleft()
            for dx, dy in offsets:
                pt = x+dx, y+dy
                if pt in points:
                    points.remove(pt)
                    region.add(pt)
                    queue.append(pt)
        result.append(region)
    return result


def font_chars(path):
    return [dict(re.findall(r'(\w+)=(\d+)', line))
            for line in path.read_text(encoding='utf-8').splitlines()
            if line.startswith('char ')]


def check_assets():
    report = load_json(P/'tools/icon-import-report.json')
    quality = {}
    for size in (16, 24):
        key = f'Icons{size}'
        assert font_chars(P/f'resources/fonts/{key}.fnt')[:39] == font_chars(OUT/f'before/{key}.fnt')
        chars = font_chars(P/f'resources/fonts/{key}.fnt')
        assert len(chars) == len(NAMES) == 40
        quality[str(size)] = {}
        for i, name in enumerate(NAMES):
            tile = glyph(name, size)
            alpha = tile.getchannel('A')
            assert set(alpha.getdata()) <= {0, 255}, (name, size, 'alpha')
            assert all(rgb == (255, 255, 255) for rgb in tile.convert('RGB').getdata())
            m = META[key]['chars'][chr(0xe000+i)]
            for field, meta in [('x', 'x'), ('y', 'y'), ('width', 'w'), ('height', 'h'),
                                ('xoffset', 'xo'), ('yoffset', 'yo'), ('xadvance', 'a')]:
                assert int(chars[i][field]) == m[meta], (key, i, field)
            assert int(chars[i]['id']) == 0xe000+i
            if name not in IMPORTED:
                assert tile.tobytes() == glyph(name, size, True).tobytes(), (name, size, 'fallback changed')
                continue
            entry = report['sizes'][str(size)][name]
            master = P/'artwork/icon-masters'/f'{name}.png'
            assert entry['sha256'] == hashlib.sha256(master.read_bytes()).hexdigest()
            assert entry['hints_applied']
            margin = 1 if size == 16 else 2
            x0, y0, x1, y1 = alpha.getbbox()
            assert min(x0, y0, size-x1, size-y1) >= margin
            foreground = regions(alpha, diagonal=True)
            holes = [r for r in regions(alpha, False) if all(0 < x < size-1 and 0 < y < size-1 for x, y in r)]
            assert min(map(len, foreground)) > 1, (name, size, 'isolated pixel')
            quality[str(size)][name] = {'bbox': list(alpha.getbbox()),
                'opaque_pixels': sum(bool(v) for v in alpha.getdata()),
                'components_8_connected': len(foreground), 'holes_4_connected': len(holes),
                'hole_areas': sorted(map(len, holes))}
            expected = {'steps': (2, 0), 'flame': (1, 1), 'heart': (1, 0),
                        'battery': (2, 1), 'sun': (2, 1)}
            if name in expected:
                assert (len(foreground), len(holes)) == expected[name], (name, size, quality[str(size)][name])
            if name == 'mountain':
                assert len(foreground) == 1 and len(holes) >= 2
            assert Image.open(P/f'artwork/icon-pixels/{size}/{name}.png').tobytes() == tile.tobytes()
    # Runtime code, numeric bold fonts, menu fonts and settings mapping unchanged.
    baseline = load_json(OUT/'baseline-sha256.json')
    # 3.2.0 deliberately changes view/theme code and typography. Protect the unchanged
    # data readers, app entry/delegate, and defaults; check all old icon cells above.
    protected = [f for f in baseline if f in ['source/AuroraApp.mc','source/AuroraSettingsDelegate.mc',
                 'source/CalendarData.mc','source/MoonData.mc']]
    for f in protected:
        assert hashlib.sha256((P/f).read_bytes()).hexdigest() == baseline[f], f
    # Only the two small icon atlases belong to the device resource tree.
    assert not any((P/'resources').rglob('*master*'))
    assert not re.search(r'artwork|icon-masters|icon-pixels', (P/'monkey.jungle').read_text())
    assert not any(p.stem in IMPORTED for p in (P/'resources').rglob('*.png'))
    # Exercise a new named master and stale hints without mutating project outputs.
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp)/'test.png'
        source = Image.new('RGBA', (60, 30))
        ImageDraw.Draw(source).rectangle((5, 5, 54, 24), fill='red')
        source.save(f)
        tile, entry = import_master(f, 16, {'sha256': 'old', 'sizes': {'16': {'clear': [[7, 7]]}}})
        assert not entry['hints_applied'] and tile.getpixel((7, 7)) == 255
        assert tile.getbbox() == (1, 4, 15, 10) or tile.getbbox() == (1, 5, 15, 11)
        Image.new('RGBA', (20, 20)).save(f)
        try:
            master_mask(f)
        except ValueError:
            pass
        else:
            raise AssertionError('Empty master was accepted')
    return quality, len(protected)


def text_pixels(command):
    x, y, font, text, justify = command['args']
    meta = META[font]
    if justify == 1:
        x -= sum(meta['chars'][ch]['a'] for ch in text)//2
    points = set()
    for ch in text:
        m = meta['chars'][ch]
        mask = ATLAS[font].getchannel('A').crop((m['x'], m['y'], m['x']+m['w'], m['y']+m['h']))
        ox, oy = round(x+m['xo']), round(y+m['yo'])
        points.update((ox+xx, oy+yy) for yy in range(mask.height) for xx in range(mask.width)
                      if mask.getpixel((xx, yy)))
        x += m['a']
    return points


def layout_checks():
    result = subprocess.run(['node', str(P/'tools/icon_layout_cases.cjs')], cwd=P,
                            check=True, capture_output=True, encoding='utf-8')
    cases = [json.loads(line) for line in result.stdout.splitlines()]
    collisions = []
    comparisons = 0
    minimum_field_gap = 280
    selected = {}
    for scene in cases:
        commands = [c for c in scene['commands'] if c['op'] == 'drawText']
        icon_ink = [(c, text_pixels(c)) for c in commands if c['args'][2].startswith('Icons')]
        text_ink = [(c, text_pixels(c)) for c in commands if not c['args'][2].startswith('Icons')]
        for icon, a in icon_ink:
            for text, b in text_ink:
                comparisons += 1
                overlap = a & b
                if overlap:
                    collisions.append({'case': scene['label'], 'icon_id': ord(icon['args'][3])-0xe000,
                                       'text': text['args'][3], 'overlap_pixels': len(overlap)})
            ix, iy, font, _, _ = icon['args']
            if font == 'Icons16' and ix in (106, 189) and iy in (187, 213):
                adjacent = next(c for c in commands if c['args'][0] == ix+19 and c['args'][1] == iy-1)
                b = text_pixels(adjacent)
                minimum_field_gap = min(minimum_field_gap, min(x for x, y in b)-max(x for x, y in a)-1)
        if scene['label'] in ['default', 'imports', 'sleep', 'low-memory']:
            selected[scene['label']] = scene
    (OUT/'overlap-details.json').write_text(json.dumps(collisions, indent=2), encoding='utf-8')
    assert not collisions, f'Icon/text overlap: {collisions[:8]}'
    return {'cases': len(cases), 'icon_text_pairs': comparisons, 'collisions': collisions,
            'minimum_C2_C5_blank_columns': minimum_field_gap,
            'scope': 'Translated source with fixtures and actual PNG glyph masks; not Garmin VM'}, selected


def paste_rgba(canvas, tile, xy, scale=1):
    if scale != 1:
        tile = tile.resize((tile.width*scale, tile.height*scale), Image.Resampling.NEAREST)
    canvas.paste(tile, xy, tile)


def comparison_sheets(selected):
    f, small = caption_font(22), caption_font(15)
    # A compact 1x sheet contains genuine native pixels; view at 100%.
    native = Image.new('RGB', (840, 290), '#151a24')
    d = ImageDraw.Draw(native)
    d.text((18, 12), 'NATIVE PIXELS / 100% / before -> after', font=f, fill='white')
    d.text((18, 45), '16px top row; 24px bottom row. Original numeric bold fonts retained.', font=small, fill='#afbdcd')
    for i, name in enumerate(IMPORTED):
        x = 20+i*138
        d.text((x, 85), name, font=small, fill='white')
        for size, y in [(16, 118), (24, 192)]:
            paste_rgba(native, glyph(name, size, True), (x, y))
            paste_rgba(native, glyph(name, size), (x+45, y))
            d.text((x+5, y+30), f'{size}px', font=small, fill='#afbdcd')
    native.save(OUT/'icons-native.png')
    history = Image.new('RGB', (1160, 850), '#151a24')
    d = ImageDraw.Draw(history)
    d.text((18, 12), 'BEFORE / AFTER AT BOTH NATIVE SIZES / NEAREST-NEIGHBOUR x6', font=f, fill='white')
    for i, name in enumerate(IMPORTED):
        x = 20+i*190
        d.text((x, 52), name, font=f, fill='white')
        for size, before, y in [(16, True, 120), (16, False, 280), (24, True, 460), (24, False, 660)]:
            d.text((x, y-27), f'{size}px '+('before' if before else 'after'), font=small, fill='#afbdcd')
            paste_rgba(history, glyph(name, size, before), (x, y), 6)
    history.save(OUT/'icons-before-after-enlarged.png')
    zoom = Image.new('RGB', (1140, 660), '#151a24')
    d = ImageDraw.Draw(zoom)
    d.text((18, 10), 'MASTER / 16px x8 / 24px x8 / independent pixel hints', font=f, fill='white')
    for i, name in enumerate(IMPORTED):
        x = 18+i*186
        d.text((x, 48), name, font=small, fill='white')
        master = Image.open(P/'artwork/icon-masters'/f'{name}.png').convert('RGBA')
        master = master.crop(master.getchannel('A').getbbox())
        master.thumbnail((115, 105), Image.Resampling.LANCZOS)
        paste_rgba(zoom, master, (x+(160-master.width)//2, 85+(105-master.height)//2))
        paste_rgba(zoom, glyph(name, 16), (x+16, 224), 8)
        paste_rgba(zoom, glyph(name, 24), (x-2, 400), 8)
    d.text((18, 620), 'White RGB; alpha {0,255}; 1px / 2px minimum transparent margin; nearest-neighbour enlargement.', font=small, fill='#afbdcd')
    zoom.save(OUT/'icons-enlarged.png')
    before_atlas = dict(ATLAS)
    for size in (16, 24):
        before_atlas[f'Icons{size}'] = Image.open(OUT/f'before/Icons{size}.png').convert('RGBA')
    faces = Image.new('RGB', (1170, 760), '#151a24')
    d = ImageDraw.Draw(faces)
    d.text((20, 12), '280 x 280 NATIVE FACE / SOURCE FIXTURES / NOT SIMULATOR CAPTURES', font=f, fill='white')
    for row, label in enumerate(['default', 'imports']):
        scene_path = OUT/f'{label}-commands.json'
        scene_path.write_text(json.dumps(selected[label]), encoding='utf-8')
        before = render(scene_path, before_atlas)
        after = render(scene_path)
        y = 90+row*330
        d.text((20, y-30), label+' / before', font=small, fill='white')
        d.text((320, y-30), 'after / native 280px', font=small, fill='white')
        d.text((625, y-30), 'data region / after x3', font=small, fill='white')
        faces.paste(before, (20, y))
        faces.paste(after, (320, y))
        faces.paste(after.crop((100, 178, 267, 234)).resize((501, 168), Image.Resampling.NEAREST), (625, y+40))
        after.save(OUT/f'face-{label}-native.png')
        after.resize((1120, 1120), Image.Resampling.NEAREST).save(OUT/f'face-{label}-4x.png')
    faces.save(OUT/'face-comparison.png')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    quality, protected = check_assets()
    layout, selected = layout_checks()
    comparison_sheets(selected)
    report = {'glyphs': 40, 'imported': IMPORTED, 'fallback': 34,
              'protected_files_unchanged': protected, 'quality': quality, 'layout': layout}
    (OUT/'validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"PASS 6 PNG imports / 34 exact fallback glyphs at both sizes; {protected} protected files unchanged")
    print(f"PASS {layout['cases']} source fixture layouts / {layout['icon_text_pairs']} icon-text pairs / zero overlapping pixels")
    print(f"C2-C5 minimum blank columns between icon ink and adjacent numbers: {layout['minimum_C2_C5_blank_columns']}")
