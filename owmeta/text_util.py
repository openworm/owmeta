import shutil

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


def format_table(dat, header=None, pref_widths=None, default_termwidth=400):
    dat = list(dat)
    if not dat:
        return ''

    ncols = len(dat[0])

    widths = None
    if header:
        if ncols != len(header):
            raise Exception('Width of header, {}, does not'
                            ' match width of data, {}'.format(len(header), ncols))

        widths = tuple(_max_width(d) for d in header)

    for row in dat:
        if len(row) != ncols:
            raise Exception('Row widths are not consistent.'
                            ' Expected {}, but found row width of {}'.format(ncols, len(row)))
        these_widths = (_max_width(d) for d in row)
        if widths is None:
            widths = tuple(these_widths)
        else:
            widths = tuple(max(v) for v in zip(widths, these_widths))

    if pref_widths:
        if ncols != len(pref_widths):
            raise Exception('Width of adjustment preferences,'
                            ' {},  does not match width of data, {}'.format(len(pref_widths), ncols))

        pref_widths = list(pref_widths)
    else:
        max_col_width = max(widths)
        pref_widths = list(x / max_col_width for x in widths)

    try:
        termwidth, _ = shutil.get_terminal_size((default_termwidth, 0))
    except AttributeError:
        termwidth = default_termwidth

    prefsorted_widths = sorted(zip(pref_widths, range(ncols)), key=lambda x: x[0])
    new_widths = list(widths)
    idx = 0
    while sum(new_widths) + ncols - 1 >= termwidth:
        selection = max(prefsorted_widths, key=lambda x: new_widths[x[1]] * x[0])
        new_widths[selection[1]] -= 1

    widths = new_widths

    fmt = ' '.join('{:' + str(w) + '}' for w in widths)

    lines = []
    for row in dat:
        row_strings = list(zip_longest(*(format(f).split('\n') for f, wdth in zip(row, widths)),
                                   fillvalue=''))
        for m in row_strings:
            lines.append(fmt.format(*(it[:wdth] for it, wdth in zip(m, widths))))

    if header:
        w = max(len(m) for m in lines)
        lines.insert(0, '-' * w)
        lines.insert(0, fmt.format(*(format(f)[:wdth] for f, wdth in zip(header, widths))))

    return '\n'.join(lines)


def _max_width(s):
    return max(len(line) for line in str(s).split('\n'))
