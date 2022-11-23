from rapidfuzz import process, fuzz as rfuzz
from functools import wraps
from time import process_time

def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(process_time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(process_time() * 1000)) - start
            print(
                f"Total execution time {func.__name__}: {end_ if end_ > 0 else 0} ms"
            )

    return _time_it

# @measure
def RapidFuzz_Levenshtein(w1, w2):
    '''Use for one-to-one similaritu check'''
    # return rfuzz.partial_ratio(str(w1), str(w2))
    # return rfuzz.QRatio(str(w1), str(w2))
    return rfuzz.ratio(str(w1), str(w2),processor=False)

def RapidFuzzChoices_Levenshtein(w1, choices, n=2):
    '''Use for one-to-many similarity check'''
    result = process.extract(str(w1), choices, scorer=rfuzz.WRatio, limit=n)
    # result = process.extractOne(str(w1), choices, scorer=rfuzz.WRatio)
    return result