"""Render each asset in an isolated Blender process; resume completed previews."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import hashlib
from inventory import ROOT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--blender',default=r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
    parser.add_argument('--cycles',action='store_true')
    parser.add_argument('--force',action='store_true')
    args=parser.parse_args()
    inventory=json.loads((ROOT/'inventory.json').read_text())
    logdir=ROOT/'previews/logs';logdir.mkdir(parents=True,exist_ok=True)
    results=[]
    for item in inventory:
        asset=item['asset']
        report=ROOT/'previews/raw'/asset/'render_report.json'
        expected=hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest()
        if report.exists() and json.loads(report.read_text()).get('version')==2 and json.loads(report.read_text()).get('manifest_sha256')==expected and not args.force:
            print('SKIP',asset,flush=True);continue
        wait_start=time.monotonic()
        while True:
            try:
                manifest=json.loads((ROOT/'manifest.json').read_text())
                if manifest.get('version')==2 and any(a['id']==asset for a in manifest['assets']):break
            except (json.JSONDecodeError,FileNotFoundError):pass
            if time.monotonic()-wait_start>900:
                raise TimeoutError('Texture generation did not complete '+asset)
            time.sleep(2)
        print('RENDER',asset,flush=True)
        with (logdir/(asset+'.log')).open('w') as log:
            run=subprocess.run([args.blender,'--factory-startup','-b','--python',str(ROOT/'scripts/render_asset.py'),
                '--',asset,'--cycles' if args.cycles else '--eevee'],stdout=log,stderr=subprocess.STDOUT,timeout=300)
        ok=run.returncode==0 and report.exists()
        results.append({'asset':asset,'ok':ok,'exit_code':run.returncode})
        (ROOT/'previews/render_batch.json').write_text(json.dumps(results,indent=2))
        if not ok:raise RuntimeError('Preview failed '+asset+'; see '+str(logdir/(asset+'.log')))
    print('ALL_PREVIEWS_COMPLETE',len(inventory),flush=True)


if __name__=='__main__':main()
