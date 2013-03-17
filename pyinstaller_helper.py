#!/usr/bin/env python
# coding=utf-8

from PyInstaller import makespec
import sys,os,shutil
PYINSTALLER_PATH=None
for p in sys.path:
    pp = os.path.join(p,"pyinstallerBuild")
    if os.path.isdir(pp):
        PYINSTALLER_PATH=pp
if PYINSTALLER_PATH is None:
    raise Exception("can not find pyinstaller path")

REMOVE_DIR = lambda p:os.path.isdir(p) and shutil.rmtree(p)

def pack(
        scripts        = [],
        import_base    = None,
        hiddenimports  = [],
        hookspath      = [],
        name           = None,
        out_path       = None,
        force          = True,
        datas          = []
):
    curr_path = os.getcwd()

    if out_path is None:
        out_path = curr_path

    for i in range(len(hookspath)):
        hookspath[i] = os.path.abspath(hookspath[i])

    for i in range(len(scripts)):
        scripts[i] = os.path.abspath(scripts[i])

    for i in range(len(datas)):
        datas[i] = os.path.abspath(datas[i])

    out_path    = os.path.abspath(out_path)
    import_base = os.path.abspath(import_base)

    REMOVE_DIR(os.path.join(out_path,'build'))
    REMOVE_DIR(os.path.join(out_path,'dist'))

    specfnm = makespec.main(
        scripts        = scripts,
        name           = name       ,
        onefile        = 0          ,
        console        = True       ,
        debug          = False      ,
        strip          = 0          ,
        noupx          = 0          ,
        comserver      = 0          ,
        workdir        = out_path   ,
        pathex         = [ import_base, out_path, curr_path ],
        version_file   = None       ,
        icon_file      = None       ,
        manifest       = None       ,
        resources      = []         ,
        crypt          = None       ,
        hiddenimports  = hiddenimports,
        hookspath      = hookspath
    )
    print specfnm
    __add_datas(specfnm,datas)

    sys.argv = ['myself']
    sys.argv.append(r'--buildpath="%s"' % os.path.join(out_path,'build'))
    sys.argv.append(specfnm)

    #import PyInstaller
    #import utils.Build

    builder = os.path.join(PYINSTALLER_PATH,'pyinstaller.py')
    cmd = r'python "%s" --buildpath="%s" "%s"' % (builder,os.path.join(out_path,'build'),specfnm)
    print cmd
    if os.system(cmd) == 0:
        print "== ok ======================="




def __find_spec_in_path(path):
    files = os.listdir(path)
    for f in files:
        if f.endswith('.spec'):
            return f

def __add_datas(specfnm,datas=[]):
    if len(datas) == 0:
        return
    f = open(specfnm,"r")
    contents = f.readlines()
    f.close()

    index = 0
    for i in range(len(contents)):
        if contents[i].find("pyz = PYZ")>-1:
            index = i
            break
    for data in datas:
        line = 'a.datas.append( ("%s", "%s","DATA") )\n' % (os.path.split(data)[1], data)
        contents.insert(index,line.replace('\\', r'\\'))

    f = open(specfnm,"w")
    f.writelines(contents)
    f.close()

def get_all_package_menbers(pack_name):
    hiddenimports = []
    pa = __import__(pack_name)
    base_path = os.path.dirname(pa.__file__)
    for f in os.listdir(base_path):
        if f.endswith('.py'):
            hiddenimports.append( pack_name + '.' + os.path.splitext(f)[0] )
    return hiddenimports

def get_all_py_members(pack_name):
    import vavava.util,re
    hiddenimports = []
    pa = vavava.util.importAny(pack_name)
    pa = os.path.splitext(pa.__file__)[0]
    f = open(pa+'.py','rb')
    con = f.read().decode('utf-8')
    reg_str = '^def\s*(.*?)\('
    m = vavava.util.reg_helper( con, reg_str, re.M|re.I|re.VERBOSE )
    if m:
        for mm in m:
            hiddenimports.append( pack_name + "." + mm )
    reg_str = '^class\s*([^\(|:]*?)(\(|:)'
    m = vavava.util.reg_helper( con, reg_str, re.M|re.I|re.VERBOSE )
    if m:
        for mm in m:
            hiddenimports.append( pack_name + "." + mm[0] )
    return hiddenimports

def query_package(pa):
    clses = []
    members = get_all_package_menbers(pa)
    for member in members:
        clses.append(member)
        tmp = get_all_py_members(member)
        for cls in tmp:
            clses.append( pa+"."+member+"."+cls )
    return clses

def copyPyFiles(sourceDir, targetDir):
    sourceDir = os.path.abspath(sourceDir)
    targetDir = os.path.abspath(targetDir)
    print "copy:\n%s\n%s" % (sourceDir,targetDir)
    dirs = os.listdir(sourceDir)
    for f in dirs:
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isdir(sourceF):
            copyPyFiles(sourceF, targetF)
        elif os.path.isfile(sourceF):
            if not f.endswith('.py') and not f.endswith('.pyc'):
                continue
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            open(targetF, "wb").write(open(sourceF, "rb").read())

"""
import vavava.util
kk = get_all_py_menbers(vavava.util)
for k in kk:
    print k

    build.main(
        specfile   = specfnm,
        buildpath  = out_path,
        noconfirm  = True,
        ascii=False
    )

    #pyi        = os.path.join(PYINSTALLER_PATH,'pyinstaller.py')
    #spec_file = __find_spec_in_path(out_path)
    #if force and spec_file:
    #    script_file = os.path.join(out_path,spec_file)

    #os.chdir(out_path)

    cmd = 'python "%s" --out="%s" --additional-hooks-dir="%s" --name="%s" --paths="%s" "%s"' \
          % (pyi,out_path,hooks_path,name,import_base,script_file)
    print cmd
    if os.system(cmd) == 0:
        print "== ok ======================="
"""

def  u_decode( value ):
    value = value.replace("\u0000", "" )
    value = value.replace("\u0001", "" )
    value = value.replace("\u0002", "" )
    value = value.replace("\u0003", "" )
    value = value.replace("\u0004", "" )
    value = value.replace("\u0005", "" )
    value = value.replace("\u0006", "" )
    value = value.replace("\u0007", "" )
    value = value.replace("\u0008", "" )
    value = value.replace("\u0009", "" )
    value = value.replace("\n", "" )
    value = value.replace("\u000B", "" )
    value = value.replace("\u000C", "" )
    value = value.replace("\r", "" )
    value = value.replace("\u000E", "" )
    value = value.replace("\u000F", "" )
    value = value.replace("\u0010", "" )
    value = value.replace("\u0011", "" )
    value = value.replace("\u0012", "" )
    value = value.replace("\u0013", "" )
    value = value.replace("\u0014", "" )
    value = value.replace("\u0015", "" )
    value = value.replace("\u0016", "" )
    value = value.replace("\u0017", "" )
    value = value.replace("\u0018", "" )
    value = value.replace("\u0019", "" )
    value = value.replace("\u001A", "" )
    value = value.replace("\u001B", "" )
    value = value.replace("\u001C", "" )
    value = value.replace("\u001D", "" )
    value = value.replace("\u001E", "" )
    value = value.replace("\u001F", "" )
    return value;
















