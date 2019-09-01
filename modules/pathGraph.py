import colorsys
from graphviz import Digraph

def buildPaths(eventLog):
    print("Building unique paths")
    uniquePaths = {}  # {((state1, condition, state2), ... ): count, color}
    for case in eventLog:
        prevState = None
        tmpPath = []
        for record in eventLog[case]:
            if prevState != None:  # all but 1st state
                tmpPath.append((prevState, record[2], record[1]))
            prevState = record[1]
        fullPath = tuple(tmpPath)
        if fullPath not in uniquePaths:
            uniquePaths[fullPath] = [1, 0]
        else:
            uniquePaths[fullPath][0] += 1
    assignColors(uniquePaths)
    return uniquePaths

def assignColors(uniquePaths):
    print("Assigining colors to each path")
    colors = []
    colorsCount = len(uniquePaths)
    step = 1./colorsCount
    for i in range(colorsCount):
        hue = i * step
        l = 0.5
        s = 0.5
        r,g,b = colorsys.hls_to_rgb(hue,l,s)
        ri = round(r * 255)
        gi = round(g * 255)
        bi = round(b * 255)
        color = 256*256*ri + 256*gi + bi
        colors.append([color,hue])
    colors_iter = iter(colors)
    for path in sorted(uniquePaths):
        uniquePaths[path][1] = next(colors_iter)[0]
    return None

col1="#e85a71"  # red
col2="#454552"  # blueish dark-gray
col3="#FFFFFF"  # white
col4="#f6f6e9"  # yellowish light-gray
col5="#929292"  # gray
col6="#424242"  # dark-gray

def drawGraph(uniquePaths, fakeStartEnd, outputFileName, longKeysLength):
    print("Building graph")
    f = Digraph('finite_state_machine', filename=outputFileName)
    f.attr(rankdir='LR')
    if fakeStartEnd:
        f.attr('node', shape='circle', width='0.6', margin='0', color=col1, style='filled', fillcolor=col1, fontsize='10', fontcolor=col3, fontname='Helvetica bold')
        f.node('START')
        f.attr('node', shape='circle', width='0.6', margin='0', color=col2, style='filled', fillcolor=col2, fontsize='10', fontcolor=col3, fontname='Helvetica bold')
        f.node('END')
    f.attr('node', shape='ellipse', width='0.6', margin='0.1', color=col5, style='filled', fillcolor=col4, fontsize='11', fontcolor=col6)
    limit = longKeysLength
    if fakeStartEnd and limit>0:
        limit += 2
    skippedCount = 0
    for path in sorted(uniquePaths):
        f.attr('edge', color="#{:06x}".format(uniquePaths[path][1]), fontsize='10', fontname='Helvetica italic', fontcolor=col6)
        if len(path)>limit and limit>0:
            skippedCount += 1
            continue
        for st1, cond, st2 in path:
            f.edge(st1, st2, label="{0}({1})".format(cond, uniquePaths[path][0]))
    print("Skipped {} keys".format(skippedCount))
    return f

def buildGraph(eventLog, fakeStartEnd, outputFileName, outFormats, view, longPathsLength, cleanup):
    print("===PathGraph===")
    paths = buildPaths(eventLog)
    graph = drawGraph(paths, fakeStartEnd, outputFileName, longPathsLength)
    for outFormat in outFormats:
        try:
            graph.render(filename=outputFileName, view=view, cleanup=cleanup, format=outFormat)
        except Exception as e:
            err = "Error while graph rendering. If caused by edge length limit (65535) try excluding some paths using --ignore-paths-length (-ipl) argument."
            raise RuntimeError(err) from e
    return None
