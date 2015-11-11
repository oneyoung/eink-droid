import os
from xml.dom.minidom import parse


class Bleach(object):
    def __init__(self, apkdir):
        self.apkdir = apkdir

    def run(self):
        # we start from res/ folder
        cmd = "find %s -name '*.xml' " % os.path.join(self.apkdir, 'res')
        p = os.popen(cmd)
        xmls = p.read().splitlines()
        for xml in xmls:
            self.handle_xml(xml)

    def handle_xml(self, fpath):
        try:
            with open(fpath) as fp:
                xml = parse(fp)
        except:
            print "parse xml fail: ", fpath
            return

        self.handle_node(xml)

        # save file
        fp = open(fpath, 'w')
        buf = xml.toxml()
        fp.write(buf.encode("utf-8"))
        fp.close()

    def _m_attr(self, node):
        '''
        modify attributes
        '''
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

    def _m_color(self, node):
        '''
        modify color node
        '''
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

    def _m_anima(self, node):
        '''
        modify animation node
        '''
        tags = ['alpha', 'scale', 'translate', 'rotate']
        if node.nodeName in tags:
            node.setAttribute('android:duration', '10')

    def handle_node(self, node):
        # first apply for methods starts with '_m_'
        for attr in dir(self):
            if attr.startswith('_m_'):
                func = getattr(self, attr)
                func(node)

        for c in node.childNodes:
            self.handle_node(c)
