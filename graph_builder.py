import re
import yaml
import time
from os import listdir
from os.path import join, isfile
from modules.CLargs import getParser
from modules.eventLog import getEventLogFromCsv, addFakeStartEnd, analyzeEventLog
from modules.transitionGraph import buildGraph as buildTGraph
from modules.pathGraph import buildGraph as buildPGraph

# Get source files for Draw and Stat modes
def getFiles(args):
    if args["input_files"] is not None:
        return args["input_files"]
    else:
        return [join(args["input_dir"], f) for f in listdir(args["input_dir"]) if isfile(join(args["input_dir"], f))]

# Draw mode
def draw(args):
    for inputFileName in getFiles(args):
        fileStartTime = time.time()
        print("Processing file: {}".format(inputFileName))
        fileName = re.sub(r'.*/', '', inputFileName)
        fileName = re.sub(r'\..*', '', fileName)
        outputFileName = join(args["output_dir"], fileName)
        log = getEventLogFromCsv(inputFileName, dictConfig = args["dictionary_config"],
                        dict=args["dictionary"], useConversion=not args["no_conversion"])
        print("EventLog parsing time for {}: {} {}".format(inputFileName, str(round(time.time()-fileStartTime, 2)), "s"))
        analyzeEventLog(log, show=args["view_statistics"], save=args["save_statistics"], outputFileName=outputFileName+"-stat.txt")
        addFakeStartEnd(log)
        if 'tgraph' in args["graph_type"]:
            buildTGraph(log, fakeStartEnd=not args["no_fake_states"],
                    outputFileName=outputFileName+"-TGraph.gv", outFormats=args["output_format"],
                    view=args["view"], cleanup=not args["save_gv"])
        if 'pgraph' in args["graph_type"]:
            buildPGraph(log, fakeStartEnd=not args["no_fake_states"],
                    outputFileName=outputFileName+"-PGraph.gv", outFormats=args["output_format"],
                    view=args["view"], cleanup=not args["save_gv"],
                    longPathsLength=args["ignore_paths_length"])
        print("Execution time for {}: {} {}".format(inputFileName, str(round(time.time()-fileStartTime, 2)), "s\n"))
    return None

# Stat mode
def stat(args):
    for inputFileName in getFiles(args):
        fileStartTime = time.time()
        print("Processing file: {}".format(inputFileName))
        fileName = re.sub(r'.*/', '', inputFileName)
        fileName = re.sub(r'\..*', '', fileName)
        outputFileName = join(args["output_dir"], fileName)
        log = getEventLogFromCsv(inputFileName, dictConfig = args["dictionary_config"],
                        dict=args["dictionary"], useConversion=not args["no_conversion"])
        print("EventLog parsing time for {}: {} {}".format(inputFileName, str(round(time.time()-fileStartTime, 2)), "s"))
        analyzeEventLog(log, show=args["view_statistics"], save=args["save_statistics"], outputFileName=outputFileName+"-stat.txt")
        print("Execution time for {}: {} {}".format(inputFileName, str(round(time.time()-fileStartTime, 2)), "s\n"))
    return None

# Run mode
def run(args):
    with open(args["config"], "r") as stream:
        config = yaml.safe_load(stream)
    fileargs = parser.parse_args(config.split())
    fileargs.func(vars(fileargs))

# Main code here
parser = getParser(draw=draw, stat=stat, run=run)
arguments = parser.parse_args()
startTime = time.time()
arguments.func(vars(arguments))  # Call mode function (e.g. draw)
print("Overall execution time: {} {}".format(str(round(time.time()-startTime, 2)), "s"))
