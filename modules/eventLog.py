import csv
import yaml
from itertools import groupby, count
from collections import defaultdict
import statistics

def convertValue(valuesForConversion, value):
    if value in valuesForConversion:
        return valuesForConversion[value]
    else:
        return value

def getEventLogFromCsv(input_file, dictConfig, dict, useConversion):
    print("===EventLog===")
    eventLog = {}  # {EntityID: [[time, state, transition], ...]}
    print("Reading dictionaries config file: {}".format(dictConfig))
    with open(dictConfig, "r") as stream:
        config = yaml.safe_load(stream)
        entity_field = config[dict]["fields"]["EntityID"]
        state_field = config[dict]["fields"]["State"]
        transition_field = config[dict]["fields"]["Transition"]
        seqnumber_field = config[dict]["fields"]["SeqNumber"]
        statesForConversion = config[dict]["values"][state_field]
        transitionsForConversion = config[dict]["values"][transition_field]

    print("Reading the file data and storing states and transitions for each entity")
    with open(input_file, newline="\n") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            entity = row[entity_field]
            if useConversion:
                transition = [int(row[seqnumber_field]), convertValue(statesForConversion, row[state_field]), convertValue(transitionsForConversion, row[transition_field])]
            else:
                transition = [int(row[seqnumber_field]), row[state_field], row[transition_field]]
            if entity not in eventLog:
                eventLog[entity] = [transition]
            else:
                eventLog[entity].append(transition)
    for entity in eventLog:
        eventLog[entity].sort(key=lambda x: x[0])
    return eventLog

def addFakeStartEnd(eventLog):
    print("Adding fake START and END points for each entity transitions")
    for entity in eventLog:
        eventLog[entity].insert(0, [0, "START", ""])
        eventLog[entity].append([0, "END", ""])
    return None

