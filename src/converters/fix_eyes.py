"""Restore neutral eyes omitted by OpenGOAL's GLB exporter, using the owner's textures.

OpenGOAL renders merc eyes to a separate texture at runtime. Its GLB uses 4x4
programmer_eye placeholders instead. This offline neutral-pose adapter replaces
only those materials; skeletal/mesh/animation BIN data remains byte identical.
It does not yet reproduce the original per-animation gaze/blink channels.
"""
import argparse
import base64
import hashlib
from io import BytesIO
import json
from pathlib import Path
import struct

from PIL import Image
import numpy as np
from eye_data import tracks


def neutral_eye(textures: Path, pose: dict, name: str, blink: float = 0.0) -> tuple[dict, dict]:
    iris_path = textures / 'eichar/bam-iris-16x16.png'
    pupil_path = textures / 'common/autoeye-pupil.png'
    lid_path = textures / ('sidekick-lod0/sk-eye-lid.png' if name == 'daxter' else 'common/autoeye-lid.png')
    iris = Image.open(iris_path).convert('RGBA')
    pupil = Image.open(pupil_path).convert('RGBA')
    lid = Image.open(lid_path).convert('RGBA')
    if iris.size != (16, 16) or pupil.size != iris.size:
        raise ValueError('Unexpected original eye texture dimensions')
    # Match OpenGOAL's 128x128 eye framebuffer and bilinear/clamp sampler.
    def draw(target, image, rect, blend=False):
        x0, y0, x1, y1 = rect
        if x1 <= x0 or y1 <= y0:
            return
        pixels = np.asarray(image, dtype=np.float64)
        size = target.shape[0]
        xx, yy = np.meshgrid((np.arange(size) + 0.5) * 32 / size,
                             (np.arange(size) + 0.5) * 32 / size)
        mask = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
        u = np.clip((xx - x0) / (x1 - x0) * image.width - 0.5, 0, image.width - 1)
        v = np.clip((yy - y0) / (y1 - y0) * image.height - 0.5, 0, image.height - 1)
        ux, vy = u.astype(int), v.astype(int)
        uf, vf = (u - ux)[..., None], (v - vy)[..., None]
        sample = ((pixels[vy, ux] * (1 - uf) + pixels[vy, np.minimum(ux + 1, image.width - 1)] * uf) * (1 - vf)
                  + (pixels[np.minimum(vy + 1, image.height - 1), ux] * (1 - uf)
                     + pixels[np.minimum(vy + 1, image.height - 1), np.minimum(ux + 1, image.width - 1)] * uf) * vf)
        if blend:
            alpha = np.minimum(1, sample[..., 3:4] / 128)
            sample[..., :3] = sample[..., :3] * alpha + target[..., :3] * (1 - alpha)
        target[mask] = sample[mask]

    images = {}
    for side, eye in pose.items():
        result = np.full((128, 128, 4), iris.getpixel((0, 0)), dtype=float)
        cx, cy = 16 + eye['x'] / 128 * 32, 16 + eye['y'] / 128 * 32
        for image, scale, blend in ((iris, eye['iris_scale'], False), (pupil, eye['pupil_scale'], True)):
            half = 16 * scale / 64
            draw(result, image, (cx - half, cy - half, cx + half, cy + half), blend)
        lid_position = eye['lid'] / 128
        if lid_position < 0:
            lid_position += 1
            lid_position += (1 - lid_position) * blink
        top = -32 + 32 * lid_position
        draw(result, lid, (0, top, 32, top + 32 * eye['lid_scale'] / 64))
        result[..., 3] = 255
        stream = BytesIO()
        Image.fromarray(np.clip(result, 0, 255).astype('uint8')).save(stream, format='PNG')
        images[side] = stream.getvalue()
    return images, {
        str(path.relative_to(textures)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (iris_path, pupil_path, lid_path)
    }


def fix(path: Path, png: dict) -> dict:
    raw = path.read_bytes()
    chunks, offset = [], 12
    while offset < len(raw):
        length, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        chunks.append((kind, raw[offset:offset + length]))
        offset += length
    doc = json.loads(chunks[0][1])
    binary = next(payload for kind, payload in chunks if kind == 0x004E4942)
    replacements = []
    for material in doc['materials']:
        if not material.get('name', '').startswith('programmer_eye_'):
            continue
        pbr = material['pbrMetallicRoughness']
        texture = doc['textures'][pbr['baseColorTexture']['index']]
        image = doc['images'][texture['source']]
        side = 'left' if '_left' in material['name'] else 'right'
        image['uri'] = 'data:image/png;base64,' + base64.b64encode(png[side]).decode('ascii')
        pbr.pop('metallicRoughnessTexture', None)
        pbr['metallicFactor'] = 0.0
        pbr['roughnessFactor'] = 0.6
        material.pop('extensions', None)
        material['alphaMode'] = 'OPAQUE'
        replacements.append(material['name'])
    if len(replacements) != 2:
        raise ValueError(f'{path.name}: expected two distinct eye materials')
    encoded = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode()
    encoded += b' ' * (-len(encoded) % 4)
    chunks[0] = (0x4E4F534A, encoded)
    body = b''.join(struct.pack('<II', len(payload), kind) + payload for kind, payload in chunks)
    path.write_bytes(struct.pack('<4sII', b'glTF', 2, len(body) + 12) + body)
    return {'materials': replacements, 'binary_sha256_unchanged': hashlib.sha256(binary).hexdigest(),
            'staged_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-root', type=Path, required=True)
    parser.add_argument('--assets', type=Path, required=True)
    args = parser.parse_args()
    workspace = args.export_root.resolve(strict=True)
    textures = workspace / 'decompiler_out/jak1/textures'
    assets = args.assets.resolve(strict=True)
    if workspace == assets or workspace in assets.parents or assets in workspace.parents:
        parser.error('Converted assets must be separate from exporter data')
    report = {'schema': 2, 'mode': 'original_stance_eye_pose_no_runtime_eye_track_yet', 'characters': {}}
    for name, prefix in (('jak', 'eichar'), ('daxter', 'sidekick')):
        dump = args.export_root / f'decompiler_out/jak1/{prefix}-ag.txt'
        eye_tracks = tracks(dump)
        pose = eye_tracks[f'{prefix}-stance-loop'][0]
        png, hashes = neutral_eye(textures, pose, name)
        eye_folder = assets / 'eyes'
        eye_folder.mkdir(exist_ok=True)
        # Chronological order of the original table's countdown (9 -> 0).
        blink_table = [0.0, 0.1, 0.333, 1.0, 1.0, 1.0, 1.0, 0.9, 0.667, 0.0]
        for frame, amount in enumerate(blink_table):
            images, _ = neutral_eye(textures, pose, name, amount)
            for side, image in images.items():
                (eye_folder / f'{name}-{side}-{frame}.png').write_bytes(image)
        report['characters'][name] = {**fix(assets / f'{name}.glb', png), 'pose': pose,
                                     'sources': hashes, 'eye_dump_sha256': hashlib.sha256(dump.read_bytes()).hexdigest(),
                                     'available_eye_tracks': len(eye_tracks), 'blink_table_60hz': blink_table}
    (assets / 'eyes.local.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
