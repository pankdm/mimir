
from model import *

def GetInfoAsText(god_class):
    num_total = 0
    num_marked = 0
    freq_specific_marked = dict((k, 0) for k in MarkValues)
    total_freq = 0
    total_freq_marked = 0

    for query in god_class.get_queries():
        total_freq += query.freq
        num_total += 1

        mark = god_class.get_total_mark_for_query(query.text)
        if mark != Mark.UNDEFINED:
            freq_specific_marked[mark] += query.freq
            num_marked += 1
            total_freq_marked += query.freq
    out = \
    [
        "Marked: %d (%d)" % (num_marked, num_total),
        "Freq marked: %d (%d)" % (total_freq_marked, total_freq),
    ] + [ \
        k + ": " + str(freq_specific_marked[k]) for k in MarkValues if k != Mark.UNDEFINED
    ]

    return "\n".join(out)


