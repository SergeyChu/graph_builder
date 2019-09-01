from graphviz import Digraph

def buildTransitions(eventLog):
    print("Building transitions")
    transitions = {}  # {(st1,st2): {condition: count}}
    for case in eventLog:
        prevState = None
        for entState in eventLog[case]:
            if prevState != None:  # all but 1st state
                currState = entState[1]
                currCond = entState[2]
                # If no such transition record adding a new one with 1 as count
                if (prevState, currState) not in transitions:
                    transitions[(prevState, currState)] = {currCond: 1}
                # If no such condition record in transition adding a new one with 1 as count
                elif currCond not in transitions[(prevState, currState)]:
                    transitions[(prevState, currState)][currCond] = 1
                # If record for a transition and condition exists then simply increasing count for it
                else:
                    transitions[(prevState, currState)][currCond] += 1
            prevState = entState[1]
    return transitions

col1="#e85a71"  # red
col2="#454552"  # blueish dark-gray
col3="#FFFFFF"  # white
col4="#f6f6e9"  # yellowish light-gray
col5="#929292"  # gray
col6="#424242"  # dark-gray

def drawGraph(transitions, fakeStartEnd, fileName):
    print("Building graph")
    f = Digraph('finite_state_machine', filename=fileName)
    f.attr(rankdir='LR')
    if fakeStartEnd:
        f.attr('node', shape='circle', width='0.6', margin='0', color=col1, style='filled', fillcolor=col1, fontsize='10', fontcolor=col3, fontname='Helvetica bold')
        f.node('START')
        f.attr('node', shape='circle', width='0.6', margin='0', color=col2, style='filled', fillcolor=col2, fontsize='10', fontcolor=col3, fontname='Helvetica bold')
        f.node('END')
    f.attr('node', shape='ellipse', width='0.6', margin='0.1', color=col5, style='filled', fillcolor=col4, fontsize='11', fontcolor=col6)
    f.attr('edge', color=col6, fontsize='10', fontname='Helvetica italic', fontcolor=col6)
    for st1, st2 in sorted(transitions):
        for cond in transitions[(st1, st2)]:
            f.edge(st1, st2, label="{0}({1})".format(cond, transitions[(st1, st2)][cond]))
    return f

def buildGraph(eventLog, fakeStartEnd, outputFileName, outFormats, view, cleanup):
    print("===TransitionGraph===")
    transitions = buildTransitions(eventLog)
    graph = drawGraph(transitions, fakeStartEnd, outputFileName)
    for outFormat in outFormats:
        graph.render(filename=outputFileName, view=view, cleanup=cleanup, format=outFormat)
    return None
