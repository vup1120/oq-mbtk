import os
import re
import shutil
from pathlib import Path


def create_folder(folder: str, clean: bool = False):
    """
    Create a folder. If the folder exists, it's possible to
    clean it.

    :param folder:
        The name of the folder tp be created
    :param clean:
        When true the function removes the content of the folder
    """
    if os.path.exists(folder):
        if clean:
            shutil.rmtree(folder)
    else:
        Path(folder).mkdir(parents=True, exist_ok=True)


def _get_src_id(fpath: str) -> str:
    """
    Returns the ID of the source included in a string with the
    format `whatever_<source_id>.csv`

    :param fpath:
        The string containign the source ID
    :returns:
        The source ID
    """
    fname = os.path.basename(fpath)
    if '_' in fname:
        pattern = '.*_+(\\S*)\\..*'
        #pattern = '.*[_|\\.]([\\w|-]*)\\.'
    else:
        pattern = '(\\S*)\\..*'
    mtch = re.search(pattern, fname)


    try:
        return mtch.group(1)
    except:
        fmt = 'Name {:s} does not comply with standards'
        raise ValueError(fmt.format(fname))


def get_list(tmps, sep=','):
    """
    Given a string of elements separated by a `separator` returns a list of
    elements.

    :param tmps:
        The string to be parsed
    :param sep:
        The separator character
    """
    tml = re.split('\\{:s}'.format(sep), tmps)
    # Cleaning
    tml = [re.sub('(^\\s*|\\s^)', '', a) for a in tml]
    return tml
