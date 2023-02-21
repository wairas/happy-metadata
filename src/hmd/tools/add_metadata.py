import argparse
import json
import os
import pandas as pd
import traceback

from hmd import GLOBAL_EXT, HappyMetaData
from simple_range import index_value, range_indices, FIRST, ALL


def add(path, metadata, recursive, indent=2):
    """
    Adds meta-data from a panda dataframe to (global) Happy meta-data JSON files.

    :param path: the path with the meta-data files to extend
    :type path: str
    :param metadata: the dictionary with the metadata, the sample ID the key
    :type metadata: dict
    :param recursive: whether to look for JSON files recursively
    :type recursive: bool
    :param indent: the indentation to use for pretty-printing, None turns off pretty-printing
    :type indent: int
    """
    print("Dir: %s" % path)
    for f in os.listdir(path):
        if (f == ".") or (f == ".."):
            continue
        full = os.path.join(path, f)
        if recursive and os.path.isdir(full):
            add(full, metadata, recursive, indent=indent)
        if not f.endswith(GLOBAL_EXT):
            continue

        h = HappyMetaData.load(full)
        if h.sample_id in metadata:
            for k in metadata[h.sample_id]:
                h.set(k, metadata[h.sample_id][k])
            h.save_global(full, indent=indent)
            print("- %s: updated" % f)
        else:
            print("- %s: no meta-data" % f)


def process(path, spreadsheet, sample_id=FIRST, meta_data=ALL, recursive=True, indent=2):
    """
    Adds meta-data from a spreadsheet to (global) Happy meta-data JSON files.

    :param path: the path with the meta-data files to extend
    :type path: str
    :param spreadsheet: the spreadsheet file with the meta-data to add
    :type spreadsheet: str
    :param sample_id: the spreadsheet column (1-based index) with the sample ID
    :type sample_id: str
    :param meta_data: the columns in the spreadsheet containing the meta-data (1-based indices)
    :type meta_data: str
    :param recursive: whether to look for JSON files recursively
    :type recursive: bool
    :param indent: the indentation to use for pretty-printing, None turns off pretty-printing
    :type indent: int
    """
    ext = os.path.splitext(spreadsheet)[1].lower()
    if ext == ".csv":
        metadata = pd.read_csv(spreadsheet)
    elif ext == ".xls":
        metadata = pd.read_excel(spreadsheet, engine="xlrd")
    elif ext == ".xlsx":
        metadata = pd.read_excel(spreadsheet, engine="openpyxl")
    elif ext == ".ods":
        metadata = pd.read_excel(spreadsheet, engine="odf")
    else:
        raise Exception("Unsupported spreadsheet file format: %s" % spreadsheet)
    sampleid_col = index_value(sample_id, metadata.shape[1])
    metadata_cols = range_indices(meta_data, metadata.shape[1])
    if sampleid_col in metadata_cols:
        metadata_cols.remove(sampleid_col)
    lookup = dict()
    cols = metadata.columns
    for i in range(metadata.shape[0]):
        sid = str(metadata.iat[i, sampleid_col])
        lookup[sid] = dict()
        for n in metadata_cols:
            lookup[sid][cols[n]] = metadata.iat[i, n]
    add(path, lookup, recursive, indent=indent)


def main(args=None):
    """
    The main method for parsing command-line arguments and labeling.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    parser = argparse.ArgumentParser(
        description="Adds (global) meta-data stored in a spreadsheet to Happy meta-data JSON files (ext: %s)." % GLOBAL_EXT,
        prog="hmd-add-metadata",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--path", metavar="DIR", help="the directory with the Happy meta-data files (ext: %s)" % GLOBAL_EXT, required=True)
    parser.add_argument('-r', '--recursive', action="store_true", required=False, help='Whether to look for JSON files recursively.')
    parser.add_argument("-s", "--spreadsheet", metavar="FILE", help="the spreadsheet with the meta-data to add (csv/xls/xslx/ods)", required=True)
    parser.add_argument("-i", "--sample_id", metavar="INDEX", help="the column with the sample ID (1-based index)", required=False, default=FIRST)
    parser.add_argument("-m", "--meta_data", metavar="RANGE", help="the range of columns with sample data (1-based indices), automatically excludes sample ID", required=False, default=ALL)
    parser.add_argument("-I", "--indent", metavar="INT", help="the indentation to use for pretty-printing the JSON files", required=False, type=int, default=None)
    parsed = parser.parse_args(args=args)
    process(parsed.path, parsed.spreadsheet,
            sample_id=parsed.sample_id, meta_data=parsed.meta_data,
            recursive=parsed.recursive, indent=parsed.indent)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == '__main__':
    main()
