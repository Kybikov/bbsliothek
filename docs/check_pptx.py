import zipfile, re, sys

pptx = sys.argv[1]
with zipfile.ZipFile(pptx) as z:
    import re as re2
    slides = sorted([n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
                    key=lambda x: int(re2.search(r"slide(\d+)", x).group(1)))
    for i, name in enumerate(slides, 1):
        xml = z.read(name).decode("utf-8")
        texts = re.findall(r"<a:t>([^<]*)</a:t>", xml)
        print(f"=== Slide {i} ===")
        joined = " | ".join(t for t in texts if t.strip())
        print(joined[:400])
        print()
