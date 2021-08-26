
# Helper methods
def get_longest_key(dictionary):
    return max(map(len, dictionary))


def first(dictionary):
    return next(iter(dictionary))


def to_choices(dictionary):
    return list(dictionary.items())


# TODO ensure extensions are checked case insensitive
LANGUAGES = {
    # CODE : (Name, moss_name, [extensions])

    'PY': ('Python', 'python', ['py']),  # pyi, pyc, pyd, pyo, pyw, pyz
    'JA': ('Java', 'java', ['java']),  # class, jar
    'CP': ('C++', 'cc', ['C', 'cc', 'cpp', 'cxx', 'c++', 'h', 'H', 'hh', 'hpp', 'hxx', 'h++']),
    'CX': ('C', 'c', ['c', 'h']),
    'CS': ('C#', 'csharp', ['cs', 'csx']),
    'JS': ('Javascript', 'javascript', ['js']),  # cjs, mjs
    'PL': ('Perl', 'perl', ['pl', 'plx', 'pm', 'xs', 't', 'pod']),
    'MP': ('MIPS assembly', 'mips', ['asm', 's']),

    # TODO decide which to add, and add extensions
    # 'LP' : ('Lisp', 'lisp', []),
    # 'HS' : ('Haskell', 'haskell', []),
    # 'VB' : ('Visual Basic', 'vb', []),
    # 'MB' : ('Matlab', 'matlab', []),
    # 'AA' : ('a8086 assembly', 'a8086', []),
    # 'VL' : ('Verilog', 'verilog', []),
    # 'PS' : ('Pascal', 'pascal', []),
    # 'ML' : ('ML', 'ml', []),
    # 'AD' : ('Ada', 'ada', []),
    # 'VH' : ('VHDL', 'vhdl', []),
    # 'SC' : ('Scheme', 'scheme', []),
    # 'FT' : ('FORTRAN', 'fortran', ['f', 'for', 'f90']),
    # 'SP' : ('Spice', 'spice', []),
    # 'PG' : ('Prolog', 'prolog', ['pl', 'pro', 'P']),
    # 'PS' : ('PL/SQL', 'plsql', []),
    # 'AS' : ('ASCII', 'ascii', []) # All?
}


DEFAULT_LANGUAGE = first(LANGUAGES)
VIEWABLE_LANGUAGES = {LANGUAGES[l][0]: LANGUAGES[l][2] for l in LANGUAGES}
READABLE_TO_CODE_LANGUAGES = {LANGUAGES[l][0]: l for l in LANGUAGES}

LANGUAGE_CHOICES = [(l, LANGUAGES[l][0]) for l in LANGUAGES]
MOSS_LANGUAGES = {l: LANGUAGES[l][1] for l in LANGUAGES}
VALID_EXTENSIONS = {l: LANGUAGES[l][2] for l in LANGUAGES}

SUPPORTED_MOSS_LANGUAGES = list(MOSS_LANGUAGES.values())
MAX_LANGUAGE_LENGTH = get_longest_key(LANGUAGES)

UPLOADING_STATUS = 'UPL'
PROCESSING_STATUS = 'PRO'
COMPLETED_STATUS = 'COM'
FAILED_STATUS = 'FAI'

# Other
STATUSES = {
    # 'Code': 'Name',
    UPLOADING_STATUS: 'Uploading',
    PROCESSING_STATUS: 'Processing',
    COMPLETED_STATUS: 'Complete',
    FAILED_STATUS: 'Failed'
}

STATUS_CHOICES = to_choices(STATUSES)
DEFAULT_STATUS = first(STATUSES)
MAX_STATUS_LENGTH = get_longest_key(STATUSES)

UUID_LENGTH = 32

# Default MOSS settings
DEFAULT_MOSS_LANGUAGE = LANGUAGES[DEFAULT_LANGUAGE][0]
MAX_UNTIL_IGNORED = 10
MAX_DISPLAYED_MATCHES = 250
MAX_COMMENT_LENGTH = 64

# UI Defaults
POLLING_TIME = 1000  # in milliseconds
