"""Complete final preview checks without repeating pixel math for unchanged PNGs."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from inventory import ROOT
from paint import recipe_fingerprint


def main():
    m=json.loads((ROOT/'manifest.json').read_text());r=json.loads((ROOT/'validation.json').read_text())
    assert r['passed'] and r['version']==2 and r['recipe_sha256']==recipe_fingerprint(m)
    for path,digest in m['source_files'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
    for key,t in m['texture_sets'].items():
        for name,path in t['variants'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==r['texture_sets'][key]['variants'][name]['sha256']
    pairs=m['mix_and_match']['combinations'];renders=0
    for asset in m['assets']:
        key=asset['id'];pr=json.loads((ROOT/'previews/raw'/key/'render_report.json').read_text())
        assert pr['version']==2 and pr['combination_count']==len(pairs)
        for path in pr['renders']:assert Image.open(ROOT/path).size==(480,360);renders+=1
        for pair in pairs:assert (ROOT/'previews/combinations'/key/(pair['id']+'.png')).exists()
        for path in pr['preset_aliases'].values():assert (ROOT/path).exists()
        for folder in ['ships','inspection','matrices']:assert (ROOT/'previews'/folder/(key+'.png')).exists()
        assert (ROOT/pr['preview_blend']).exists()
    br=json.loads((ROOT/'previews/blender_validation.json').read_text());assert {b['asset'] for b in br}=={a['id'] for a in m['assets']}
    assert all(b['pair_switches_checked']==len(pairs) and b['source_switch_checked'] and b['saved_file_reopened'] and b['relative_texture_links_valid'] for b in br)
    lr=json.loads((ROOT/'previews/lods/report.json').read_text());assert {x['asset'] for x in lr}=={a['id'] for a in m['assets'] if a['lods']}
    for entry in lr:assert (ROOT/entry['image']).exists()
    for name in ['source']+list(m['palettes']):assert (ROOT/'previews/fleets'/(name+'.png')).exists()
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert '<article data-asset="carrier' not in html and 'id="hull"' in html and 'id="detail"' in html
    r['checks'].update(preview_required=True,rendered_views=renders,combination_previews=len(pairs)*len(m['assets']),
        blender_pair_switch_checks=sum(b['pair_switches_checked'] for b in br),rendered_lod_comparisons=len(lr),variant_hashes_rechecked=True)
    browser_path=ROOT/'browser_validation.json'
    if browser_path.exists():
        browser=json.loads(browser_path.read_text())
        assert browser['passed'] and browser['independent_pairs_checked']==len(pairs) and browser['asset_cards']==len(m['assets'])
        r['checks']['browser_pairs_checked']=browser['independent_pairs_checked']
    gpu_log=ROOT/'godot_gpu_test.log'
    if gpu_log.exists() and 'GODOT_BAKER_COMPLETE '+str(len(pairs))+' pairs' in gpu_log.read_text():
        r['checks']['godot_gpu_pairs_checked']=len(pairs)
    (ROOT/'validation.json').write_text(json.dumps(r,indent=2));print('DELIVERY_VALIDATED',json.dumps(r['checks']))


if __name__=='__main__':main()
