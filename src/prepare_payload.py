"""Prepare an allowlisted offline payload. Never copies retail Data/ISO/exports."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def copy_tree(source,dest):
    for p in source.rglob('*'):
        if p.is_symlink():
            raise ValueError('Symlink in payload input: '+str(p))
        if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith(('.pyc','.pyo')):
            target=dest/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('source','runtime','ratchet-extractor','opengoal','python','redist','output'):
        p.add_argument('--'+field,type=Path,required=True)
    a=p.parse_args();src=a.source.resolve();out=a.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    code=Path(__file__).resolve().parent
    def cp(source,name):
        to=out/name;to.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,to)
    expected='d911b5f6597adb15eea65a35c6a67298a698efcacc4027c5927e1e7dfb0be531'
    if sha(a.runtime)!=expected:
        raise ValueError('This release is pinned to tested native alpha47')
    cp(a.runtime,'runtime/RatchetJakCrossover.exe')
    cp(src/'runtime/deps/sdl3-3.4.18/SDL3.dll','runtime/deps/sdl3-3.4.18/SDL3.dll')
    copy_tree(src/'crates/rc-engine/assets/shaders',out/'runtime/assets/shaders')
    cp(a.ratchet_extractor,'tools/ratchet_clank-extract.exe')
    cp(a.opengoal/'bin/extractor.exe','tools/extractor.exe')
    goal=a.opengoal/'jak1/data'
    copy_tree(goal/'decompiler/config',out/'opengoal/decompiler/config')
    for file in (goal/'goal_src/jak1/build').glob('all_objs*.json'):
        cp(file,'opengoal/goal_src/jak1/build/'+file.name)
    for file in (goal/'game/assets/jak1/patches').glob('*.xd3'):
        cp(file,'opengoal/game/assets/jak1/patches/'+file.name)
    # Licensed configuration only: no goal_src game instructions, game textures,
    # exported GLBs, ISO data, saves, custom test models or decompiler outputs.
    for file in a.python.iterdir():
        if file.is_file() and file.suffix.lower() in ('.exe','.dll','.txt'):
            cp(file,'python/'+file.name)
    copy_tree(a.python/'DLLs',out/'python/DLLs')
    for file in (a.python/'Lib').iterdir():
        if file.name in ('site-packages','test','tests','__pycache__','ensurepip','idlelib','tkinter'):
            continue
        if file.is_dir():
            copy_tree(file,out/'python/Lib'/file.name)
        elif file.suffix=='.py':
            cp(file,'python/Lib/'+file.name)
    copy_tree(a.python/'Lib/site-packages',out/'python/Lib/site-packages')
    for file in ('msvcp140.dll','vcruntime140.dll','vcruntime140_1.dll'):
        for folder in ('tools','runtime','python'):
            cp(a.redist/file,folder+'/'+file)
    for file in ('stage_characters.py','fix_eyes.py','validate_conversions.py','eye_data.py','import_jak.py'):
        cp(src/'tools/crossover'/file,'scripts/'+file)
    for file in ('generate.py','GameLauncher.cs.in','locales.json'):
        cp(code/file,'scripts/'+file)
    for file in ('RatchetJak.ico','RatchetJak-logo.png'):
        cp(src/'branding'/file,'branding/'+file)
    for file in ('parts.tsv','groups.tsv'):
        cp(src/'runtime/assets/local-jak/eco'/file,'config/'+file)
    config=json.loads((src/'runtime/assets/local-jak/eco/manifest.json').read_text())
    (out/'config/eco-manifest.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    cp(src/'LICENSE','licenses/ReRAC-ISC.txt')
    cp(a.python/'LICENSE.txt','licenses/Python.txt')
    notice=code/'THIRD_PARTY_NOTICES.md'
    if notice.exists():
        cp(notice,'licenses/THIRD_PARTY_NOTICES.md')
    # Legal notices are staged separately by the release maintainer.
    extra=code/'licenses'
    if extra.exists():
        copy_tree(extra,out/'licenses')
    files={str(f.relative_to(out)).replace('\\','/'):sha(f) for f in sorted(out.rglob('*')) if f.is_file()}
    forbidden=[f for f in files if f.lower().endswith(('.iso','.glb','.gltf','.rgba','.sbk','.vag','.dgo','.cgo'))]
    if forbidden:
        raise ValueError('Retail/converted data in payload: '+str(forbidden))
    manifest=dict(schema=1,beta='V19 alpha47 experimental',runtime_sha256=expected,files=files)
    (out/'payload-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    archive=out.parent/(out.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for file in sorted(out.rglob('*')):
            if file.is_file():
                z.write(file,str(file.relative_to(out)).replace('\\','/'))
    print(json.dumps(dict(files=len(files),archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive)),indent=2))


if __name__=='__main__':
    main()
