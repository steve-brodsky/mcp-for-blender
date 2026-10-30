"""Blender node equivalent of paint.compose(); no Pillow dependency in Blender."""
import bpy


def rgb(code):return tuple(int(code[i:i+2],16)/255 for i in (1,3,5))+(1,)


def find_image(node,seen=None):
    seen=seen or set()
    if node in seen:return None
    seen.add(node)
    if node.type=='TEX_IMAGE':return node
    for socket in node.inputs:
        for link in socket.links:
            found=find_image(link.from_node,seen)
            if found:return found
    return None


def make_paint_material(original,binding,manifest,root):
    if binding['action']=='preserve':return original
    material=original.copy();material.name='FleetPaint / '+original.name;material.use_fake_user=True
    material['pc_source_name']=original.name;material['pc_source_index']=binding['index']
    material['pc_action']=binding['action']
    nodes=material.node_tree.nodes;links=material.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    if binding['action']=='replace_base_color_factor':
        material['pc_role']=binding['role'];material['pc_alpha']=binding['original_base_color_factor'][3]
        return material
    t=manifest['texture_sets'][binding['texture_set']]
    material['pc_texture_set']=binding['texture_set']
    target=next((find_image(link.from_node) for link in shader.inputs['Base Color'].links),None)
    assert target is not None,original.name
    source=bpy.data.images.load(str(root/'previews/inputs'/binding['texture_set']/'source.png'),check_existing=True)
    source.colorspace_settings.name='Non-Color';target.image=source
    mask=nodes.new('ShaderNodeTexImage')
    mask.image=bpy.data.images.load(str(root/'previews/inputs'/binding['texture_set']/'mask.png'),check_existing=True)
    mask.image.colorspace_settings.name='Non-Color'
    mask.interpolation=target.interpolation
    for link in list(target.inputs['Vector'].links):links.new(link.from_socket,mask.inputs['Vector'])
    separate=nodes.new('ShaderNodeSeparateColor');links.new(mask.outputs['Color'],separate.inputs[0])
    hc=nodes.new('ShaderNodeRGB');hc.name='PC Hull sRGB'
    dc=nodes.new('ShaderNodeRGB');dc.name='PC Detail sRGB'
    def scalar(operation,a,b=None):
        node=nodes.new('ShaderNodeMath');node.operation=operation
        for index,value in enumerate([a,b]):
            if value is None:continue
            if isinstance(value,(int,float)):node.inputs[index].default_value=value
            else:links.new(value,node.inputs[index])
        return node.outputs[0]
    def vector(operation,a,b=None):
        node=nodes.new('ShaderNodeVectorMath');node.operation=operation
        for index,value in enumerate([a,b]):
            if value is None:continue
            if isinstance(value,tuple):node.inputs[index].default_value=value
            else:links.new(value,node.inputs[index])
        return node.outputs['Value'] if operation=='DOT_PRODUCT' else node.outputs['Vector']
    lum=vector('DOT_PRODUCT',target.outputs['Color'],(.2126,.7152,.0722))
    def tint(color,weight,reference):
        ratio=scalar('DIVIDE',lum,reference)
        scaled=vector('MULTIPLY',color,ratio)
        clipped=vector('MINIMUM',scaled,(1,1,1))
        return vector('MULTIPLY',clipped,weight)
    hull=tint(hc.outputs[0],separate.outputs[0],t['normalization']['hull'])
    detail=tint(dc.outputs[0],separate.outputs[1],t['normalization']['detail'])
    remaining=scalar('SUBTRACT',1,scalar('ADD',separate.outputs[0],separate.outputs[1]))
    untouched=vector('MULTIPLY',target.outputs['Color'],remaining)
    srgb=vector('ADD',vector('ADD',untouched,hull),detail)
    # Convert the resulting numeric sRGB into the linear input expected by Principled BSDF.
    channels=nodes.new('ShaderNodeSeparateColor');links.new(srgb,channels.inputs[0])
    combine=nodes.new('ShaderNodeCombineColor')
    for channel in range(3):
        value=channels.outputs[channel]
        low=scalar('DIVIDE',value,12.92)
        high=scalar('POWER',scalar('DIVIDE',scalar('ADD',value,.055),1.055),2.4)
        use_low=scalar('LESS_THAN',value,.04045)
        result=scalar('ADD',scalar('MULTIPLY',use_low,low),scalar('MULTIPLY',scalar('SUBTRACT',1,use_low),high))
        links.new(result,combine.inputs[channel])
    links.new(combine.outputs[0],shader.inputs['Base Color'])
    return material


def set_pair(material,hull,detail,manifest):
    if material.get('pc_action')=='replace_base_color_texture':
        material.node_tree.nodes['PC Hull sRGB'].outputs[0].default_value=rgb(manifest['hull_colors'][hull]['srgb'])
        material.node_tree.nodes['PC Detail sRGB'].outputs[0].default_value=rgb(manifest['detail_colors'][detail]['srgb'])
    elif material.get('pc_action')=='replace_base_color_factor':
        role=material['pc_role'];family='hull_colors' if role=='hull' else 'detail_colors'
        color=rgb(manifest[family][hull if role=='hull' else detail]['srgb'])
        linear=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in color[:3])+(material['pc_alpha'],)
        shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value=linear
