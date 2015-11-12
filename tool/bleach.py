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
        apply to all attrs
        '''
        # apply to all attrs
        if node.attributes:
            for k in node.attributes.keys():
                val = node.getAttribute(k)
                if self._is_rgb(val):
                    node.setAttribute(k, self._rgb2wb(val))

    def _m_val(self, node):
        '''
        apply to all nodeValue
        '''
        val = node.nodeValue
        if val and self._is_rgb(val):
            node.nodeValue = self._rgb2wb(val)

    def _is_rgb(self, val):
        if not val:
            return False
        if val.startswith('#') and len(val) == 9:
            hexs = val[1:].lower()
            s = '0123456789abcdef'
            return all([c in s for c in hexs])
        return False

    def _rgb2wb(self, val):
        '''
        convert #aarrggbb to black/white
        '''
        rest = val[1:]
        values = []
        for _ in range(4):
            hexval = int(rest[:2], 16)
            values.append(hexval)
            rest = rest[2:]
        a, r, g, b = values
        grey = int(0.299*r + 0.587*g + 0.144*b)
        # we use 4 level mapping
        N = 4
        base = 0x100/N
        level = grey/base + (1 if grey > 0x7f else 0)
        c_value = level*base
        if c_value > 0xff:
            c_value = 0xff
        color = ('%.2x' % (c_value)) * 3

        if a > 0x80:
            alpha = 'ff'
        else:
            alpha = '%.2x' % a
        new_val = '#' + alpha + color
        return new_val

    def _m_anima(self, node):
        '''
        modify animation node
        '''
        tags = ['alpha', 'scale', 'translate', 'rotate']
        if node.nodeName in tags:
            node.setAttribute('android:duration', '10')
            # now we set fromXXX equals toXXX
            attrs = node.attributes.keys()
            # check if it need to go back to init state
            back = False
            for attr in ['android:fillBefore', 'android:fillEnable']:
                if attr in attrs:
                    val = node.getAttribute(attr)
                    if val == 'true':
                        back = True
            for attr in attrs:
                if attr.startswith('android:from'):
                    from_attr = attr
                    what = attr[len('android:from')]
                    to_attr = 'android:to' + what
                    if to_attr in attrs:  # 'from' and 'to' exists
                        from_val = node.getAttribute(from_attr)
                        to_val = node.getAttribute(to_attr)
                        if back:  # 'to' <= 'from'
                            node.setAttribute(to_attr, from_val)
                        else:
                            node.setAttribute(from_attr, to_val)

    def handle_node(self, node):
        # first apply for methods starts with '_m_'
        try:
            for attr in dir(self):
                if attr.startswith('_m_'):
                    func = getattr(self, attr)
                    func(node)
        except Exception, e:
            print "node failed: ", node.toxml()
            print str(e)

        for c in node.childNodes:
            self.handle_node(c)
