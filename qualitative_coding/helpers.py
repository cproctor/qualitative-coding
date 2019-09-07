
def merge_ranges(ranges, clamp=None):
    "Overlapping ranges? Let's fix that. Optionally supply clamp=[0, 100]"
    if any(filter(lambda r: r.step != 1, ranges)): raise ValueError("Ranges must have step=1")
    endpoints = [(r.start, r.stop) for r in sorted(ranges, key=lambda r: r.start)]
    results = []
    if any(endpoints):
        a, b = endpoints[0]
        for start, stop in endpoints:
            if start <= b:
                b = max(b, stop)
            else:
                results.append(range(a, b))
                a, b = start, stop
        results.append(range(a, b))
    if clamp is not None:
        lo, hi = clamp
        results = [range(max(lo, r.start), min(hi, r.stop)) for r in results]
    return results

