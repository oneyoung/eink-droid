#!/usr/bin/env python2
import os
import sys


apk = sys.argv[-1]
apkname = os.path.splitext(os.path.basename(apk))[0]

pkgdir = os.path.dirname(os.path.abspath(__file__))
apktool = os.path.join(pkgdir, 'apktool', 'apktool')
signapk_dir = os.path.join(pkgdir, 'signapk')
output_apk = apkname + ".eInk.apk"
outdir = apkname + "-out"


# dump apk
os.system("{apktool} d -f -o {apkdir} {apk}".format(apktool=apktool,
                                                    apkdir=outdir,
                                                    apk=apk))
# handle
os.system("python2 %s/eink.py" % pkgdir)
# build again
tmp_apk = apkname + 'tmp'
os.system("{apktool} b -f -o {apk} {apkdir}".format(apktool=apktool,
                                                    apk=tmp_apk,
                                                    apkdir=outdir))
# signapk
os.system("java -jar {path}/signapk.jar {path}/certificate.pem {path}/key.pk8 \
          {in_apk} {out_apk}".format(path=signapk_dir,
                                     in_apk=tmp_apk,
                                     out_apk=output_apk))
# clean up
os.system("rm -rf " + outdir)
os.system("rm " + tmp_apk)

print ("##DONE##: " + output_apk)
