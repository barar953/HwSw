import json
import my_json_dumps as myjson

def check_outputs(obj):
    print("=== Input Object ===")
    print(obj)
    print()

    # Baseline: stdlib json.dumps
    baseline_out = json.dumps(obj, ensure_ascii=True)
    print("[Baseline]")
    print(baseline_out)

    # Optimized: your dumps_optimized
    optimized_out = myjson.dumps_optimized(obj)
    print("[Optimized]")
    print(optimized_out)

    # Fast: your dumps_fast (orjson/ujson if available, else fallback)
    fast_out = myjson.dumps_fast(obj)
    print("[Fast]")
    print(fast_out)


if __name__ == "__main__":
    # Example test data
    test_data = {
        "test": True,
        "number": 1234567.234,
        "array": [1, 2, 3,     6],
        "nested": {"key": "value", "unicode": "\u0105\u0107\u017c"}
    }

    check_outputs(test_data)
