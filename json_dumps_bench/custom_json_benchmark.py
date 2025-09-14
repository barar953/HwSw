import json
import my_json_dumps as myjson
import sys
from pathlib import Path

import pyperf

# Original test cases
EMPTY = ({}, 2000)
SIMPLE_DATA = {'key1': 0, 'key2': True, 'key3': 'value', 'key4': 'foo',
               'key5': 'string'}
SIMPLE = (SIMPLE_DATA, 1000)
NESTED_DATA = {'key1': 0, 'key2': SIMPLE[0], 'key3': 'value', 'key4': SIMPLE[0],
               'key5': SIMPLE[0], 'key': '\u0105\u0107\u017c'}
NESTED = (NESTED_DATA, 1000)
HUGE = ([NESTED[0]] * 1000, 1)


# Add your custom JSON file
def load_custom_json():
    """Load custom JSON file if it exists."""
    custom_file = '/path/to/your/file.json'  # CHANGE THIS PATH
    if Path(custom_file).exists():
        try:
            with open(custom_file, 'r') as f:
                data = json.load(f)

            # Estimate good iteration count based on file size
            file_size = Path(custom_file).stat().st_size
            if file_size < 10240:  # < 10KB
                iterations = 500
            elif file_size < 102400:  # < 100KB
                iterations = 100
            elif file_size < 1048576:  # < 1MB
                iterations = 10
            else:  # >= 1MB
                iterations = 1

            return data, iterations
        except Exception as e:
            print(f"Warning: Could not load custom JSON file: {e}")
            return None, 0
    return None, 0


# Load custom data
CUSTOM_DATA, CUSTOM_ITERATIONS = load_custom_json()
if CUSTOM_DATA is not None:
    CUSTOM = (CUSTOM_DATA, CUSTOM_ITERATIONS)
    CASES = ['EMPTY', 'SIMPLE', 'NESTED', 'HUGE', 'CUSTOM']
else:
    CASES = ['EMPTY', 'SIMPLE', 'NESTED', 'HUGE']


def bench_json_dumps(data):
    for obj, count_it in data:
        for _ in count_it:
            json.dumps(obj)


def add_cmdline_args(cmd, args):
    if args.cases:
        cmd.extend(("--cases", args.cases))
    if args.impl:
        cmd.extend(("--impl", args.impl))


def main():
    runner = pyperf.Runner(add_cmdline_args=add_cmdline_args)
    runner.argparser.add_argument("--cases",
                                  help="Comma separated list of cases. Available cases: %s. By default, run all cases."
                                       % ', '.join(CASES))
    runner.argparser.add_argument("--impl",
                                  choices=["baseline", "optimized", "fast"],
                                  default="baseline",
                                  help="Which implementation of json.dumps to use: baseline (stdlib), optimized, or fast")
    runner.metadata['description'] = "Benchmark json.dumps() with custom data"

    args = runner.parse_args()

    # Select implementation
    if args.impl == "optimized":
        json.dumps = myjson.dumps_optimized
    elif args.impl == "fast":
        json.dumps = myjson.dumps_fast
    else:  # baseline
        import importlib
        std_json = importlib.import_module("json")
        json.dumps = std_json.dumps

    # Select cases
    if args.cases:
        cases = []
        for case in args.cases.split(','):
            case = case.strip()
            if case:
                cases.append(case)
        if not cases:
            print("ERROR: empty list of cases")
            sys.exit(1)
    else:
        cases = CASES

    data = []
    for case in cases:
        obj, count = globals()[case]
        data.append((obj, range(count)))

    runner.bench_func('json_dumps', bench_json_dumps, data)


if __name__ == '__main__':
    main()
