import argparse

def addVersion(parser):
    parser.add_argument('--version', action='version', version='%(prog)s 1.3')

def addInOutStat(parser, show_stat_default):
    parser.add_argument('--input-files', '-i', nargs='+',
            help='''list of input files''')
    parser.add_argument('--input-dir', '-id', default='data/',
            help='''input directory (only if --input-files are not specified)''')
    parser.add_argument('--dictionary-config', '-dc', default='configs/dictionaries.yml',
            help='''reading config location''')
    parser.add_argument('--dictionary', '-d', default='Other',
            help='''protocol/dictionary to use for file parsing and conversion''')
    parser.add_argument('--no-conversion', '-nc', action='store_true',
            help='''disable conversion of states and transitions
            into readable format (as per --dictionary-config)''')
    parser.add_argument('--view-statistics', '-vs', choices=['no', 'basic', 'full'], default=show_stat_default,
            help='''console output mode for statistical analysis of log files:
            'no' - no output;
            'basic' - only cases/events counts;
            'full' - full analysis.''')
    parser.add_argument('--save-statistics', '-ss', action='store_true',
            help='''output statistical analysis to the txt-file''')
    parser.add_argument('--output-dir', '-od', default='output/',
            help='''output directory''')

def addDrawings(parser):
    parser.add_argument('--output-format', '-of', choices=['png', 'pdf'], default=['pdf'], nargs='+',
            help='''output image format''')
    parser.add_argument('--graph-type', '-t', choices=['tgraph', 'pgraph'], default=['tgraph', 'pgraph'], nargs='+',
            help='''graph type:
            'tgraph' - Transtion Graph;
            'pgraph' - colored Path Graph''')
    parser.add_argument('--no-fake-states', '-nf', action='store_true',
            help='''disable addition of fake states ('Start' and 'End')''')
    parser.add_argument('--ignore-paths-length', '-ipl', default=1000, type=int,
            help='''for PGraphs - ignore paths longer than specified (should help if graphviz fails to handle large graph), or -1 to disable ignoring''')
    parser.add_argument('--view', '-v', action='store_true',
            help='''open the output files when finished''')
    parser.add_argument('--save-gv', '-sgv', action='store_true',
            help='''save graph source file (.gv) along with the image''')

def addRunner(parser):
    parser.add_argument('config', help='''yml-file with arguments (just strings separated with spaces or newlines)''')

def getParser(draw, stat, run):
    argparser = argparse.ArgumentParser(prog="Graph builder",
            description='Takes the logs extraction as input and builds transition/path graph or performs statistical analysis.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = argparser.add_subparsers(title="Work modes")
    parser_draw = subparsers.add_parser('draw', help='create transition/path graphs', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_stat = subparsers.add_parser('stat', help='analyze logs and output statistics', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_run = subparsers.add_parser('run', help='run %(prog)s with arguments taken from yml-file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_draw.set_defaults(func=draw)
    parser_stat.set_defaults(func=stat)
    parser_run.set_defaults(func=run)
    addVersion(argparser)
    addInOutStat(parser_draw,"basic")
    addInOutStat(parser_stat,"full")
    addDrawings(parser_draw)
    addRunner(parser_run)
    return argparser
