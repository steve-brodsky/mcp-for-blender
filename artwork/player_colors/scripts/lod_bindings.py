"""Resolve geometry-only LOD surfaces using the production material inheritance rule."""
import json
from inventory import ROOT, read_glb


def primitive_bindings(source,lod,material_bindings):
    by_material={b['lod_material_index']:b['source_material_index'] for b in material_bindings}
    used={p.get('material',0) for mesh in source.get('meshes',[]) for p in mesh['primitives']}
    bindings=[]
    for mi,mesh in enumerate(lod.get('meshes',[])):
        for pi,p in enumerate(mesh['primitives']):
            if 'material' in p:
                source_index=by_material[p['material']]
            elif len(used)==1:
                source_index=next(iter(used))
            else:
                # Interceptor LODs omit materials but retain the four surfaces in order;
                # scripts/ships/interceptor.gd assigns LOD0's material by surface index.
                assert len(source['meshes'])==len(lod['meshes'])
                assert len(source['meshes'][mi]['primitives'])==len(mesh['primitives'])
                source_index=source['meshes'][mi]['primitives'][pi].get('material',0)
            bindings.append({'lod_mesh_index':mi,'lod_primitive_index':pi,'source_material_index':source_index})
    return bindings


def main():
    path=ROOT/'manifest.json';manifest=json.loads(path.read_text())
    count=0
    for asset in manifest['assets']:
        source,_=read_glb(asset['source'])
        for lod in asset['lods']:
            doc,_=read_glb(lod['path'])
            lod['primitive_bindings']=primitive_bindings(source,doc,lod['material_bindings'])
            lod['usage']='Assign the matching LOD0 variant material to each listed mesh surface, including geometry-only LODs with no embedded materials.'
            count+=1
    path.write_text(json.dumps(manifest,indent=2))
    print('LOD_BINDINGS_COMPLETE',count)


if __name__=='__main__':main()
