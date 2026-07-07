#!/usr/bin/env python3
"""rapdtool_split_bins.py - write one FASTA per identified species/genus.

Reads the RaPDTool confidence report (rapdtool_confidence.txt) produced by
rapdtool_results.pl, maps each confidently identified bin to its taxon, and
copies the corresponding refined-bin FASTA into an output directory renamed by
taxon.

Can be run standalone on an existing RaPDTool results directory:
    rapdtool_split_bins.py --root /path/to/rapdtool_results
"""

import argparse
import glob
import os
import re
import shutil
import sys

HEADER_TOKENS = {'Genus-closest-hit', 'Species', 'Bin'}


def sanitize(label):
    label = label.strip()
    label = re.sub(r'[^\w.+-]+', '_', label)   # spaces, slashes, etc. -> _
    return label.strip('_') or 'unknown'


def parse_confidence(path):
    """Return list of (taxon_label, bin_name) from Genus/Species sections."""
    pairs = []
    section = None
    with open(path) as fh:
        for raw in fh:
            line = raw.rstrip('\n')
            stripped = line.strip()
            if stripped.startswith('#'):
                low = stripped.lower()
                if 'genus with high confidence' in low:
                    section = 'taxon'
                elif 'species with high confidence' in low:
                    section = 'taxon'
                elif 'focus profile' in low:
                    section = 'focus'
                else:
                    section = None
                continue
            if section != 'taxon' or stripped == '':
                continue
            fields = line.split('\t')
            if len(fields) < 3:
                continue
            if fields[0] in HEADER_TOKENS or fields[-2] == 'Bin':
                continue
            label = fields[0].strip()
            bin_name = fields[-2].strip()
            if label and bin_name:
                pairs.append((label, bin_name))
    return pairs


def find_refined_bins_dirs(root):
    pattern = os.path.join(root, 'workfmbm', 'outbinningref',
                           '*_Binning_refiner_outputs', '*_refined_bins')
    return sorted(d for d in glob.glob(pattern) if os.path.isdir(d))


def locate_bin_fasta(bin_name, bins_dirs):
    for d in bins_dirs:
        cand = os.path.join(d, bin_name + '.fna')
        if os.path.isfile(cand):
            return cand
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='Write one FASTA per identified species/genus from RaPDTool results.')
    ap.add_argument('--root', default='.',
                    help='RaPDTool results directory (default: current dir)')
    ap.add_argument('--confidence',
                    help='path to rapdtool_confidence.txt (default: <root>/rapdtool_confidence.txt)')
    ap.add_argument('--bins-dir', action='append', dest='bins_dirs',
                    help='refined-bins directory (repeatable; default: autodiscovered under root)')
    ap.add_argument('--out-dir',
                    help='output directory (default: <root>/species_bins)')
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    confidence = args.confidence or os.path.join(root, 'rapdtool_confidence.txt')
    out_dir = args.out_dir or os.path.join(root, 'species_bins')
    bins_dirs = [os.path.abspath(d) for d in (args.bins_dirs or [])] \
        or find_refined_bins_dirs(root)

    if not os.path.isfile(confidence):
        print('split_bins: no confidence report found (%s); nothing to do' % confidence,
              file=sys.stderr)
        return 0
    if not bins_dirs:
        print('split_bins: no refined-bins directory found under %s; nothing to do' % root,
              file=sys.stderr)
        return 0

    pairs = parse_confidence(confidence)
    if not pairs:
        print('split_bins: no confidently identified taxa; nothing to do', file=sys.stderr)
        return 0

    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for label, bin_name in pairs:
        src = locate_bin_fasta(bin_name, bins_dirs)
        if not src:
            print('split_bins: warning - bin FASTA not found for "%s"' % bin_name,
                  file=sys.stderr)
            continue
        base = '%s__%s.fna' % (sanitize(label), bin_name)
        dest = os.path.join(out_dir, base)
        n = 1
        while os.path.exists(dest):
            dest = os.path.join(out_dir, '%s__%s_%d.fna' % (sanitize(label), bin_name, n))
            n += 1
        shutil.copy(src, dest)
        written += 1

    print('split_bins: wrote %d species FASTA file(s) to %s' % (written, out_dir))
    return 0


if __name__ == '__main__':
    sys.exit(main())
