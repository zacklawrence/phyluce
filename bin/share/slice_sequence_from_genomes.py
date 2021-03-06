#!/usr/bin/env python
# encoding: utf-8
"""
File: slice_sequence_from_genomes.py
Author: Brant Faircloth

Created by Brant Faircloth on 02 April 2012 11:04 PDT (-0700)
Copyright (c) 2012 Brant C. Faircloth. All rights reserved.

Description: 

"""

import os
import argparse
import ConfigParser

from phyluce import lastz
from bx.seq import twobit
from seqtools.sequence import fasta
from phyluce.helpers import FullPaths, is_dir, is_file

#import pdb


def get_args():
    """Get arguments from CLI"""
    parser = argparse.ArgumentParser(
            description="""Given a LASTZ input directory, find matches, add flank, and return a FASTA file of sequences""")
    parser.add_argument(
            "conf",
            action=FullPaths,
            type=is_file,
            help="""Path to the configuration file"""
        )
    parser.add_argument(
            "lastz",
            action=FullPaths,
            type=is_dir,
            help="""Path to the directory containing LASTZ results"""
        )
    parser.add_argument(
            "output",
            action=FullPaths,
            type=is_dir,
            help="""Path to the output directory for storing FASTA files"""
        )
    parser.add_argument(
            "--flank",
            type=int,
            default=500,
            help="""The amount of flanking sequence to add to each match""",
        )
    return parser.parse_args()


def get_all_files_from_conf(conf):
    all_files = []
    if conf.has_section("chromos"):
        all_files.extend(conf.items("chromos"))
    if conf.has_section("scaffolds"):
        all_files.extend(conf.items("scaffolds"))
    return all_files


def slice_and_return_fasta(tb, lz, flank=500):
    record = fasta.FastaSequence()
    if lz.zstart1 - flank > 0:
        ss = lz.zstart1 - flank
    else:
        ss = 0
    if lz.end1 + flank < len(tb[lz.name1]):
        se = lz.end1 + flank
    else:
        se = len(tb[lz.name1])
    record.identifier = "{0}|{1}|{2}-{3}|{4}-{5}||{6}|{7}|{8}-{9}".format(
            lz.name1,
            lz.strand1,
            lz.zstart1,
            lz.end1,
            ss,
            se,
            lz.name2.strip('>'),
            lz.strand2,
            lz.zstart2,
            lz.end2
        )
    record.sequence = tb[lz.name1][ss:se]
    return record


def main():
    args = get_args()
    conf = ConfigParser.ConfigParser()
    conf.read(args.conf)
    all_files = get_all_files_from_conf(conf)
    for genome in all_files:
        name, twobit_name = genome
        out_file = os.path.join(args.output, name) + ".fasta"
        out = fasta.FastaWriter(out_file)
        tb = twobit.TwoBitFile(file(twobit_name))
        lz = os.path.join(args.lastz, name) + ".lastz"
        count = 0
        for row in lastz.Reader(lz, long_format=True):
            sequence = slice_and_return_fasta(tb, row, args.flank)
            out.write(sequence)
            count += 1
        print "\t{} sequences written to {}".format(count, out_file)
        out.close()

if __name__ == '__main__':
    main()