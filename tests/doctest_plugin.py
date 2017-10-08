# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import doctest


ALLOW_UNICODE = doctest.register_optionflag('ALLOW_UNICODE')
_doctestOutputChecker = doctest.OutputChecker

class UnicodeOutputChecker(doctest.OutputChecker):
    _literal_re = re.compile(r"(\W|^)[uU]([rR]?[\'\"])", re.UNICODE)

    def _remove_u_prefixes(self, txt):
        return re.sub(self._literal_re, r'\1\2', txt)

    def check_output(self, want, got, optionflags):
        res = _doctestOutputChecker.check_output(self, want, got, optionflags)
        if res:
            return True
        if not (optionflags & ALLOW_UNICODE):
            return False

        # ALLOW_UNICODE is active and want != got
        cleaned_want = self._remove_u_prefixes(want)
        cleaned_got = self._remove_u_prefixes(got)
        res = _doctestOutputChecker.check_output(self, cleaned_want, cleaned_got, optionflags)
        return res
