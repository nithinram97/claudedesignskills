"""
Clairvoyant — "Orb" mascot animation for Blender
=================================================

Run:  Blender > Scripting tab > Open this file > Run Script
      (or headless: blender -b -P clairvoyant_orb_blender.py -a)

Tested on Blender 5.2 LTS; written to also work on Blender 4.2+ (EEVEE).
The script wipes the current scene and builds everything from scratch.

14-second story (420 frames @ 30 fps):
  001-055  Orb drops from the sky, squash-and-stretch landing, dust shockwave
  055-115  Looks left, looks right, blinks
  115-170  Glowing KPI pillars rise around him, he hops with excitement
  170-215  An amber trend line draws across the pillar tops; he looks up at it
  215-285  The brand's open "C" halo draws itself around him
  285-340  TRANSFORMATION: Orb closes his eyes and glows; the halo tightens into
           the logo's C ring, his legs fold into the V stand, his feet merge
           into the groundline, his antenna spark flies out to become the
           breakout point, and his body dissolves into light
  340-365  The KPI bars rise inside the C and the amber breakout line fires
  365-420  The lockup lifts, the CLAIRVOYANT wordmark (official Michroma
           outlines, embedded below) appears letter by letter: end card

The end card matches the official stacked lockup (dark variant: white + amber),
built from the same geometry as the brand SVGs.

Effects: reflective data-grid floor, volumetric fog with light shafts,
floating motes, emissive pillars, bloom/glow in the compositor,
depth of field, motion blur and an orbiting camera.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

# --------------------------------------------------------------------------
# Settings you may want to change
# --------------------------------------------------------------------------
FPS = 30
FRAME_END = 420
RES_X, RES_Y = 1920, 1080
RENDER_SAMPLES = 64
OUTPUT_PATH = "//clairvoyant_orb_"   # relative to the .blend file location

# Brand colours
SLATE = "#2F4356"
SLATE_DEEP = "#16202B"
AMBER = "#F5B942"
AMBER_DEEP = "#E8A33D"
ICE = "#CFE3F5"
BLUSH = "#F28B82"
LOGO_WHITE = "#FFFFFF"

# Official logo geometry lives in SVG units (see clairvoyant-mark.svg).
# SVG -> world: ring radius 56 SVG units = 1 metre = Orb's body radius.
S_LOGO = 1.0 / 56.0
LOGO_Z0 = 1.91          # world height of the ring centre while it sits on the floor
LOGO_LIFT = 1.2         # how far the finished lockup rises to make room for the wordmark


def LX(x):
    return (x - 190) * S_LOGO


def LZ(y):
    return LOGO_Z0 - (y - 115) * S_LOGO


# Michroma (SIL Open Font License) outlines for the letters of CLAIRVOYANT,
# as cubic Bezier contours in font units: {letter: (advance, [[(anchor, handle_in, handle_out), ...], ...])}
MICHROMA_UPM = 2048
MICHROMA_CAP = 1536
MICHROMA = {'A':(2176,[[((64,0),(139,0),(363,512)),((960,1536),(661,1024),(1045,1536)),((1216,1536),(1131,1536),(1515,1024)),((2112,0),(1813,512),(2037,0)),((1888,0),(1963,0),(1824,117)),((1696,352),(1760,235),(1291,352)),((480,352),(885,352),(416,235)),((288,0),(352,117),(213,0))],[((576,512),(747,811),(917,512)),((1600,512),(1259,512),(1429,811)),((1088,1408),(1259,1109),(917,1109))]]),'C':(2145,[[((128,748),(128,583),(128,761)),((128,788),(128,775),(128,924)),((148,1130),(135,1038),(161,1223)),((217,1356),(184,1298),(250,1414)),((350,1489),(294,1458),(407,1520)),((563,1552),(478,1540),(648,1562)),((871,1568),(751,1568),(1005,1568)),((1274,1568),(1140,1568),(1411,1568)),((1622,1548),(1527,1562),(1716,1536)),((1850,1472),(1792,1510),(1907,1433)),((1975,1302),(1949,1377),(2001,1228)),((2014,1007),(2014,1130),(1950,1007)),((1822,1007),(1886,1007),(1822,1104)),((1796,1232),(1813,1179),(1779,1286)),((1708,1349),(1750,1325),(1668,1373)),((1541,1394),(1612,1388),(1470,1399)),((1274,1402),(1381,1402),(1140,1402)),((871,1402),(1005,1402),(776,1402)),((630,1394),(695,1399),(565,1388)),((470,1354),(512,1375),(430,1334)),((376,1258),(398,1302),(355,1214)),((332,1078),(340,1154),(324,1002)),((320,788),(320,905),(320,775)),((320,748),(320,761),(320,635)),((332,466),(324,541),(340,391)),((376,287),(355,332),(398,242)),((470,187),(430,209),(512,165)),((630,144),(565,151),(695,137)),((871,134),(776,134),(1005,134)),((1274,134),(1140,134),(1381,134)),((1541,141),(1470,136),(1612,146)),((1708,182),(1668,159),(1750,205)),((1796,296),(1779,242),(1813,348)),((1822,519),(1822,423),(1886,519)),((2014,519),(1950,519),(2014,396)),((1975,225),(2001,298),(1949,152)),((1850,60),(1907,96),(1792,22)),((1622,-14),(1716,-2),(1527,-26)),((1274,-32),(1411,-32),(1140,-32)),((871,-32),(1005,-32),(721,-32)),((501,-2),(598,-22),(404,19)),((274,111),(329,56),(220,166)),((160,347),(182,244),(139,450))]]),'I':(576,[[((192,0),(256,0),(192,512)),((192,1536),(192,1024),(256,1536)),((384,1536),(320,1536),(384,1024)),((384,0),(384,512),(320,0))]]),'L':(1664,[[((192,0),(661,0),(192,512)),((192,1536),(192,1024),(256,1536)),((384,1536),(320,1536),(384,1077)),((384,160),(384,619),(789,160)),((1600,160),(1195,160),(1600,107)),((1600,0),(1600,53),(1131,0))]]),'N':(2321,[[((192,0),(256,0),(192,512)),((192,1536),(192,1024),(259,1536)),((392,1536),(325,1536),(906,1103)),((1935,237),(1421,670),(1936,237)),((1937,237),(1936,237),(1937,670)),((1937,1536),(1937,1103),(2001,1536)),((2129,1536),(2065,1536),(2129,1024)),((2129,0),(2129,512),(2062,0)),((1929,0),(1996,0),(1415,437)),((386,1310),(900,873),(385,1310)),((384,1310),(385,1310),(384,873)),((384,0),(384,437),(320,0))]]),'O':(2145,[[((871,-32),(1005,-32),(721,-32)),((501,-2),(598,-22),(404,19)),((274,111),(329,56),(220,166)),((160,347),(182,244),(139,450)),((128,748),(128,583),(128,761)),((128,788),(128,775),(128,924)),((148,1130),(135,1038),(161,1223)),((217,1356),(184,1298),(250,1414)),((350,1489),(294,1458),(407,1520)),((563,1552),(478,1540),(648,1562)),((871,1568),(751,1568),(1005,1568)),((1274,1568),(1140,1568),(1394,1568)),((1582,1552),(1497,1562),(1667,1540)),((1794,1489),(1738,1520),(1851,1458)),((1928,1356),(1895,1414),(1961,1298)),((1997,1130),(1984,1223),(2010,1038)),((2017,788),(2017,924),(2017,775)),((2017,748),(2017,761),(2017,583)),((1984,347),(2006,450),(1963,244)),((1870,111),(1925,166),(1816,56)),((1644,-2),(1741,19),(1547,-22)),((1274,-32),(1424,-32),(1140,-32))],[((871,134),(776,134),(1005,134)),((1274,134),(1140,134),(1369,134)),((1515,144),(1450,137),(1580,151)),((1674,187),(1634,165),(1716,209)),((1768,287),(1747,242),(1790,332)),((1813,466),(1805,391),(1821,541)),((1825,748),(1825,635),(1825,761)),((1825,788),(1825,775),(1825,905)),((1813,1078),(1821,1002),(1805,1154)),((1768,1258),(1790,1214),(1747,1302)),((1674,1354),(1716,1334),(1634,1375)),((1515,1394),(1580,1388),(1450,1399)),((1274,1402),(1369,1402),(1140,1402)),((871,1402),(1005,1402),(776,1402)),((630,1394),(695,1399),(565,1388)),((470,1354),(512,1375),(430,1334)),((376,1258),(398,1302),(355,1214)),((332,1078),(340,1154),(324,1002)),((320,788),(320,905),(320,775)),((320,748),(320,761),(320,635)),((332,466),(324,541),(340,391)),((376,287),(355,332),(398,242)),((470,187),(430,209),(512,165)),((630,144),(565,151),(695,137))]]),'R':(2087,[[((196,1536),(196,1024),(539,1536)),((1224,1536),(881,1536),(1374,1536)),((1586,1516),(1495,1529),(1678,1503)),((1795,1447),(1748,1480),(1842,1414)),((1891,1313),(1874,1370),(1908,1256)),((1916,1098),(1916,1185),(1916,1085)),((1916,1058),(1916,1071),(1916,978)),((1888,852),(1906,909),(1868,794)),((1778,712),(1832,747),(1724,676)),((1538,636),(1644,651),(1649,424)),((1872,0),(1761,212),(1808,0)),((1680,0),(1744,0),(1571,207)),((1353,622),(1462,415),(1340,621)),((1312,621),(1326,621),(1297,621)),((1267,621),(1282,621),(974,621)),((388,621),(681,621),(388,414)),((388,0),(388,207),(324,0)),((196,0),(260,0),(196,512))],[((388,787),(388,981),(671,787)),((1237,787),(954,787),(1351,787)),((1506,798),(1441,791),(1572,806)),((1652,839),(1620,820),(1682,858)),((1711,921),(1702,886),(1720,956)),((1724,1058),(1724,1002),(1724,1071)),((1724,1098),(1724,1085),(1724,1161)),((1706,1248),(1718,1211),(1694,1285)),((1634,1329),(1670,1312),(1598,1346)),((1473,1362),(1544,1358),(1402,1368)),((1187,1370),(1306,1370),(921,1370)),((388,1370),(654,1370),(388,1176))]]),'T':(1916,[[((862,0),(926,0),(862,459)),((862,1376),(862,917),(606,1376)),((94,1376),(350,1376),(94,1429)),((94,1536),(94,1483),(670,1536)),((1822,1536),(1246,1536),(1822,1483)),((1822,1376),(1822,1429),(1566,1376)),((1054,1376),(1310,1376),(1054,917)),((1054,0),(1054,459),(990,0))]]),'V':(2048,[[((896,0),(981,0),(620,512)),((68,1536),(344,1024),(141,1536)),((288,1536),(215,1536),(533,1069)),((1024,136),(779,603),(1269,603)),((1760,1536),(1515,1069),(1832,1536)),((1977,1536),(1905,1536),(1702,1024)),((1152,0),(1427,512),(1067,0))]]),'Y':(2176,[[((992,0),(1056,0),(992,213)),((992,640),(992,427),(704,939)),((128,1536),(416,1237),(213,1536)),((384,1536),(299,1536),(619,1285)),((1088,784),(853,1035),(1323,1035)),((1792,1536),(1557,1285),(1877,1536)),((2048,1536),(1963,1536),(1760,1237)),((1184,640),(1472,939),(1184,427)),((1184,0),(1184,213),(1120,0))]])}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgba(h, a=1.0):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


def set_input(node, names, value):
    """Set the first existing input among several possible names (API changes across versions)."""
    if isinstance(names, str):
        names = [names]
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return node.inputs[n]
    return None


def link_obj(obj, collection=None):
    (collection or bpy.context.scene.collection).objects.link(obj)
    return obj


def new_empty(name, loc=(0, 0, 0), parent=None, size=0.3):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = size
    e.location = loc
    link_obj(e)
    if parent:
        e.parent = parent
    return e


def mesh_obj(name, build, mat=None, parent=None, loc=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    link_obj(ob)
    if mat:
        ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
    ob.location = loc
    return ob


def sphere(name, radius=1.0, mat=None, parent=None, loc=(0, 0, 0), scale=(1, 1, 1), seg=64, rings=32):
    ob = mesh_obj(name, lambda bm: bmesh.ops.create_uvsphere(
        bm, u_segments=seg, v_segments=rings, radius=radius), mat, parent, loc)
    ob.scale = scale
    return ob


def cylinder_between(name, p1, p2, r, mat, parent=None):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    ob = mesh_obj(name, lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, segments=32, radius1=r, radius2=r, depth=d.length), mat, parent)
    ob.location = (p1 + p2) / 2
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    return ob


def curve_obj(name, points, bevel, mat, parent=None, cyclic=False, kind="POLY", res=12):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = bevel
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    cu.resolution_u = res
    sp = cu.splines.new(kind)
    sp.points.add(len(points) - 1)
    for p, co in zip(sp.points, points):
        p.co = (co[0], co[1], co[2], 1.0)
    sp.use_cyclic_u = cyclic
    if kind == "NURBS":
        sp.use_endpoint_u = True
        sp.order_u = 3
    ob = bpy.data.objects.new(name, cu)
    link_obj(ob)
    if mat:
        cu.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob


def circle_pts(r, n=128, plane="XZ"):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if plane == "XZ":
            pts.append((r * math.cos(a), 0, r * math.sin(a)))
        else:
            pts.append((r * math.cos(a), r * math.sin(a), 0))
    return pts


def kf(target, path, frame, value, index=-1):
    if index >= 0:
        getattr(target, path)[index] = value
    else:
        setattr(target, path, value)
    target.keyframe_insert(data_path=path, frame=frame, index=index)


def kf_vec(obj, path, frame, value):
    setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame)


def kf_socket(socket, frame, value):
    socket.default_value = value
    socket.keyframe_insert("default_value", frame=frame)


def surface_point(center, r, az_deg, el_deg, inset=0.0):
    """Point on a sphere facing the camera (-Y), with outward normal."""
    az, el = math.radians(az_deg), math.radians(el_deg)
    n = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return Vector(center) + n * (r - inset), n


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------
def principled(name, color, rough=0.4, metal=0.0, coat=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    set_input(b, "Base Color", hex_rgba(color))
    set_input(b, "Roughness", rough)
    set_input(b, "Metallic", metal)
    set_input(b, ["Coat Weight", "Clearcoat"], coat)
    set_input(b, ["Coat Roughness", "Clearcoat Roughness"], 0.05)
    if emit:
        set_input(b, ["Emission Color", "Emission"], hex_rgba(emit))
        set_input(b, "Emission Strength", emit_strength)
    return m


def emission(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hex_rgba(color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def pillar_material(name, color, strength):
    """Emission that brightens toward the top of each bar."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.02, 0.03, 0.05, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = hex_rgba(color)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    glossy = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_input(glossy, "Base Color", hex_rgba(SLATE_DEEP))
    set_input(glossy, "Roughness", 0.15)
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(glossy.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    return m


def grid_floor_material():
    """Glossy dark floor with glowing grid lines that fade with distance."""
    m = bpy.data.materials.new("Floor_DataGrid")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    tc = N("ShaderNodeTexCoord")
    sep = N("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], sep.inputs[0])

    def line(axis_out, spacing, width):
        div = N("ShaderNodeMath"); div.operation = "DIVIDE"; div.inputs[1].default_value = spacing
        fr = N("ShaderNodeMath"); fr.operation = "FRACT"
        sub = N("ShaderNodeMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = 0.5
        ab = N("ShaderNodeMath"); ab.operation = "ABSOLUTE"
        gt = N("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5 - width
        L(axis_out, div.inputs[0]); L(div.outputs[0], fr.inputs[0]); L(fr.outputs[0], sub.inputs[0])
        L(sub.outputs[0], ab.inputs[0]); L(ab.outputs[0], gt.inputs[0])
        return gt.outputs[0]

    gx = line(sep.outputs["X"], 1.0, 0.012)
    gy = line(sep.outputs["Y"], 1.0, 0.012)
    mx = N("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L(gx, mx.inputs[0]); L(gy, mx.inputs[1])

    # radial fade: 1 near the centre, 0 far away
    ln = N("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    L(tc.outputs["Object"], ln.inputs[0])
    fade = N("ShaderNodeMapRange")
    fade.inputs["From Min"].default_value = 3.0
    fade.inputs["From Max"].default_value = 22.0
    fade.inputs["To Min"].default_value = 1.0
    fade.inputs["To Max"].default_value = 0.0
    L(ln.outputs["Value"], fade.inputs["Value"])
    mul = N("ShaderNodeMath"); mul.operation = "MULTIPLY"
    L(mx.outputs[0], mul.inputs[0]); L(fade.outputs["Result"], mul.inputs[1])

    pulse = N("ShaderNodeMath"); pulse.operation = "MULTIPLY"   # inputs[1] = animatable intensity
    pulse.inputs[1].default_value = 1.0
    L(mul.outputs[0], pulse.inputs[0])

    em = N("ShaderNodeEmission")
    em.inputs["Color"].default_value = hex_rgba("#3E6E9A")
    L(pulse.outputs[0], em.inputs["Strength"])

    bsdf = N("ShaderNodeBsdfPrincipled")
    set_input(bsdf, "Base Color", hex_rgba("#0A1119"))
    set_input(bsdf, "Roughness", 0.12)
    add = N("ShaderNodeAddShader")
    L(bsdf.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1])
    L(add.outputs[0], out.inputs["Surface"])
    return m, pulse


# --------------------------------------------------------------------------
# Scene reset & render settings
# --------------------------------------------------------------------------
def reset_scene():
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                 bpy.data.lights, bpy.data.cameras, bpy.data.worlds, bpy.data.actions):
        for block in list(coll):
            coll.remove(block)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, FRAME_END
    sc.render.fps = FPS
    sc.frame_set(1)
    return sc


def render_settings(sc):
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    ee = sc.eevee
    for attr, val in (("taa_render_samples", RENDER_SAMPLES), ("use_raytracing", True),
                      ("use_shadows", True), ("volumetric_tile_size", "4"),
                      ("volumetric_samples", 96), ("use_volumetric_shadows", True),
                      ("volumetric_end", 60.0), ("use_gtao", True), ("use_bloom", True)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception:
                pass
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    sc.render.use_motion_blur = True
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    sc.view_settings.exposure = 0.3

    sc.render.filepath = OUTPUT_PATH
    try:
        if hasattr(sc.render.image_settings, "media_type"):
            sc.render.image_settings.media_type = "VIDEO"
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
    except Exception:
        sc.render.image_settings.file_format = "PNG"   # fallback: image sequence


def setup_bloom(sc):
    """Fog-glow bloom in the compositor (handles both the 4.x and 5.x compositor APIs)."""
    if hasattr(sc, "compositing_node_group"):              # Blender 5.x
        ng = bpy.data.node_groups.new("Clairvoyant_Comp", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        sc.compositing_node_group = ng
        out = ng.nodes.new("NodeGroupOutput")
        out_socket = out.inputs[0]
    else:                                                  # Blender 4.x
        sc.use_nodes = True
        ng = sc.node_tree
        ng.nodes.clear()
        out = ng.nodes.new("CompositorNodeComposite")
        out_socket = out.inputs["Image"]
    rl = ng.nodes.new("CompositorNodeRLayers")
    glare = ng.nodes.new("CompositorNodeGlare")
    if "Type" in glare.inputs:                             # 4.5+/5.x: options are sockets
        for v in ("Bloom", "BLOOM", "Fog Glow", "FOG_GLOW"):
            try:
                glare.inputs["Type"].default_value = v
                break
            except Exception:
                continue
        set_input(glare, "Threshold", 0.8)
        set_input(glare, "Strength", 0.9)
        set_input(glare, "Size", 0.75)
        try:
            glare.inputs["Quality"].default_value = "High"
        except Exception:
            pass
    else:
        glare.glare_type = "BLOOM" if "BLOOM" in [i.identifier for i in glare.bl_rna.properties["glare_type"].enum_items] else "FOG_GLOW"
        glare.threshold = 0.8
        glare.quality = "HIGH"
        if hasattr(glare, "size"):
            glare.size = 7
    lens = ng.nodes.new("CompositorNodeLensdist")
    set_input(lens, ["Dispersion", "Dispersion"], 0.012)
    set_input(lens, "Distortion", -0.01)
    ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
    ng.links.new(glare.outputs[0], lens.inputs["Image"])
    ng.links.new(lens.outputs[0], out_socket)


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------
def build_world(sc):
    w = bpy.data.worlds.new("Clairvoyant_Night")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    # gradient sky: deep slate at the horizon to near-black overhead
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = hex_rgba("#1B2C3D")
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = hex_rgba("#05080C")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.6
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    # atmospheric haze for light shafts
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.018
    set_input(vol, "Color", hex_rgba("#9DB4CC"))
    set_input(vol, "Anisotropy", 0.35)
    nt.links.new(vol.outputs[0], out.inputs["Volume"])


def build_stage():
    floor_mat, grid_strength = grid_floor_material()
    floor = mesh_obj("Floor", lambda bm: bmesh.ops.create_grid(
        bm, x_segments=1, y_segments=1, size=40), floor_mat, smooth=False)

    # glowing ring "plinth" under Orb
    plinth = curve_obj("Plinth_Ring", circle_pts(1.9, plane="XY"), 0.025,
                       emission("Plinth_Glow", ICE, 6.0), cyclic=True)
    plinth.location.z = 0.01
    build_stage.plinth = plinth

    # floating motes: one mesh of many tiny spheres, slowly rotating
    import random
    random.seed(7)

    def motes(bm):
        for _ in range(220):
            r = random.uniform(2.5, 14)
            a = random.uniform(0, 2 * math.pi)
            z = random.uniform(0.3, 7)
            s = random.uniform(0.01, 0.035)
            mat = Matrix.Translation((r * math.cos(a), r * math.sin(a), z))
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s, matrix=mat)
    dust = mesh_obj("Floating_Motes", motes, emission("Mote_Glow", AMBER, 18.0), smooth=False)
    kf(dust, "rotation_euler", 1, 0.0, index=2)
    kf(dust, "rotation_euler", FRAME_END, math.radians(40), index=2)
    kf(dust, "location", 1, 0.0, index=2)
    kf(dust, "location", FRAME_END, 0.6, index=2)

    # distant monolith silhouettes for depth
    for i, (x, y, h) in enumerate([(-11, 14, 6), (-6, 18, 9), (7, 17, 7.5), (12, 13, 5), (1, 22, 11)]):
        mono = mesh_obj(f"Monolith_{i}", lambda bm: bmesh.ops.create_cube(bm, size=1.0),
                        principled(f"Monolith_Mat_{i}", "#0E1823", rough=0.3,
                                   emit="#2A4A6A", emit_strength=0.15), smooth=False)
        mono.scale = (1.2, 1.2, h)
        mono.location = (x, y, h / 2)
    return floor, grid_strength


def build_lights():
    def light(name, kind, loc, rot, energy, color, size=1.0, spot=None):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = hex_rgba(color)[:3]
        if kind == "AREA":
            ld.size = size
        if kind == "SPOT" and spot:
            ld.spot_size = math.radians(spot)
            ld.spot_blend = 0.6
        if hasattr(ld, "use_shadow"):
            ld.use_shadow = True
        ob = bpy.data.objects.new(name, ld)
        ob.location = loc
        ob.rotation_euler = [math.radians(a) for a in rot]
        link_obj(ob)
        return ob

    light("Key_Warm", "AREA", (-4.5, -5.5, 5.5), (55, 0, -40), 900, "#FFE8CC", size=4)
    light("Rim_Ice_R", "AREA", (4.5, 3.5, 3.5), (-60, 0, 130), 1200, "#7FC4FF", size=2)
    light("Rim_Ice_L", "AREA", (-4.5, 3.0, 2.5), (-65, 0, -130), 700, "#5AA0E6", size=2)
    shaft = light("God_Ray_Spot", "SPOT", (1.5, 4.0, 11), (-20, 8, 0), 9000, "#DDEBFF", spot=34)
    return shaft


# --------------------------------------------------------------------------
# Orb the mascot
# --------------------------------------------------------------------------
def build_orb():
    m_body = principled("Orb_Body", "#46647F", rough=0.3, coat=0.8)  # brand slate, lifted for 3D lighting
    m_white = principled("Orb_EyeWhite", "#F4F7FA", rough=0.25, coat=0.5)
    m_pupil = principled("Orb_Pupil", "#0B1118", rough=0.08, coat=1.0)
    m_shine = emission("Orb_EyeShine", "#FFFFFF", 6.0)
    m_blush = principled("Orb_Blush", BLUSH, rough=0.6, emit=BLUSH, emit_strength=0.4)
    m_amber = emission("Orb_Amber", AMBER, 12.0)
    m_mouth = principled("Orb_Mouth", "#0B1118", rough=0.4)

    root = new_empty("Orb_Root", (0, 0, 0), size=0.8)
    # body pivot sits at the bottom of the sphere so squash keeps him grounded
    body = new_empty("Orb_Body_Ctrl", (0, 0, 0.85), parent=root, size=0.5)
    R = 1.0
    C = Vector((0, 0, R))      # sphere centre in body space

    sphere("Orb_Sphere", R, m_body, body, C)

    # eyes: a control empty per eye (blink = scale Z), white, pupil, two shines
    eyes, pupils = [], []
    for side, az in (("L", -24), ("R", 24)):
        p, n = surface_point(C, R, az, 14, inset=0.06)
        ctrl = new_empty(f"Orb_Eye_{side}", p, body, size=0.2)
        ctrl.rotation_mode = "QUATERNION"
        ctrl.rotation_quaternion = n.to_track_quat("-Y", "Z")
        sphere(f"Orb_EyeWhite_{side}", 1.0, m_white, ctrl, (0, 0, 0), (0.27, 0.13, 0.31))
        pup = new_empty(f"Orb_PupilCtrl_{side}", (0, -0.06, 0), ctrl, size=0.1)
        sphere(f"Orb_Pupil_{side}", 1.0, m_pupil, pup, (0, 0, 0), (0.16, 0.11, 0.19))
        sphere(f"Orb_Shine_{side}", 1.0, m_shine, pup, (0.06, -0.1, 0.08), (0.05, 0.03, 0.05), seg=16, rings=8)
        sphere(f"Orb_Shine2_{side}", 1.0, m_shine, pup, (-0.05, -0.1, -0.07), (0.022, 0.015, 0.022), seg=12, rings=6)
        eyes.append(ctrl)
        pupils.append(pup)

    # cheeks
    for side, az in (("L", -46), ("R", 46)):
        p, n = surface_point(C, R, az, -6, inset=0.035)
        b = sphere(f"Orb_Blush_{side}", 1.0, m_blush, body, p, (0.15, 0.04, 0.08), seg=24, rings=12)
        b.rotation_mode = "QUATERNION"
        b.rotation_quaternion = n.to_track_quat("-Y", "Z")

    # smile (a soft curve hugging the sphere)
    pts = [surface_point(C, R + 0.005, az, el)[0] for az, el in ((-15, -12), (-7, -19), (0, -21), (7, -19), (15, -12))]
    curve_obj("Orb_Smile", pts, 0.03, m_mouth, body, kind="NURBS")

    # antenna: the logo's amber breakout line, now a springy stalk
    p, n = surface_point(C, R, 28, 58, inset=0.05)
    ant = new_empty("Orb_Antenna_Root", p, body, size=0.2)
    curve_obj("Orb_Antenna_Stalk", [(0, 0, 0), (0.12, -0.02, 0.35), (0.42, -0.05, 0.62)],
              0.035, m_amber, ant, kind="NURBS")
    tip = sphere("Orb_Antenna_Tip", 0.13, m_amber, ant, (0.45, -0.05, 0.66), seg=32, rings=16)
    tl = bpy.data.lights.new("Antenna_Glow", "POINT")
    tl.energy = 60
    tl.color = hex_rgba(AMBER)[:3]
    tl.shadow_soft_size = 0.15
    tlo = bpy.data.objects.new("Antenna_Glow", tl)
    tlo.parent = tip
    link_obj(tlo)

    # legs: the logo's V, now two chunky legs with bean feet
    legs, feet = [], []
    for side, sx in (("L", -1), ("R", 1)):
        legs.append(cylinder_between(f"Orb_Leg_{side}", (0.28 * sx, 0, 1.05), (0.42 * sx, -0.02, 0.2), 0.11, m_body, root))
        foot = sphere(f"Orb_Foot_{side}", 1.0, m_body, root, (0.45 * sx, -0.12, 0.13), (0.24, 0.34, 0.14))
        foot.rotation_euler.z = math.radians(-12 * sx)
        feet.append(foot)

    return dict(root=root, body=body, eyes=eyes, pupils=pupils, antenna=ant,
                tip=tip, tip_mat=m_amber, tip_light=tl, legs=legs, feet=feet, body_mat=m_body)


# --------------------------------------------------------------------------
# Story props: pillars, trend line, halo, wordmark, shockwave
# --------------------------------------------------------------------------
def build_pillars():
    pillars = []
    heights = (1.2, 1.6, 1.4, 2.1, 2.6, 3.1, 3.9)
    n = len(heights)
    for i, h in enumerate(heights):
        a = math.radians(205 - i * (230 / (n - 1)))      # arc behind Orb, left to right
        r = 3.6
        x, y = r * math.cos(a), abs(r * math.sin(a)) * 0.55 + 1.2
        last = i == n - 1
        mat = pillar_material(f"Pillar_Mat_{i}", AMBER if last else "#5FA8E8", 7.0 if last else 3.0)

        def cube(bm):
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.translate(bm, vec=(0, 0, 0.5), verts=bm.verts)   # origin at base
        p = mesh_obj(f"Pillar_{i}", cube, mat, loc=(x, y, 0), smooth=False)
        p.scale = (0, 0, 0)
        bev = p.modifiers.new("Bevel", "BEVEL")
        bev.width = 0.04
        bev.segments = 3
        pillars.append((p, h))
    return pillars


def animate_pillars(pillars, start=115):
    for i, (p, h) in enumerate(pillars):
        f0 = start + i * 5
        kf_vec(p, "scale", 1, (0, 0, 0))
        kf_vec(p, "scale", f0, (0, 0, 0))
        kf_vec(p, "scale", f0 + 4, (0.38, 0.38, 0.2))
        kf_vec(p, "scale", f0 + 12, (0.38, 0.38, h * 1.12))   # overshoot
        kf_vec(p, "scale", f0 + 18, (0.38, 0.38, h * 0.96))
        kf_vec(p, "scale", f0 + 24, (0.38, 0.38, h))


def build_trend(pillars):
    pts = [(p.location.x, p.location.y - 0.2, h + 0.35) for p, h in pillars]
    line = curve_obj("Trend_Line", pts, 0.045, emission("Trend_Glow", AMBER, 16.0))
    line.data.bevel_factor_mapping_end = "SPLINE"
    kf(line.data, "bevel_factor_end", 1, 0.0)
    kf(line.data, "bevel_factor_end", 170, 0.0)
    kf(line.data, "bevel_factor_end", 205, 1.0)

    end = sphere("Trend_Point", 0.16, emission("Trend_Point_Glow", AMBER, 25.0),
                 loc=pts[-1], seg=32, rings=16)
    for f, s in ((1, 0.0), (204, 0.0), (210, 1.6), (216, 1.0)):
        kf_vec(end, "scale", f, (s, s, s))
    return line, end


def build_halo():
    """The logo's open C ring, drawn around Orb. Gap faces right (+X), like the mark."""
    halo = curve_obj("Halo_C_Ring", circle_pts(2.05, 160, "XZ"), 0.075,
                     emission("Halo_Glow", ICE, 9.0), cyclic=False)
    halo.location = (0, -0.1, 1.85)
    d = halo.data
    d.bevel_factor_mapping_start = "SPLINE"
    d.bevel_factor_mapping_end = "SPLINE"
    kf(d, "bevel_factor_start", 1, 0.08)
    kf(d, "bevel_factor_end", 1, 0.08)
    kf(d, "bevel_factor_end", 215, 0.08)
    kf(d, "bevel_factor_end", 250, 0.92)
    halo["base_radius"] = 2.05
    # thin inner hairline ring, like the mark's inner ring
    inner = curve_obj("Halo_Inner_Ring", circle_pts(1.78, 160, "XZ"), 0.015,
                      emission("Halo_Inner_Glow", ICE, 5.0))
    inner.location = halo.location
    inner.data.bevel_factor_mapping_start = "SPLINE"
    inner.data.bevel_factor_mapping_end = "SPLINE"
    kf(inner.data, "bevel_factor_start", 1, 0.12)
    kf(inner.data, "bevel_factor_end", 1, 0.12)
    kf(inner.data, "bevel_factor_end", 228, 0.12)
    kf(inner.data, "bevel_factor_end", 258, 0.88)
    # slow settle rotation for life
    for ob in (halo, inner):
        kf(ob, "rotation_euler", 215, math.radians(-40), index=1)
        kf(ob, "rotation_euler", 265, 0.0, index=1)
    return halo, inner


def shockwave(frame, z=0.02, max_r=4.0, name="Shockwave"):
    mat = emission(f"{name}_Mat", ICE, 0.0)
    ring = curve_obj(name, circle_pts(1.0, 96, "XY"), 0.03, mat, cyclic=True)
    ring.location.z = z
    s = mat.node_tree.nodes["Emission"].inputs["Strength"]
    for f, r, e in ((1, 0.01, 0.0), (frame - 1, 0.01, 0.0), (frame, 0.6, 25.0), (frame + 25, max_r, 0.0)):
        kf_vec(ring, "scale", f, (r, r, r))
        kf_socket(s, f, e)
    return ring


# --------------------------------------------------------------------------
# The official logo (end card) and the transformation
# --------------------------------------------------------------------------
GAP_OUTER = math.degrees(math.atan2(115 - 84, 236 - 190)) / 360.0    # ring opening, as a curve fraction
GAP_INNER = math.degrees(math.atan2(115 - 91, 225 - 190)) / 360.0
T_SWAP = 340            # frame where the morphing mascot parts hand over to the clean logo


def vis(ob, frame, visible):
    ob.hide_render = not visible
    ob.hide_viewport = not visible
    ob.keyframe_insert("hide_render", frame=frame)
    ob.keyframe_insert("hide_viewport", frame=frame)


def letter_curve(name, ch, em, mat, parent):
    adv, contours = MICHROMA[ch]
    k = em / MICHROMA_UPM
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = 0.018
    cu.bevel_depth = 0.004
    cu.resolution_u = 16
    for cont in contours:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(cont) - 1)
        for bp, (a, hl, hr) in zip(sp.bezier_points, cont):
            bp.handle_left_type = "FREE"
            bp.handle_right_type = "FREE"
            bp.co = (a[0] * k, a[1] * k, 0)
            bp.handle_left = (hl[0] * k, hl[1] * k, 0)
            bp.handle_right = (hr[0] * k, hr[1] * k, 0)
        sp.use_cyclic_u = True
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    link_obj(ob)
    ob.parent = parent
    ob.rotation_euler.x = math.radians(90)      # stand the letter up in the logo plane, facing -Y
    return ob, adv * k


def build_logo():
    """Every element of the official stacked lockup, 1:1 with clairvoyant-lockup-stacked-dark.svg."""
    root = new_empty("Logo_Root", (0, 0, 0), size=1.0)
    m_white = principled("Logo_White", LOGO_WHITE, rough=0.3, emit=LOGO_WHITE, emit_strength=1.6)
    m_amber = emission("Logo_Amber", AMBER, 3.0)   # kept low so bloom doesn't wash the amber to white
    L = {"root": root, "white": m_white, "amber": m_amber}

    def tube(name, pts, stroke, mat):
        ob = curve_obj(name, pts, stroke * S_LOGO / 2, mat, parent=root)
        ob.data.bevel_factor_mapping_start = "SPLINE"
        ob.data.bevel_factor_mapping_end = "SPLINE"
        return ob

    # open C ring + hairline inner ring (gap faces right, as in the mark)
    L["ring"] = tube("Logo_Ring", circle_pts(1.0, 160, "XZ"), 12, m_white)
    L["ring"].location.z = LOGO_Z0
    L["ring"].data.bevel_factor_start, L["ring"].data.bevel_factor_end = GAP_OUTER, 1 - GAP_OUTER
    L["inner"] = tube("Logo_Inner_Ring", circle_pts(42 * S_LOGO, 160, "XZ"), 2, m_white)
    L["inner"].location.z = LOGO_Z0
    L["inner"].data.bevel_factor_start, L["inner"].data.bevel_factor_end = GAP_INNER, 1 - GAP_INNER

    # baseline, KPI bars (last one amber), breakout line and point
    L["baseline"] = tube("Logo_Baseline", [(LX(152), 0, LZ(150)), (LX(228), 0, LZ(150))], 2, m_white)
    L["bars"] = []
    for i, (bx, bh) in enumerate(((158, 18), (174, 26), (190, 34), (206, 44))):
        def cube(bm):
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.translate(bm, vec=(0, 0, 0.5), verts=bm.verts)
        bar = mesh_obj(f"Logo_Bar_{i}", cube, m_amber if i == 3 else m_white,
                       root, (LX(bx + 5), 0, LZ(150)), smooth=False)
        bar.scale = (10 * S_LOGO, 0.12, bh * S_LOGO)
        L["bars"].append(bar)
    L["breakout"] = tube("Logo_Breakout", [(LX(211), 0, LZ(106)), (LX(256), 0, LZ(88))], 3, m_amber)
    L["dot"] = sphere("Logo_Breakout_Point", 5 * S_LOGO, m_amber, root, (LX(258), 0, LZ(87)), seg=32, rings=16)

    # V stand and groundline
    L["v"] = tube("Logo_V_Stand", [(LX(148), 0, LZ(168)), (LX(190), 0, LZ(210)), (LX(232), 0, LZ(168))], 6, m_white)
    L["ground"] = tube("Logo_Groundline", [(LX(158), 0, LZ(218)), (LX(222), 0, LZ(218))], 6, m_white)

    # wordmark: Michroma, 7% tracking, centred under the mark, same spacing as the stacked lockup
    em = (40 / 2.25) * S_LOGO
    track = 0.07 * em
    text = "CLAIRVOYANT"
    width = sum(MICHROMA[c][0] for c in text) * em / MICHROMA_UPM + track * (len(text) - 1)
    cap = MICHROMA_CAP / MICHROMA_UPM * em
    base_z = LZ(221) - (46 / 2.25) * S_LOGO - cap
    x = LX(195.5) - width / 2                      # stacked lockup centres the mark's bbox over the text
    L["letters"] = []
    for i, ch in enumerate(text):
        ob, adv = letter_curve(f"Logo_Letter_{i:02d}_{ch}", ch, em, m_white, root)
        ob.location = (x, 0, base_z)
        L["letters"].append(ob)
        x += adv + track
    return L


def animate_transformation(sc, orb, logo, halo, inner, pillars, trend_root, plinth):
    T0 = 285
    body, root = orb["body"], orb["root"]

    # -- settle into a calm pose, then close the eyes happily ------------------
    kf(body, "location", T0, 0.85, index=2)
    kf_vec(body, "scale", T0, (1, 1, 1))
    kf(body, "rotation_euler", T0, 0.0, index=1)
    for p in orb["pupils"]:
        kf_vec(p, "location", T0, (0, -0.06, 0))
    for e in orb["eyes"]:
        kf_vec(e, "scale", 292, (1, 1, 1))
        kf_vec(e, "scale", 298, (1.08, 1, 0.07))

    # -- he starts to glow ----------------------------------------------------
    b = orb["body_mat"].node_tree.nodes["Principled BSDF"]
    set_input(b, ["Emission Color", "Emission"], hex_rgba(LOGO_WHITE))
    es = b.inputs["Emission Strength"]
    kf_socket(es, 1, 0.0)
    kf_socket(es, 296, 0.0)
    kf_socket(es, 320, 5.0)
    bc = b.inputs["Base Color"]
    kf_socket(bc, 296, bc.default_value[:])
    kf_socket(bc, 320, hex_rgba(LOGO_WHITE))

    # -- antenna spark flies out and becomes the breakout point ---------------
    sc.frame_set(300)
    tip_world = orb["tip"].matrix_world.translation.copy()
    ant = orb["antenna"]
    kf_vec(ant, "scale", 300, (1, 1, 1))
    kf_vec(ant, "scale", 306, (0, 0, 0))
    for f, e in ((296, 60), (304, 0)):
        kf(orb["tip_light"], "energy", f, e)
    dot = logo["dot"]
    dot_home = dot.location.copy()
    mid = (tip_world + dot_home) / 2 + Vector((0.3, -0.6, 1.0))
    kf_vec(dot, "scale", 1, (0, 0, 0))
    kf_vec(dot, "scale", 299, (0, 0, 0))
    kf_vec(dot, "scale", 300, (1.5, 1.5, 1.5))
    kf_vec(dot, "location", 300, tip_world)
    kf_vec(dot, "location", 315, mid)
    kf_vec(dot, "location", 330, dot_home)
    kf_vec(dot, "scale", 330, (1.0, 1.0, 1.0))
    kf_vec(dot, "scale", 362, (1.0, 1.0, 1.0))
    kf_vec(dot, "scale", 365, (1.9, 1.9, 1.9))      # pulse when the breakout line arrives
    kf_vec(dot, "scale", 372, (1.0, 1.0, 1.0))
    sl = bpy.data.lights.new("Spark_Glow", "POINT")
    sl.color = hex_rgba(AMBER)[:3]
    sl.shadow_soft_size = 0.1
    slo = bpy.data.objects.new("Spark_Glow", sl)
    slo.parent = dot
    link_obj(slo)
    for f, e in ((1, 0), (299, 0), (300, 250), (330, 120), (365, 500), (380, 60)):
        kf(sl, "energy", f, e)

    # -- the body dissolves into light (shrinks about the ring centre) --------
    for f, s_, z in ((300, 1.0, 0.85), (312, 0.8, 1.11), (322, 0.42, 1.49), (334, 0.0, LOGO_Z0)):
        kf_vec(body, "scale", f, (s_, s_, s_))
        kf(body, "location", f, z, index=2)

    # -- halo tightens into the logo's C ring ---------------------------------
    for ob, r_target, stroke, gap, t1 in ((halo, 1.0, 12, GAP_OUTER, 335), (inner, 42 * S_LOGO, 2, GAP_INNER, 338)):
        sc_t = r_target / (2.05 if ob is halo else 1.78)
        d = ob.data
        kf_vec(ob, "scale", 300, (1, 1, 1))
        kf_vec(ob, "location", 300, tuple(ob.location))
        kf(d, "bevel_depth", 300, d.bevel_depth)
        kf(d, "bevel_factor_start", 300, d.bevel_factor_start)
        kf(d, "bevel_factor_end", 300, d.bevel_factor_end)
        kf_vec(ob, "scale", t1, (sc_t, sc_t, sc_t))
        kf_vec(ob, "location", t1, (0, 0, LOGO_Z0))
        kf(d, "bevel_depth", t1, (stroke * S_LOGO / 2) / sc_t)
        kf(d, "bevel_factor_start", t1, gap)
        kf(d, "bevel_factor_end", t1, 1 - gap)
        em = ob.active_material.node_tree.nodes["Emission"]
        kf_socket(em.inputs["Color"], 300, em.inputs["Color"].default_value[:])
        kf_socket(em.inputs["Color"], t1, hex_rgba(LOGO_WHITE))
        kf_socket(em.inputs["Strength"], 300, em.inputs["Strength"].default_value)
        kf_socket(em.inputs["Strength"], t1, 3.0)

    # -- legs fold into the V stand ------------------------------------------
    v_top = {-1: Vector((LX(148), 0, LZ(168))), 1: Vector((LX(232), 0, LZ(168)))}
    v_bot = Vector((LX(190), 0, LZ(210)))
    for leg, sx in zip(orb["legs"], (-1, 1)):
        L0 = leg.data.vertices[0].co.z * -2 if leg.data.vertices[0].co.z < 0 else leg.data.vertices[0].co.z * 2
        arm = v_bot - v_top[sx]
        kf_vec(leg, "location", 304, tuple(leg.location))
        kf_vec(leg, "rotation_quaternion", 304, tuple(leg.rotation_quaternion))
        kf_vec(leg, "scale", 304, (1, 1, 1))
        kf_vec(leg, "location", 334, tuple((v_top[sx] + v_bot) / 2))
        kf_vec(leg, "rotation_quaternion", 334, tuple(arm.to_track_quat("Z", "Y")))
        r_t = 3 * S_LOGO / 0.11
        kf_vec(leg, "scale", 334, (r_t, r_t, arm.length / L0))

    # -- feet merge into the groundline ---------------------------------------
    half = (LX(222) - LX(158)) / 4
    for foot, sx in zip(orb["feet"], (-1, 1)):
        kf_vec(foot, "location", 306, tuple(foot.location))
        kf_vec(foot, "scale", 306, tuple(foot.scale))
        kf(foot, "rotation_euler", 306, foot.rotation_euler.z, index=2)
        kf_vec(foot, "location", 336, (sx * half, 0, LZ(218)))
        kf_vec(foot, "scale", 336, (half * 1.05, 3 * S_LOGO, 3 * S_LOGO))
        kf(foot, "rotation_euler", 336, 0.0, index=2)

    # -- clear the stage: pillars sink, trend line retracts, plinth closes ----
    for i, (p, h) in enumerate(pillars):
        f0 = 288 + i * 3
        kf_vec(p, "scale", f0, (0.38, 0.38, h))
        kf_vec(p, "scale", f0 + 16, (0.38, 0.38, 0.0))
        kf_vec(p, "scale", f0 + 17, (0, 0, 0))
    tl, tp = trend_root
    kf(tl.data, "bevel_factor_start", 1, 0.0)
    kf(tl.data, "bevel_factor_start", 290, 0.0)
    kf(tl.data, "bevel_factor_start", 312, 1.0)
    kf_vec(tp, "scale", 296, (1, 1, 1))
    kf_vec(tp, "scale", 304, (0, 0, 0))
    kf_vec(plinth, "scale", 300, (1, 1, 1))
    kf_vec(plinth, "scale", 330, (0, 0, 0))

    # -- hand-over: morphing mascot parts -> clean logo parts -----------------
    mascot = [ob for ob in bpy.data.objects if ob.name.startswith("Orb_") or ob.name == "Antenna_Glow"]
    for ob in mascot + [halo, inner]:
        vis(ob, 1, True)
        vis(ob, T_SWAP, False)
    for ob in (logo["ring"], logo["inner"], logo["v"], logo["ground"]):
        vis(ob, 1, False)
        vis(ob, T_SWAP, True)

    # -- the chart inside the C draws itself ----------------------------------
    bl = logo["baseline"].data
    kf(bl, "bevel_factor_end", 1, 0.0)
    kf(bl, "bevel_factor_end", 334, 0.0)
    kf(bl, "bevel_factor_end", 344, 1.0)
    for i, bar in enumerate(logo["bars"]):
        full = tuple(bar.scale)
        f0 = 340 + i * 4
        kf_vec(bar, "scale", 1, (0, 0, 0))            # fully hidden, not just flattened
        kf_vec(bar, "scale", f0 - 1, (0, 0, 0))
        kf_vec(bar, "scale", f0, (full[0], full[1], 0))
        kf_vec(bar, "scale", f0 + 7, (full[0], full[1], full[2] * 1.15))
        kf_vec(bar, "scale", f0 + 11, full)
    bo = logo["breakout"].data
    kf(bo, "bevel_factor_end", 1, 0.0)
    kf(bo, "bevel_factor_end", 355, 0.0)
    kf(bo, "bevel_factor_end", 364, 1.0)

    # white flash through the logo at the hand-over, then settle
    ws = logo["white"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f, e in ((1, 1.6), (T_SWAP - 1, 1.6), (T_SWAP, 9.0), (T_SWAP + 14, 1.6)):
        kf_socket(ws, f, e)

    # -- lift the lockup and reveal the wordmark letter by letter -------------
    lr = logo["root"]
    kf(lr, "location", 368, 0.0, index=2)
    kf(lr, "location", 388, LOGO_LIFT, index=2)
    for i, ob in enumerate(logo["letters"]):
        f0 = 380 + i * 2
        kf_vec(ob, "scale", 1, (0, 0, 0))
        kf_vec(ob, "scale", f0, (0, 0, 0))
        kf_vec(ob, "scale", f0 + 5, (1.15, 1.15, 1.15))
        kf_vec(ob, "scale", f0 + 9, (1, 1, 1))



# --------------------------------------------------------------------------
# Character animation
# --------------------------------------------------------------------------
def animate_orb(o, trend_point):
    root, body, ant = o["root"], o["body"], o["antenna"]

    def squash(f, sxy, sz):
        kf_vec(body, "scale", f, (sxy, sxy, sz))

    # 1) drop in from the sky and land (frame 40)
    kf(root, "location", 1, 7.0, index=2)
    kf(root, "location", 40, 0.0, index=2)
    squash(1, 0.92, 1.12)
    squash(36, 0.86, 1.22)            # stretched while falling
    squash(42, 1.28, 0.68)            # impact squash
    squash(48, 0.93, 1.1)
    squash(54, 1.04, 0.97)
    squash(60, 1.0, 1.0)

    # antenna spring wobble after landing (decaying)
    for f, a in ((1, -10), (40, -18), (44, 26), (49, -16), (54, 9), (59, -4), (64, 0)):
        kf(ant, "rotation_euler", f, math.radians(a), index=1)

    # 2) look left, look right, blink
    def look(f, x, z):
        for p in o["pupils"]:
            kf_vec(p, "location", f, (x, -0.06, z))

    def tilt(f, deg):
        kf(body, "rotation_euler", f, math.radians(deg), index=1)

    look(60, 0, 0); tilt(60, 0)
    look(66, -0.1, 0.02); tilt(68, -6)
    look(80, -0.1, 0.02); tilt(80, -6)
    look(86, 0.1, 0.02); tilt(88, 6)
    look(100, 0.1, 0.02); tilt(100, 6)
    look(106, 0, 0); tilt(108, 0)

    def blink(f):
        for e in o["eyes"]:
            kf_vec(e, "scale", f, (1, 1, 1))
            kf_vec(e, "scale", f + 3, (1.05, 1, 0.08))
            kf_vec(e, "scale", f + 6, (1, 1, 1))
    blink(110)
    blink(158)

    # 3) excited hops while the pillars rise
    for f0 in (124, 144):
        kf(root, "location", f0, 0.0, index=2)
        squash(f0, 1.15, 0.85)
        kf(root, "location", f0 + 7, 0.75, index=2)
        squash(f0 + 4, 0.9, 1.15)
        kf(root, "location", f0 + 14, 0.0, index=2)
        squash(f0 + 14, 1.18, 0.82)
        squash(f0 + 19, 1.0, 1.0)
        for f, a in ((f0 + 14, -14), (f0 + 18, 12), (f0 + 23, -5), (f0 + 28, 0)):
            kf(ant, "rotation_euler", f, math.radians(a), index=1)

    # 4) watch the trend line draw up and to the right
    look(172, 0.0, 0.0)
    look(185, 0.06, 0.06)
    look(205, 0.11, 0.09)
    tilt(172, 0); tilt(205, 8)
    # antenna tip flashes when the trend hits its peak
    tip_strength = o["tip_mat"].node_tree.nodes["Emission"].inputs["Strength"]
    for f, e in ((1, 12.0), (204, 12.0), (208, 60.0), (222, 12.0)):
        kf_socket(tip_strength, f, e)
    for f, e in ((1, 60), (204, 60), (208, 400), (222, 60)):
        kf(o["tip_light"], "energy", f, e)

    # 5) proud pose: look at camera, puff up slightly as the halo forms
    look(225, 0, 0); tilt(225, 0)
    squash(232, 1.0, 1.0)
    squash(240, 1.06, 1.06)
    squash(250, 1.0, 1.0)
    blink(268)
    # gentle idle bob to the end
    for i, f in enumerate(range(250, 286, 12)):
        kf(body, "location", f, 0.85 + (0.04 if i % 2 else 0.0), index=2)


# --------------------------------------------------------------------------
# Camera
# --------------------------------------------------------------------------
def build_camera(sc, orb_root):
    target = new_empty("Camera_Target", (0, 0, 3.5), size=0.4)
    kf(target, "location", 1, 3.8, index=2)
    kf(target, "location", 40, 1.7, index=2)
    kf_vec(target, "location", 170, (0.6, 0.6, 2.0))
    kf_vec(target, "location", 210, (0.4, 0.4, 2.0))
    kf_vec(target, "location", 240, (0, 0, 1.5))
    kf_vec(target, "location", 285, (0, 0, 1.5))
    kf_vec(target, "location", 330, (0, 0, 1.9))
    kf_vec(target, "location", 365, (0, 0, 1.9))
    kf_vec(target, "location", 395, (0.098, 0, LOGO_Z0 + LOGO_LIFT - 0.7))

    cd = bpy.data.cameras.new("Camera")
    cd.lens = 40
    cd.dof.use_dof = True
    cd.dof.focus_object = target
    cd.dof.aperture_fstop = 2.2
    cam = bpy.data.objects.new("Camera", cd)
    link_obj(cam)
    sc.camera = cam
    # open the aperture up for the end card so the whole lockup is sharp
    for f, v in ((1, 2.2), (300, 2.2), (340, 8.0)):
        cd.dof.aperture_fstop = v
        cd.keyframe_insert("dof.aperture_fstop", frame=f)
    c = cam.constraints.new("TRACK_TO")
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    for f, loc in ((1, (0, -15, 6.5)), (40, (1.2, -11, 3.2)), (110, (-2.6, -9.5, 2.6)),
                   (170, (-4.0, -11.0, 3.6)), (215, (-2.0, -10.0, 3.0)),
                   (260, (0, -11.5, 2.9)), (285, (0.5, -11.0, 2.8)),
                   (330, (0.05, -11.5, 2.2)), (365, (0.08, -11.8, 2.3)),
                   (395, (0.098, -9.0, 2.42)), (FRAME_END, (0.098, -8.5, 2.42))):
        kf_vec(cam, "location", f, loc)
    return cam


# --------------------------------------------------------------------------
# Build it all
# --------------------------------------------------------------------------
def main():
    sc = reset_scene()
    render_settings(sc)
    build_world(sc)
    floor, grid_strength = build_stage()
    shaft = build_lights()
    orb = build_orb()
    pillars = build_pillars()
    animate_pillars(pillars)
    trend = build_trend(pillars)
    halo, inner = build_halo()
    logo = build_logo()
    shockwave(40, max_r=5.0, name="Landing_Shockwave")
    shockwave(208, z=0.02, max_r=7.0, name="Peak_Shockwave")
    shockwave(250, z=0.02, max_r=9.0, name="Halo_Shockwave")
    shockwave(T_SWAP, z=0.02, max_r=12.0, name="Transform_Shockwave")
    animate_orb(orb, trend[1].location)
    animate_transformation(sc, orb, logo, halo, inner, pillars, trend, build_stage.plinth)

    # floor grid pulses with the story beats
    for f, v in ((1, 0.6), (40, 0.6), (42, 3.0), (70, 0.8), (208, 2.5), (230, 0.9), (250, 3.0), (280, 1.2),
                 (T_SWAP, 3.5), (370, 0.7), (FRAME_END, 0.5)):
        kf_socket(grid_strength.inputs[1], f, v)
    # god-ray spotlight swells for the finale
    for f, e in ((1, 6000), (215, 6000), (250, 14000), (300, 11000), (T_SWAP, 18000), (380, 9000)):
        kf(shaft.data, "energy", f, e)

    build_camera(sc, orb["root"])
    setup_bloom(sc)
    sc.frame_set(1)
    print("Clairvoyant Orb scene built. Press Space to preview, Ctrl+F12 to render the animation.")


main()
