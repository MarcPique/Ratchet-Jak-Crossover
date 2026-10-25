"""Verify corrective GLB conversion preserves all original rig, clip and binary data."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def read_glb(path):
    data = path.read_bytes()
    magic, version, total = struct.unpack_from('<4sII', data)
    assert magic == b'glTF' and version == 2 and total == len(data)
    offset, chunks = 12, []
    while offset < len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        chunks.append((kind, data[offset:offset + size]))
        offset += size
    return json.loads(chunks[0][1]), chunks[1:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.staged / 'characters.local.json').read_text())
    eyes_path = args.staged / 'eyes.local.json'
    eyes = json.loads(eyes_path.read_text()) if eyes_path.exists() else None
    result = {'schema': 1, 'characters': {}, 'verified': False}
    for name, asset in manifest['characters'].items():
        original, binary = read_glb(Path(asset['file']))
        converted, converted_binary = read_glb(args.staged / asset['asset'])
        assert binary == converted_binary, f'{name}: source BIN payload changed'
        indices = {p['attributes']['POSITION'] for m in original['meshes'] for p in m['primitives']}
        for index in indices:
            assert len(converted['accessors'][index]['min']) == 3
            assert len(converted['accessors'][index]['max']) == 3
            for key in ('min', 'max'):
                original['accessors'][index].pop(key, None)
                converted['accessors'][index].pop(key, None)
        eye_materials = []
        if eyes:
            eye_report = eyes['characters'][name]
            assert hashlib.sha256((args.staged / asset['asset']).read_bytes()).hexdigest() == eye_report['staged_sha256']
            for index, material in enumerate(original['materials']):
                if not material.get('name', '').startswith('programmer_eye_'):
                    continue
                # Only the explicitly declared material correction is allowed.
                expected = json.loads(json.dumps(material))
                pbr = expected['pbrMetallicRoughness']
                pbr.pop('metallicRoughnessTexture', None)
                pbr.update(metallicFactor=0.0, roughnessFactor=0.6)
                expected.pop('extensions', None)
                expected['alphaMode'] = 'OPAQUE'
                assert converted['materials'][index] == expected, f'{name}: unexpected eye material edits'
                converted['materials'][index] = material
                texture = original['textures'][pbr['baseColorTexture']['index']]
                image_index = texture['source']
                image = converted['images'][image_index]
                assert image['uri'].startswith('data:image/png;base64,')
                image['uri'] = original['images'][image_index]['uri']
                eye_materials.append(material['name'])
            assert len(eye_materials) == 2
        assert original == converted, f'{name}: rig, animation or other source metadata changed'
        result['characters'][name] = {'binary_unchanged': True, 'rig_and_clips_unchanged': True,
            'joints': asset['joints'], 'clips': len(asset['animations']), 'restored_eye_materials': eye_materials,
            'sha256': hashlib.sha256((args.staged / asset['asset']).read_bytes()).hexdigest()}
    result['verified'] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
