"""
Custom pickle benchmark based on pyperformance implementation.
This benchmark tests the performance of pickling/unpickling using our custom my_pickle.py module.

This will pickle/unpickle several real world-representative objects a few
thousand times. The methodology below was chosen to be similar to real-world 
scenarios which operate on single objects at a time.

Based on pyperformance bm_pickle implementation.
"""

import datetime
import random
import sys
from pathlib import Path

# Import our custom pickle implementation
# Comment/uncomment these lines to switch between original and custom pickle
# import pickle
import my_pickle as pickle

import pyperf

__author__ = "collinwinter@google.com (Collin Winter) - Modified for custom pickle benchmarking"

# Test data from pyperformance - represents real-world objects
DICT = {
    'ads_flags': 0,
    'age': 18,
    'birthday': datetime.date(1980, 5, 7),
    'bulletin_count': 0,
    'comment_count': 0,
    'country': 'BR',
    'encrypted_id': 'G9urXXAJwjE',
    'favorite_count': 9,
    'first_name': '',
    'flags': 412317970704,
    'friend_count': 0,
    'gender': 'm',
    'gender_for_display': 'Male',
    'id': 302935349,
    'is_custom_profile_icon': 0,
    'last_name': '',
    'locale_preference': 'pt_BR',
    'member': 0,
    'tags': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    'profile_foo_id': 827119638,
    'secure_encrypted_id': 'Z_xxx2dYx3t4YAdnmfgyKw',
    'session_number': 2,
    'signup_id': '201-19225-223',
    'status': 'A',
    'theme': 1,
    'time_created': 1225237014,
    'time_updated': 1233134493,
    'unread_message_count': 0,
    'user_group': '0',
    'username': 'collinwinter',
    'play_count': 9,
    'view_count': 7,
    'zip': ''
}

TUPLE = (
    [265867233, 265868503, 265252341, 265243910, 265879514,
     266219766, 266021701, 265843726, 265592821, 265246784,
     265853180, 45526486, 265463699, 265848143, 265863062,
     265392591, 265877490, 265823665, 265828884, 265753032], 60)

LIST = [[list(range(10)), list(range(10))] for _ in range(10)]

MICRO_DICT = dict((key, dict.fromkeys(range(10))) for key in range(100))

def mutate_dict(orig_dict, random_source):
    """Create variations of the dictionary for more diverse testing."""
    new_dict = dict(orig_dict)
    for key, value in new_dict.items():
        rand_val = random_source.random() * sys.maxsize
        if isinstance(value, (int, bytes, str)):
            new_dict[key] = type(value)(rand_val) if isinstance(value, (int, str)) else value
    return new_dict

# Generate test data group
random_source = random.Random(5)  # Fixed seed for reproducible results
DICT_GROUP = [mutate_dict(DICT, random_source) for _ in range(3)]

def bench_pickle(loops, pickle, options):
    """Benchmark general pickle performance (DICT, TUPLE, DICT_GROUP)."""
    range_it = range(loops)
    
    # micro-optimization: use fast local variables
    dumps = pickle.dumps
    objs = (DICT, TUPLE, DICT_GROUP)
    protocol = options.protocol
    t0 = pyperf.perf_counter()

    for _ in range_it:
        for obj in objs:
            # 20 dumps per object
            for _ in range(20):
                dumps(obj, protocol)

    return pyperf.perf_counter() - t0

def bench_unpickle(loops, pickle, options):
    """Benchmark general unpickle performance."""
    pickled_dict = pickle.dumps(DICT, options.protocol)
    pickled_tuple = pickle.dumps(TUPLE, options.protocol)
    pickled_dict_group = pickle.dumps(DICT_GROUP, options.protocol)
    range_it = range(loops)

    # micro-optimization: use fast local variables
    loads = pickle.loads
    objs = (pickled_dict, pickled_tuple, pickled_dict_group)

    t0 = pyperf.perf_counter()
    for _ in range_it:
        for obj in objs:
            # 20 loads per object
            for _ in range(20):
                loads(obj)

    return pyperf.perf_counter() - t0

def bench_pickle_list(loops, pickle, options):
    """Benchmark list pickling performance."""
    range_it = range(loops)
    # micro-optimization: use fast local variables
    dumps = pickle.dumps
    obj = LIST
    protocol = options.protocol
    t0 = pyperf.perf_counter()

    for _ in range_it:
        # 10 dumps list
        for _ in range(10):
            dumps(obj, protocol)

    return pyperf.perf_counter() - t0

