from textwrap import fill

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

def prepare_corpus_text(text, width=80, preformatted=False):
    "Splits corpus text at blank lines and wraps it."
    if preformatted:
        outlines = []
        lines = text.split("\n")
        for line in lines:
            while True:
                outlines.append(line[:width])
                if len(line) < 80:
                    break
                line = line[width:]
        return "\n".join(outlines)
    else:
        paragraphs = text.split("\n\n")
        return "\n\n".join(fill(p, width=width) for p in paragraphs)

def prompt_for_choice(prompt, options):
    "Asks for a prompt, returns an index"
    print(prompt)
    for i, opt in enumerate(options):
        print(f"{i+1}. {opt}")
    while True:
        raw_choice = input("> ")
        if raw_choice.isdigit() and int(raw_choice) in range(1, len(options)+1):
            return int(raw_choice)
        print("Sorry, that's not a valid choice.")





