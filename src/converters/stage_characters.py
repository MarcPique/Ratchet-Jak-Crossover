"""Stage validated Jak and Daxter GLBs from the private OpenGOAL export into local runtime assets."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
from import_jak import audit_glb

REQUIRED = {"idle": "stance-loop", "walk": "walk", "run": "run", "jump": "jump",
            "fall": "jump-loop", "land": "jump-land", "punch": "attack-punch"}


def prepare_for_bevy(source: Path, destination: Path) -> dict:
    """Add required POSITION accessor bounds; preserve every source binary buffer byte exactly."""
    data = source.read_bytes()
    chunks, offset = [], 12
    while offset < len(data):
        length, kind = struct.unpack_from("<II", data, offset)
        offset += 8
        payload = data[offset:offset+length]
        if len(payload) != length:
            raise ValueError("Truncated GLB chunk")
        chunks.append((kind, payload))
        offset += length
    doc = json.loads(chunks[0][1])
    binary = next(payload for kind, payload in chunks if kind == 0x004E4942)
    positions = {primitive["attributes"]["POSITION"] for mesh in doc["meshes"]
                 for primitive in mesh["primitives"]}
    bounds = {}
    for index in positions:
        accessor = doc["accessors"][index]
        if accessor["componentType"] != 5126 or accessor["type"] != "VEC3" or "sparse" in accessor:
            raise ValueError("Unsupported POSITION encoding; expected dense float32 VEC3")
        view = doc["bufferViews"][accessor["bufferView"]]
        if view.get("buffer", 0) != 0:
            raise ValueError("POSITION must use the embedded binary buffer")
        stride = view.get("byteStride", 12)
        start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        count = accessor["count"]
        end = start + (count - 1) * stride + 12
        if count < 1 or stride < 12 or end > len(binary) or end > view.get("byteOffset", 0) + view["byteLength"]:
            raise ValueError("POSITION accessor runs outside its binary buffer view")
        lo, hi = [math.inf]*3, [-math.inf]*3
        for vertex in range(count):
            values = struct.unpack_from("<fff", binary, start + vertex*stride)
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Non-finite vertex in source GLB")
            lo = [min(a, b) for a, b in zip(lo, values)]
            hi = [max(a, b) for a, b in zip(hi, values)]
        accessor["min"], accessor["max"] = lo, hi
        bounds[str(index)] = {"min": lo, "max": hi}
    encoded = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode("utf-8")
    encoded += b' ' * (-len(encoded) % 4)
    chunks[0] = (0x4E4F534A, encoded)
    body = b''.join(struct.pack("<II", len(payload), kind) + payload for kind, payload in chunks)
    destination.write_bytes(struct.pack("<4sII", b'glTF', 2, len(body)+12) + body)
    return {"position_bounds": bounds, "binary_sha256_unchanged": hashlib.sha256(binary).hexdigest(),
            "staged_sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = args.export_root.resolve(strict=True)
    output = args.out.resolve()
    if output == source or output in source.parents or source in output.parents:
        parser.error("Stage into a separate directory, outside the private exporter workspace")
    result = {"schema": 1, "status": "import_candidates_not_gameplay", "characters": {}}
    candidates = []
    for name, prefix in (("jak", "eichar"), ("daxter", "sidekick")):
        file = source / f"decompiler_out/jak1/levels/common/{prefix}-lod0.glb"
        audit = audit_glb(file)
        if not audit["skinned_animated_candidate"]:
            raise ValueError(f"{name}: missing skeleton or animation")
        clips = audit["animations"]
        mapping = {action: clips.index(f"{prefix}-{suffix}") for action, suffix in REQUIRED.items()}
        result["characters"][name] = {**audit, "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                                      "asset": f"{name}.glb", "clip_indices": mapping}
        candidates.append((file, name))
    output.mkdir(parents=True, exist_ok=True)
    for file, name in candidates:
        result["characters"][name]["conversion"] = prepare_for_bevy(file, output / f"{name}.glb")
        audit_glb(output / f"{name}.glb")
    (output / "characters.local.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({name: {"joints": v["joints"], "clips": len(v["animations"]),
                            "clip_indices": v["clip_indices"]} for name, v in result["characters"].items()}, indent=2))


if __name__ == "__main__":
    main()
