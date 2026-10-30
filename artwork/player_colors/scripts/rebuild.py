"""Repeatable full pipeline; source artwork is always read-only."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from inventory import ROOT,WORKSPACE


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--blender',default=r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
    parser.add_argument('--godot',help='Optional Godot executable for the actual GPU parity fixture.')
    parser.add_argument('--force-previews',action='store_true')
    args=parser.parse_args()
    def run(command):
        print('RUN',command,flush=True);subprocess.run([str(x) for x in command],cwd=WORKSPACE,check=True)
    def python(script,*extra):run([sys.executable,ROOT/'scripts'/script,*extra])
    python('generate.py');python('inventory.py');python('prepare_preview_inputs.py')
    python('render_all.py','--blender',args.blender,*(['--force'] if args.force_previews else []))
    for script in ['finalize_previews.py','render_lods.py']:
        run([args.blender,'--factory-startup','-b','--python',ROOT/'scripts'/script])
    python('make_sheets.py');python('bake_pair.py','--hull','white','--detail','black')
    if args.godot:
        env=os.environ.copy();env['APPDATA']=str(ROOT/'integration/.userdata')
        Path(env['APPDATA']).mkdir(exist_ok=True)
        command=[args.godot,'--path',str(ROOT/'integration'),'--script','res://test_project/test_baker.gd',
            '--rendering-method','gl_compatibility','--audio-driver','Dummy','--resolution','8x8',
            '--position','-32000,-32000','--quit-after','600','--log-file',str(ROOT/'godot_gpu_test.log')]
        options={}
        if os.name=='nt':
            startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
            options['startupinfo']=startup
        subprocess.run(command,env=env,check=True,timeout=120,**options)
        assert 'GODOT_BAKER_COMPLETE' in (ROOT/'godot_gpu_test.log').read_text()
    python('validate.py','--require-previews')
    run([sys.executable,'-m','unittest','discover','-s',ROOT/'tests','-v'])
    print('REBUILD_COMPLETE',flush=True)


if __name__=='__main__':main()
