"""Package accepted image slides; replace prompt notes with the approved lecture text."""
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image

HERE = Path(__file__).resolve().parent
DECK = HERE / 'slide-deck/evidence-first'
OUT = HERE / 'materials'
slides = json.loads((DECK/'slides.json').read_text())
images = [Image.open(DECK/s['image']).convert('RGB') for s in slides]
images[0].save(OUT/'lesson-01.pdf',save_all=True,append_images=images[1:],resolution=144)
for im in images:
    im.close()
script = (HERE/'SCRIPT.md').read_text()
segments = re.split(r'^## ',script,flags=re.M)[1:]
# Slide 04/05 share one script segment; slides 08/09 share another.
anchors = [0,1,2,3,3,4,5,6,6,7]
ns = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for prefix,uri in ns.items():
    ET.register_namespace(prefix,uri)
path = OUT/'lesson-01.pptx'
with zipfile.ZipFile(path) as z:
    entries = [(item,z.read(item.filename)) for item in z.infolist()]
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
    for item,content in entries:
        match = re.fullmatch(r'ppt/notesSlides/notesSlide(\d+)\.xml',item.filename)
        if match:
            index = int(match.group(1))-1
            tree = ET.fromstring(content)
            for shape in tree.findall('.//p:sp',ns):
                ph = shape.find('.//p:ph',ns)
                if ph is None or ph.get('type')!='body':
                    continue
                body = shape.find('p:txBody',ns)
                for para in list(body.findall('a:p',ns)):
                    body.remove(para)
                text = f"时间锚点：{slides[index]['timing']}。\n{segments[anchors[index]]}\n"
                if index==9:
                    text += '\n'+segments[8]
                text += '\n资料：data/notes.json；evidence/minimax-live-2026-10-17-batch.json及batch-initial.json。真实回放不是本次现场调用。图内文字为教学摘要，完整原文在回放页。'
                for line in text.splitlines():
                    para = ET.SubElement(body,'{'+ns['a']+'}p')
                    run = ET.SubElement(para,'{'+ns['a']+'}r')
                    ET.SubElement(run,'{'+ns['a']+'}t').text = line
            content = ET.tostring(tree,encoding='utf-8',xml_declaration=True)
        z.writestr(item,content)
print('Packaged 10-page image PDF; PPTX notes now contain lecture text, not generation prompts')
