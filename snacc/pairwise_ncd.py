import bz2
import gzip
import lzma
import os
import sys
import zlib

import lz4framed
from Bio import SeqIO

def bwt(s):
    """
    Code for Burrows-Wheeler Transformation. The code is adapted from Rosetta Code.
    """
    # uncomment below if you plan on decoding
    #s = "\002" + s + "\003"
    table = sorted(s[i:] + s[:i] for i in range(len(s)))
    last_column = [row[-1:] for row in table]
    return "".join(last_column)


def extract_sequences(filepath, reverse_complement=False, BWT=False):
    if type(filepath) == tuple:
        return extract_sequences(filepath[0]) + extract_sequences(filepath[1])
    seq = ""
    for seq_record in SeqIO.parse(filepath.absolute(), "fasta"):
        if reverse_complement:
            seq += str(seq_record.seq.reverse_complement())
        else:
            seq += str(seq_record.seq)
    if not seq:
        raise ValueError(f"No sequence extracted. Ensure that file {filepath.absolute()} contains a proper FASTA definition line (i.e. a line that starts with '>sequence_name').")
    if BWT:
        return bwt(seq)
    else:
        return seq

def compressed_size(filename, algorithm, reverse_complement=False, save_directory=None, BWT=False):
    '''

    Args:
        filename (pathlib.Path)
        algorithm (str)
                reverse_complement(bool, optional)
        save_directory (pathlib.Path, optional)

    Returns
        (pathlib.Path,int): the number of bytes in the compressed file
    '''

    # check if already compressed @TODO
    sequence = bytes(extract_sequences(filename, reverse_complement=reverse_complement, BWT=BWT), encoding="utf-8")
    extension = {
        "lzma": ".lzma",
        "gzip": ".gz",
        "bzip2": ".bz2",
        "zlib": ".ZLIB",
        "lz4": ".lz4"
    }
    if algorithm == "lzma":
        compressed_seq = lzma.compress(sequence)
    elif algorithm == "gzip":
        compressed_seq = gzip.compress(sequence)
    elif algorithm == "bzip2":
        compressed_seq = bz2.compress(sequence)
    elif algorithm == "zlib":
        compressed_seq = zlib.compress(sequence)
    elif algorithm == "lz4":
        compressed_seq = lz4framed.compress(sequence)

    if save_directory:
        if type(filename) == tuple:
            out_file = filename[0].stem + filename[1].name
        else:
            out_file = filename.name
        with open(os.path.join(save_directory.absolute(), out_file + extension[algorithm]), 'wb') as f:
            f.write(compressed_seq)

    return (filename, sys.getsizeof(compressed_seq))
#calculates NCD for 2 sequence sizes and their concatenation size
def compute_distance(x, y, cxy, cyx):
    if x > y:
        return min((cxy - y) / x, (cyx - y) / x)
    elif y > x:
        return min((cxy - x) / y, (cyx - x) / y)
    else:
        return min((cxy - x) / x, (cyx - x) / x)
