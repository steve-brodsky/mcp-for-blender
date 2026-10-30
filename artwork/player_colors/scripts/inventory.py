"""Read glTF source metadata without importing or modifying production assets."""
import hashlib
import io
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
GAME = Path(r'C:\Users\stevi\OneDrive\Documents\space-game-prototype')


def read_glb(path):
    raw = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<III', raw)
    assert magic == 0x46546C67 and version == 2 and length == len(raw), path
    chunks = {}
    offset = 12
    while offset < length:
        size, kind = struct.unpack_from('<II', raw, offset)
        chunks[kind] = raw[offset + 8:offset + 8 + size]
        offset += 8 + size
    return json.loads(chunks[0x4E4F534A]), chunks.get(0x004E4942, b'')


def image_bytes(doc, binary, image, path):
    if 'bufferView' in image:
        view = doc['bufferViews'][image['bufferView']]
        start = view.get('byteOffset', 0)
        return binary[start:start + view['byteLength']]
    uri = image['uri']
    if uri.startswith('data:'):
        import base64
        return base64.b64decode(uri.split(',', 1)[1])
    return (Path(path).parent / uri).read_bytes()


def discover():
    found = {}
    # The prototype contains the current accepted revisions of migrated ships.
    for path in sorted((GAME / 'assets/ships').rglob('*.glb')):
        if any(p in path.parts for p in ('construction', 'debris')) or '_lod' in path.stem:
            continue
        found[path.stem] = path
    for path in sorted((GAME / 'assets/weapons').rglob('*.glb')):
        found[path.stem] = path
    for folder in ('supply_ship', 'mounted turrets', 'corvette - flak'):
        for path in sorted((WORKSPACE / 'artwork' / folder / 'godot/assets').glob('*.glb')):
            if '_lod' not in path.stem:
                found.setdefault(path.stem, path)
    settings=json.loads((ROOT/'assets.json').read_text())
    for key,value in settings.get('extra_sources',{}).items():
        path=Path(value)
        if not path.is_absolute():path=WORKSPACE/path
        assert path.is_file(),str(path)
        found[key]=path
    return {key:path for key,path in found.items()
            if not any(key.startswith(prefix) for prefix in settings['excluded_prefixes'])}


def main():
    from PIL import Image, ImageDraw
    ROOT.mkdir(exist_ok=True)
    records = []
    thumbs = []
    for asset, path in discover().items():
        doc, binary = read_glb(path)
        entry = {'asset': asset, 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'materials': []}
        for index, mat in enumerate(doc.get('materials', [])):
            pbr = mat.get('pbrMetallicRoughness', {})
            item = {'index': index, 'name': mat.get('name', str(index)), 'pbr': pbr, 'emissiveFactor': mat.get('emissiveFactor', [0, 0, 0]), 'alphaMode': mat.get('alphaMode', 'OPAQUE')}
            if 'baseColorTexture' in pbr:
                image_index = doc['textures'][pbr['baseColorTexture']['index']]['source']
                raw = image_bytes(doc, binary, doc['images'][image_index], path)
                im = Image.open(io.BytesIO(raw)).convert('RGBA')
                item['image_size'] = im.size
                item['image_sha256'] = hashlib.sha256(raw).hexdigest()
                tile = Image.new('RGB', (300, 235), '#202731')
                preview = im.copy(); preview.thumbnail((290, 190))
                tile.paste(preview, ((300-preview.width)//2, 40), preview)
                draw = ImageDraw.Draw(tile)
                draw.text((6, 4), asset, fill='white')
                draw.text((6, 20), item['name'][:40], fill='white')
                thumbs.append(tile)
            entry['materials'].append(item)
        records.append(entry)
    (ROOT / 'inventory.json').write_text(json.dumps(records, indent=2))
    cols = 5
    sheet = Image.new('RGB', (cols*300, ((len(thumbs)+cols-1)//cols)*235), '#101820')
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i%cols)*300, (i//cols)*235))
    sheet.save(ROOT / 'source_atlases.jpg')
    print(json.dumps({'assets': len(records), 'textured_materials': len(thumbs), 'names': [r['asset'] for r in records]}))


if __name__ == '__main__':
    main()
