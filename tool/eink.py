import os
from xml.dom.minidom import parse


def handle_xml(fpath):
    try:
        with open(fpath) as fp:
            xml = parse(fp)
    except:
        print "parse xml fail: ", fpath
        return

    handle_node(xml)

    # save file
    fp = open(fpath, 'w')
    buf = xml.toxml()
    fp.write(buf.encode("utf-8"))
    fp.close()


def handle_node(node):
    def set_attr(o, name, val, filter_func=None):
        if o.hasAttribute(name):
            if filter_func:
                old_val = o.getAttribute(name)
                if not filter_func(old_val):
                    return
            o.setAttribute(name, val)

    if hasattr(node, 'hasAttribute'):
        set_attr(node, 'android:textColor', '#ff000000')
        set_attr(node, 'android:background', '#ffffffff',
                 lambda s: s.startswith("#"))

    if node.nodeName == 'color':
        child = node.childNodes[0]
        val = child.nodeValue
        if val.startswith('#'):
            rest = val[1:]
            values = []
            for _ in range(4):
                hexval = int(rest[:2], 16)
                values.append(hexval)
                rest = rest[2:]
            a, r, g, b = values
            grey = (r + g + b)/3
            if grey > 255/4*3:  # blank
                color = 'ffffff'
            else:
                color = '000000'
            if a > 0:
                alpha = 'ff'
            else:
                alpha = '00'
            new_val = '#' + alpha + color
            child.nodeValue = new_val

    for c in node.childNodes:
        handle_node(c)


# first find the all xml files
cmd = "find -name '*.xml'"
p = os.popen(cmd)
files = p.read().splitlines()
for f in files:
    handle_xml(f)
