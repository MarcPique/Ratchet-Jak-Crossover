"""Build the pinned experimental beta from the owner's two discs, offline.

This worker is bundled with the branded generator. It never downloads games,
modifies inputs, compiles the engine or writes into an existing installation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


LANGUAGE='en'
CATALOG=json.loads((Path(__file__).parent/'locales.json').read_text(encoding='utf-8'))
def tr(label):
    return CATALOG['setup'].get(label,{}).get(LANGUAGE,label)

def initial_settings(game,language):
    slot=CATALOG['languages'][language]['slot']
    profile=game/'UserData';profile.mkdir()
    (profile/'settings.toml').write_text(
        '# Ratchet&Jak: initial setup preferences; language can be changed in the game.\n'
        +f'language = {slot}\nfullscreen = 1\nwindow_mode = borderless\nresolution = window\nrender_scale = 100\naspect = monitor\n',encoding='utf-8')
    return slot

def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def run(label,argv,cwd,env,log):
    print('FASE: '+tr(label),flush=True)
    log.write('\nFASE: '+label+'\n'+subprocess.list2cmdline([str(x) for x in argv])+'\n');log.flush()
    proc=subprocess.Popen([str(x) for x in argv],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                          encoding='utf-8',errors='replace',creationflags=0x08000000)
    for line in proc.stdout:
        log.write(line);log.flush()
        if line.strip():
            print(line.rstrip(),flush=True)
    if proc.wait()!=0:
        raise RuntimeError(label+': código de salida '+str(proc.returncode))


def verify_payload(payload):
    manifest=json.loads((payload/'payload-manifest.json').read_text(encoding='utf-8'))
    for name,expected in manifest['files'].items():
        file=(payload/name).resolve()
        if payload not in file.parents or digest(file)!=expected:
            raise RuntimeError('Payload alterado: '+name)
    return manifest


def stage_eco(payload,goal,out):
    from PIL import Image
    out.mkdir(parents=True)
    config=payload/'config'
    for name in ('parts.tsv','groups.tsv'):
        shutil.copyfile(config/name,out/name)
    manifest=json.loads((config/'eco-manifest.json').read_text(encoding='utf-8'))
    textures=goal/'decompiler_out/jak1/textures'
    for row in manifest['textures']:
        image=Image.open(textures/'effects'/(row['name']+'.png')).convert('RGBA')
        if image.size!=(row['width'],row['height']):
            raise RuntimeError('Dimensiones Eco inesperadas: '+row['name'])
        raw=image.tobytes()
        if hashlib.sha256(raw).hexdigest()!=row['rgba_sha256']:
            raise RuntimeError('Textura Eco inesperada: '+row['name'])
        (out/row['file']).write_bytes(raw)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


def asset_references(root):
    count=0
    for gltf in root.rglob('*.gltf'):
        data=json.loads(gltf.read_text(encoding='utf-8'))
        for row in data.get('buffers',[])+data.get('images',[]):
            uri=row.get('uri','')
            if uri and not uri.startswith('data:'):
                file=(gltf.parent/uri).resolve()
                if root not in file.parents or not file.is_file():
                    raise RuntimeError('Referencia GLTF ausente o inválida: '+str(gltf))
                count+=1
    return count


def build(request):
    global LANGUAGE
    LANGUAGE=request.get("Language") or "en"
    if LANGUAGE not in CATALOG["languages"]: raise ValueError("Unsupported language")
    started=time.time()
    dest=Path(request['Destination']).resolve(strict=True)
    payload=(dest/'.builder/payload').resolve(strict=True)
    work=dest/'.builder/work';work.mkdir()
    temporary=work/'temp';temporary.mkdir()
    game=dest/'game.partial'
    final=dest/'game'
    if game.exists() or final.exists():
        raise RuntimeError('Usa un destino nuevo; no se sustituyen instalaciones.')
    phase='verificar paquete'
    result=dict(success=False,status='failed',phase=phase)
    with (dest/'build.log').open('w',encoding='utf-8') as log:
        try:
            manifest=verify_payload(payload)
            game.mkdir()
            shutil.copytree(payload/'runtime',game,dirs_exist_ok=True)
            env={k:v for k,v in os.environ.items() if not k.startswith(('RC_','RJC_'))}
            env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None)
            env.update(TEMP=str(temporary),TMP=str(temporary),TMPDIR=str(temporary),PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
            python=payload/'python/python.exe'
            extractor=payload/'tools/ratchet_clank-extract.exe'
            opengoal=payload/'tools/extractor.exe'
            goal=work/'opengoal'
            shutil.copytree(payload/'opengoal',goal)
            for folder in ('game/assets/jak1/patches','custom_assets','iso_data'):
                (goal/folder).mkdir(parents=True,exist_ok=True)
            data=game/'Data'
            phase='Identificar Ratchet SCUS_971.99'
            run(phase,[extractor,'identify','--iso',request['RatchetIso'],'--json'],work,env,log)
            phase='Extraer Ratchet desde tu ISO'
            run(phase,[extractor,'extract','--iso',request['RatchetIso'],'--out',data,'--json'],work,env,log)
            phase='Verificar Ratchet'
            run(phase,[extractor,'verify','--out',data,'--json'],work,env,log)
            phase='Extraer y validar Jak SCUS_971.24'
            full=json.dumps(dict(rip_levels=True,decompile_code=False,dump_objs=False,rip_collision=False,save_texture_pngs=True))
            run(phase,[opengoal,request['JakIso'],'--proj-path',goal,'--extract-path',goal/'iso_data','-g','jak1','-e','-v','-d',
                       '--decomp-config-override',full,'--disable-ansi'],goal,env,log)
            phase='Restaurar datos de ojos'
            eye=json.dumps(dict(allowed_objects=['eichar-ag','sidekick-ag'],rip_levels=False,levels_extract=False,decompile_code=False,
                                dump_objs=False,rip_collision=False,save_texture_pngs=False,hexdump_data=True,process_part_group_table=False,write_scripts=False))
            run(phase,[opengoal,goal/'iso_data/jak1','--proj-path',goal,'-g','jak1','-d','-f','--decomp-config-override',eye,'--disable-ansi'],goal,env,log)
            scripts=payload/'scripts';jak=game/'assets/local-jak'
            phase='Preparar Jak y Daxter animados'
            run(phase,[python,'-B',scripts/'stage_characters.py','--export-root',goal,'--out',jak],work,env,log)
            run(phase,[python,'-B',scripts/'fix_eyes.py','--export-root',goal,'--assets',jak],work,env,log)
            run('Verificar esqueletos y animaciones',[python,'-B',scripts/'validate_conversions.py','--staged',jak,'--report',dest/'conversion-report.local.json'],work,env,log)
            phase='Preparar escenario, Clank y menú'
            for level in ('00','10'):
                run(phase,[extractor,'export','--out',data,'--to',game/'assets/local-ratchet','--what','models,levels,textures','--level',level,'--json'],work,env,log)
            phase='Preparar efectos Eco originales'
            stage_eco(payload,goal,jak/'eco')
            references=asset_references((game/'assets').resolve())
            language_slot=initial_settings(game,LANGUAGE)
            env['RJC_USER_DIR']=str(game/'UserData')
            env['RC_SETTINGS_FILE']=str(game/'UserData/settings.toml')
            run('Comprobar motor nativo',[game/'RatchetJakCrossover.exe','--version-json'],game,env,log)
            phase='Finalizar instalación'
            stamp=dict(schema=2,beta=manifest['beta'],installer_language=LANGUAGE,language_slot=language_slot,fullscreen=True,resolution='monitor-native',runtime_sha256=digest(game/'RatchetJakCrossover.exe'),
                       ratchet_iso_sha256=digest(request['RatchetIso']),jak_iso_sha256=digest(request['JakIso']),
                       asset_references=references,status='generated_not_gameplay_verified',elapsed_seconds=round(time.time()-started,1))
            (game/'build-manifest.local.json').write_text(json.dumps(stamp,indent=2),encoding='utf-8')
            shutil.copytree(payload/'licenses',game/'licenses',dirs_exist_ok=True)
            game.rename(final)
            phase='Crear EXE en el escritorio'
            desktop=Path(request['DesktopDirectory']).resolve(strict=True)
            target=desktop/'Ratchet&Jak.exe'
            suffix=2
            while target.exists():
                target=desktop/('Ratchet&Jak ('+str(suffix)+').exe');suffix+=1
            template=(payload/'scripts/GameLauncher.cs.in').read_text(encoding='utf-8')
            source=work/'GameLauncher.cs'
            source.write_text(template.replace('__GAME_ROOT__',str(final).replace('"','""')),encoding='utf-8')
            launcher=work/'RatchetJakLauncher.exe'
            framework=Path(os.environ['WINDIR'])/'Microsoft.NET/Framework64/v4.0.30319'
            run(phase,[framework/'csc.exe','/nologo','/target:winexe','/platform:x64','/optimize+','/codepage:65001',
                       '/reference:System.Windows.Forms.dll','/reference:System.Core.dll',
                       '/win32icon:'+str(payload/'branding/RatchetJak.ico'),'/out:'+str(launcher),source],work,env,log)
            run('Verificar acceso de escritorio',[launcher,'--self-test'],final,env,log)
            shutil.copyfile(launcher,target)
            result=dict(success=True,status='generated_not_gameplay_verified',game=str(final),desktop_exe=str(target),manifest=stamp)
            print('LISTO: '+str(target),flush=True)
        except Exception as error:
            result.update(phase=phase,error=str(error))
            raise
        finally:
            (dest/'build-result.local.json').write_text(json.dumps(result,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request',type=Path,required=True)
    args=p.parse_args()
    build(json.loads(args.request.read_text(encoding='utf-8-sig')))
