import os


def drawGraph(
    automata,
    file="",
):
    """From https://github.com/max99x/automata-editor/blob/master/util.py"""
    f = os.popen(r"dot -Tpng -o graph%s.png" % file, 'w')
    try:
        f.write(automata.getDotFile())
    except:
        raise BaseException("Error creating graph")
    finally:
        f.close()


def isInstalled(program):
    """From http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python"""
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program) or is_exe(program + ".exe"):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file) or is_exe(exe_file + ".exe"):
                return True
    return False