def bench_unpickle_list(loops, pickle, options):
    """Benchmark list unpickling performance."""
    pickled_list = pickle.dumps(LIST, options.protocol)
    range_it = range(loops)

    # micro-optimization: use fast local variables
    loads = pickle.loads
    t0 = pyperf.perf_counter()

    for _ in range_it:
        # 10 loads list
        for _ in range(10):
            loads(pickled_list)

    return pyperf.perf_counter() - t0

def bench_pickle_dict(loops, pickle, options):
    """Benchmark dictionary pickling performance."""
    range_it = range(loops)
    # micro-optimization: use fast local variables
    protocol = options.protocol
    obj = MICRO_DICT
    t0 = pyperf.perf_counter()

    for _ in range_it:
        # 5 dumps dict
        for _ in range(5):
            pickle.dumps(obj, protocol)

    return pyperf.perf_counter() - t0

# Available benchmarks with their corresponding functions and inner loop counts
BENCHMARKS = {
    'pickle': (bench_pickle, 20),           # 20 inner-loops: don't count the 3 pickled objects
    'unpickle': (bench_unpickle, 20),       # 20 inner-loops: don't count the 3 unpickled objects
    'pickle_list': (bench_pickle_list, 10),
    'unpickle_list': (bench_unpickle_list, 10),
    'pickle_dict': (bench_pickle_dict, 5),
}

def is_accelerated_module(pickle_module):
    """Check if the pickle module is using C accelerations."""
    return getattr(pickle_module.Pickler, '__module__', '<jython>') != 'pickle'

def add_cmdline_args(cmd, args):
    """Add command line arguments for benchmark configuration."""
    if args.pure_python:
        cmd.append("--pure-python")
    cmd.extend(("--protocol", str(args.protocol)))
    cmd.append(args.benchmark)

def load_custom_pickle_data():
    """Load custom pickle data file if available."""
    custom_file = '/path/to/your/pickle_data.pkl'  # CHANGE THIS PATH
    if Path(custom_file).exists():
        try:
            with open(custom_file, 'rb') as f:
                data = pickle.load(f)
            
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
            print(f"Warning: Could not load custom pickle file: {e}")
            return None, 0
    return None, 0

if __name__ == "__main__":
    runner = pyperf.Runner(add_cmdline_args=add_cmdline_args)
    runner.metadata['description'] = "Test the performance of custom pickle implementation."

    parser = runner.argparser
    parser.add_argument("--pure-python", action="store_true",
                        help="Use the pure Python version of pickle (disable C extensions).")
    parser.add_argument("--protocol", action="store", default=None, type=int,
                        help="Which pickle protocol to use (default: highest protocol).")
    
    benchmarks = sorted(BENCHMARKS)
    parser.add_argument("benchmark", nargs='?', choices=benchmarks, default='pickle_dict',
                        help="Which benchmark to run (default: pickle_dict)")

    options = runner.parse_args()
    benchmark, inner_loops = BENCHMARKS[options.benchmark]

    name = options.benchmark
    if options.pure_python:
        name += "_pure_python"

    # Handle C extensions vs pure Python
    if options.pure_python:
        # Force pure Python implementation
        sys.modules['_pickle'] = None
        # Reload our pickle module to ensure it uses pure Python
        import importlib
        try:
            importlib.reload(pickle)
        except:
            # If reload fails, reimport
            import my_pickle as pickle
        
        # Double-check by testing the Pickler class module
        pickler_module = getattr(pickle.Pickler, '__module__', 'unknown')
        if pickler_module not in ('pickle', 'my_pickle'):
            print(f"Warning: Still using C accelerated Pickler from {pickler_module}")
        else:
            print(f"Successfully using pure Python implementation from {pickler_module}")
    else:
        # Use C accelerators if available
        if not is_accelerated_module(pickle):
            print("Warning: C accelerators not available, using pure Python implementation")

    # Set protocol
    if options.protocol is None:
        options.protocol = pickle.HIGHEST_PROTOCOL
    
    # Add metadata
    runner.metadata['pickle_protocol'] = str(options.protocol)
    runner.metadata['pickle_module'] = pickle.__name__
    runner.metadata['pickle_file'] = getattr(pickle, '__file__', 'built-in')
    runner.metadata['is_accelerated'] = str(is_accelerated_module(pickle))

    print(f"Running {name} benchmark:")
    print(f"  Protocol: {options.protocol}")
    print(f"  Module: {pickle.__name__}")
    print(f"  File: {getattr(pickle, '__file__', 'built-in')}")
    print(f"  C accelerated: {is_accelerated_module(pickle)}")
    print()

    # Run the benchmark
    runner.bench_time_func(name, benchmark, pickle, options, inner_loops=inner_loops)
