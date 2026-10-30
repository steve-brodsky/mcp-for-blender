"""Make compact authoring previews; full-resolution source and masks remain unchanged."""
import json
import numpy as np
from PIL import Image
from inventory import ROOT

manifest=json.loads((ROOT/'manifest.json').read_text())
assert manifest['version']==2
for key,t in manifest['texture_sets'].items():
    folder=ROOT/'previews/inputs'/key;folder.mkdir(parents=True,exist_ok=True)
    for output,source in [('source.png',t['original']),('mask.png',t['packed_mask'])]:
        image=Image.open(ROOT/source)
        image.thumbnail((2048,2048),Image.Resampling.LANCZOS)
        if output=='mask.png':
            values=np.array(image)
            values[:,:,1]=np.minimum(values[:,:,1],255-values[:,:,0])
            image=Image.fromarray(values)
        image.save(folder/output,compress_level=4)
print('PREVIEW_INPUTS_READY',len(manifest['texture_sets']))
