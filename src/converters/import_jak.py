"""Export the owner's Jak resources inside a private, isolated extraction workspace.

OpenGOAL is an offline converter only. This never starts gk.exe or modifies its installation.
The exporter version decides whether skins/animations are available; audit the resulting GLBs.
"""
import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess


def audit_glb(path: Path) -> dict:
    with path.open("rb") as f:
        magic, version, total = struct.unpack("<4sII", f.read(12))
        if magic != b"glTF" or version != 2 or total != path.stat().st_size:
            raise ValueError(f"Invalid GLB header: {path}")
        size, chunk = struct.unpack("<II", f.read(8))
        if chunk != 0x4E4F534A or size > total - 20:
            raise ValueError(f"Missing GLB JSON chunk: {path}")
        doc = json.loads(f.read(size).decode("utf-8"))
    nodes = doc.get("nodes", [])
    skins = doc.get("skins", [])
    animations = doc.get("animations", [])
    for skin in skins:
        if not skin.get("joints") or any(j < 0 or j >= len(nodes) for j in skin["joints"]):
            raise ValueError(f"Invalid skin joint references: {path}")
    for anim in animations:
        for channel in anim.get("channels", []):
            target = channel.get("target", {}).get("node", -1)
            if target < 0 or target >= len(nodes):
                raise ValueError(f"Invalid animation target: {path}")
    return {"file": str(path), "meshes": len(doc.get("meshes", [])),
            "skins": len(skins), "joints": sum(len(s["joints"]) for s in skins),
            "animations": [a.get("name", f"animation_{i}") for i, a in enumerate(animations)],
            "skinned_animated_candidate": bool(skins and animations)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--jak-active", type=Path)
    p.add_argument("--workspace", type=Path)
    p.add_argument("--audit", type=Path, help="Audit an existing GLB file or directory without conversion")
    args = p.parse_args()
    if args.audit:
        files = [args.audit] if args.audit.is_file() else list(args.audit.rglob("*.glb"))
        print(json.dumps([audit_glb(f) for f in files], indent=2))
        return
    if not args.jak_active or not args.workspace:
        p.error("Supply --jak-active and --workspace, or --audit")
    install = args.jak_active.resolve(strict=True)
    workspace = args.workspace.resolve()
    if workspace == install or install in workspace.parents or workspace in install.parents:
        p.error("Extraction workspace must be separate from the original installation")
    if workspace.exists() and any(workspace.iterdir()):
        p.error("Use a new or empty private extraction workspace")
    source = install / "jak1/data"
    workspace.mkdir(parents=True, exist_ok=True)
    # Copy supporting configs from the SAME installed version as extractor.exe.
    # The ISO folder is opened read-only via -f; no -e/-c/-p operations are requested.
    for name in ("decompiler", "goal_src", "game", "custom_assets"):
        if (source / name).exists():
            shutil.copytree(source / name, workspace / name)
    override = json.dumps({"rip_levels": True, "decompile_code": False,
                           "dump_objs": False, "rip_collision": False, "save_texture_pngs": True})
    command = [str(install / "bin/extractor.exe"), str(source / "iso_data/jak1"),
               "--proj-path", str(workspace), "-g", "jak1", "-d", "-f",
               "--decomp-config-override", override, "--disable-ansi"]
    (workspace / "command.json").write_text(json.dumps(command, indent=2), encoding="utf-8")
    with (workspace / "export.log").open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=workspace, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode == 0:
        # GLB omits merc eye textures/tracks. Export labelled data separately;
        # do not enable object filtering during the full level extraction.
        eye_command = command.copy()
        eye_command[eye_command.index('--decomp-config-override') + 1] = json.dumps({
            'allowed_objects': ['eichar-ag', 'sidekick-ag'], 'rip_levels': False,
            'levels_extract': False, 'decompile_code': False, 'dump_objs': False,
            'rip_collision': False, 'save_texture_pngs': False, 'hexdump_data': True,
            'process_part_group_table': False, 'write_scripts': False})
        (workspace / 'command-eye-data.json').write_text(json.dumps(eye_command, indent=2), encoding='utf-8')
        with (workspace / 'export-eye-data.log').open('w', encoding='utf-8') as log:
            result = subprocess.run(eye_command, cwd=workspace, stdout=log, stderr=subprocess.STDOUT)
    files = list((workspace / "decompiler_out").rglob("*.glb"))
    audits = [audit_glb(f) for f in files]
    (workspace / "glb-audit.json").write_text(json.dumps(audits, indent=2), encoding="utf-8")
    print(json.dumps({"exit_code": result.returncode, "exported_glbs": len(files),
                      "animated_candidates": sum(a["skinned_animated_candidate"] for a in audits),
                      "log": str(workspace / "export.log")}, indent=2))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