def analyzeEventLog(eventLog, show, save, outputFileName):
    NoCases = len(eventLog)
    NoEvents = 0
    stat=[]
    for case in eventLog:
        NoEvents += len(eventLog[case])
    if show=="full" or save:
        UniqueEvents = defaultdict(lambda: [0,0,0,0])  # {(transition,state):[eventCount,caseCount,startCaseCount,endCaseCount]}
        UniqueStates = defaultdict(lambda: [0,0,0,0])  # {state:[eventCount,caseCount,startCaseCount,endCaseCount]}
        UniquePaths = defaultdict(lambda: 0)  # {(transition,state):(count,path_str)}
        EventsPerCase = defaultdict(lambda: 0)  # {EventsPerCase : NoCases}
        for case in eventLog:
            casePath = []  # [(transition,state)]
            for _, state, transition in eventLog[case]:
                UniqueEvents[(transition, state)][0] += 1
                UniqueStates[state][0] += 1
                if (transition, state) not in casePath:
                    UniqueEvents[(transition, state)][1] += 1  # check once for the case
                if state not in (st for (tr, st) in casePath):
                    UniqueStates[state][1] += 1  # check once for the case
                casePath.append((transition, state))
            _, state, transition = eventLog[case][0]  # 1st event/state
            UniqueEvents[(transition, state)][2] += 1
            UniqueStates[state][2] += 1
            _, state, transition = eventLog[case][-1]  # last event/state
            UniqueEvents[(transition, state)][3] += 1
            UniqueStates[state][3] += 1
            UniquePaths[tuple(casePath)] += 1
        for path in UniquePaths:
            EventsPerCase[len(path)] += UniquePaths[path]

        fullevents=[]  # list of numbers of events, e.g. [1,1,1,2,2,3,4,4,...]
        for a in EventsPerCase:
            fullevents.extend([a]*EventsPerCase[a])

        # Grouping for EventsPerCase
        pathLengths = len(EventsPerCase)  # number of unique path lengths
        numberOfGroups = 13  # excluding 1st and last (as they are not being grouped)
        groupSize = pathLengths // numberOfGroups + (pathLengths % numberOfGroups > 0)  # groupsize=roundup(path_lengths/numberOfGroups)
        groups = []
        groups.append([str(min(EventsPerCase)),EventsPerCase[min(EventsPerCase)]]) # min value (not grouped)
        for _, grpLvl1 in groupby(sorted(EventsPerCase)[1:-1], lambda x, c=count(): next(c) // groupSize):  # Mid lengths devided into 8 groups
            subgrps = []  # sub-groups list for each group
            val = 0  # accumulated value for each group
            for _, grpLvl2 in groupby(grpLvl1, lambda x, c=count(): x-next(c)):  # Each group devided into subgroups based on consequtiveness
                grp2=list(grpLvl2)
                if len(grp2)>1:
                    subgrps.append(str(grp2[0])+'-'+str(grp2[-1]))  # Subgroup range e.g. '1-3' or '5-6'
                else:
                    subgrps.append(str(grp2[0]))  # Single element subgroup e.g. '1' or '5'
                for length in grp2:
                    val += EventsPerCase[length]  # Value accumulates
            groups.append([','.join(subgrps),val])  # Groups gather subgroups e.g. '1,2-5,7-8,10'
        groups.append([str(max(EventsPerCase)),EventsPerCase[max(EventsPerCase)]])  # max value (not grouped)

        head1="\n   {0}%s{1}\n"
        form1="{2}%30s{3}: %-10i"
        form2="{2}%30s{3}: %-10.2f"
        tabhead1='{2}%30s %12s %13s %12s %13s %12s %13s %12s %13s{3}'
        tabform1='%30s %12i %12.2f%% %12i %12.2f%% %12i %12.2f%% %12i %12.2f%%'
        tabhead2='{2}%30s  %-12s{3}'
        tabform2='%30s  %-12i'
        tabhead3='{2}%30s %13s    %-12s{3}'
        tabform3='%30i %12.2f%%    %-12s'
        stat.append(head1 % "General:")
        stat.append(form1 % ("Number of cases",NoCases))
        stat.append(form1 % ("Number of events",NoEvents))
        stat.append(head1 % "Unique events (transition+state):")
        stat.append(tabhead1 % ("Event","Occurences","Frequency","Occurences","Frequency","Start event","Start event","End event","End event"))
        stat.append(tabhead1 % ("","(in events)","(by event)","(in cases)","(by case)","cases","frequency","cases","frequency"))
        stat.extend(tabform1 % (ts[0]+"+"+ts[1],UniqueEvents[ts][0],UniqueEvents[ts][0]/NoEvents*100,UniqueEvents[ts][1],UniqueEvents[ts][1]/NoCases*100,
            UniqueEvents[ts][2],UniqueEvents[ts][2]/NoCases*100,UniqueEvents[ts][3],UniqueEvents[ts][3]/NoCases*100)
            for ts in sorted(UniqueEvents, key=lambda x: UniqueEvents[x][0], reverse=True))
        stat.append(head1 % "Unique states:")
        stat.append(tabhead1 % ("State","Occurences","Frequency","Occurences","Frequency","Start event","Start event","End event","End event"))
        stat.append(tabhead1 % ("","(in events)","(by event)","(in cases)","(by case)","cases","frequency","cases","frequency"))
        stat.extend(tabform1 % (s,UniqueStates[s][0],UniqueStates[s][0]/NoEvents*100,UniqueStates[s][1],UniqueStates[s][1]/NoCases*100,
            UniqueStates[s][2],UniqueStates[s][2]/NoCases*100,UniqueStates[s][3],UniqueStates[s][3]/NoCases*100)
            for s in sorted(UniqueStates, key=lambda x: UniqueStates[x][0], reverse=True))
        stat.append(head1 % "Events per case:")
        stat.append(tabhead2 % ("Events per case","Cases"))
        stat.extend(tabform2 % (e,c) for e,c in groups)
        stat.append("")
        stat.append(form1 % ("Minimum",min(fullevents)))
        stat.append(form1 % ("Mode",statistics.mode(fullevents)))
        stat.append(form2 % ("Median",statistics.median(fullevents)))
        stat.append(form2 % ("Mean",statistics.mean(fullevents)))
        stat.append(form1 % ("Maximum",max(fullevents)))
        stat.append(head1 % "Top 5 most frequent paths:")
        stat.append(tabhead3 % ("Number of cases","Frequency","Path"))
        stat.extend(tabform3 % (UniquePaths[p],UniquePaths[p]/NoCases*100,'-'.join('('+tr+')-' + st for tr,st in p))
            for p in sorted(UniquePaths, key=lambda x: UniquePaths[x], reverse=True)[:5])
        stat.append("")

    if show=="basic":
        print("===Statistics===")
        print("Number of cases: ",NoCases)
        print("Number of events: ",NoEvents)
    elif show=="full":
        print("===Statistics===")
        for str1 in stat:
            print(str1.format('\033[1m\033[4m','\033[0m','\033[1m','\033[0m'))

    if save:
        with open (outputFileName,'w') as file:
            for str1 in stat:
                file.write(str1.format('','','','')+"\n")

    return None
