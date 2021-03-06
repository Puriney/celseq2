#!/usr/bin/env python3
# coding: utf-8
import HTSeq
import argparse
import pickle

from celseq2.helper import print_logger
# from genometools.ensembl.annotations import get_genes


def cook_anno_model(gff_fpath, feature_atrr='gene_id', feature_type='exon',
                    gene_types = (),
                    stranded=True, dumpto=None, verbose=False):
    '''
    Prepare a feature model.

    Output: (features, exported_genes) where:
        - features: HTSeq.GenomicArrayOfSets()
        - exported_genes: a sorted list

    For example, feature_atrr = 'gene_name', feature_type = 'exon',
    gene_types = ('protein_coding', 'lincRNA'):
        - features: all exons ~ all gnames mapping and ready for counting
        - exported_genes: only protein_coding and lincRNA gnames are visible
    Quantification used the full genes but only the selected genes are reported.
    '''
    features = HTSeq.GenomicArrayOfSets("auto", stranded=stranded)
    fh_gff = HTSeq.GFF_Reader(gff_fpath)
    exported_genes = set()
    i = 0
    for gff in fh_gff:
        if verbose and i % 100000 == 0:
            print_logger('Processing {:,} lines of GFF...'.format(i))
        i += 1

        if gff.type != feature_type:
            continue

        features[gff.iv] += gff.attr[feature_atrr].strip()

        if not feature_atrr.startswith('gene'):
            exported_genes.add(gff.attr[feature_atrr].strip())
            continue

        if not gene_types:
            exported_genes.add(gff.attr[feature_atrr].strip())
            continue

        if gff.attr.get('gene_biotype', None) in gene_types:
            exported_genes.add(gff.attr[feature_atrr].strip())

    print_logger('Processed {:,} lines of GFF...'.format(i))

    # Use genometools to select exported_genes
    # if gene_types:
    #     exported_genes = get_genes(gff_fpath, valid_biotypes=set(gene_types))
    #     exported_genes = list(exported_genes['name'].values)

    if exported_genes:
        exported_genes = tuple(sorted(exported_genes))
    if dumpto:
        with open(dumpto, 'wb') as fh:
            pickle.dump((features, exported_genes), fh)
    return((features, exported_genes))


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--gff-file', type=str, metavar='FILENAME',
                        required=True,
                        help='File path to GFF')
    parser.add_argument('--feature-atrr', type=str,
                        default='gene_id',
                        help=('Reserved word for feature_atrr in GTF/GFF to be'
                              ' considered a Gene, e.g., \"gene_id\".'))
    parser.add_argument('--feature-type', type=str,
                        default='exon',
                        help=('Reserved word for feature type in 3rd column'
                              ' in GTF/GFF to be the components of \'Gene\','
                              ' e.g., \"exon\".'))
    parser.add_argument('--gene-types', type=tuple,
                        default=(),
                        help=('Reserved words for the attrbute \"gene_biotype\"'
                              ' (Gene type), e.g., protein_coding, lincRNA'))
    parser.add_argument('--strandless', dest='stranded', action='store_false')
    parser.set_defaults(stranded=True)
    parser.add_argument('--dumpto', type=str, metavar='FILENAME',
                        default='annotation.pickle',
                        help='File path to save cooked annotation model')
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    _ = cook_anno_model(gff_fpath=args.gff_file,
                        feature_atrr=args.feature_atrr,
                        feature_type=args.feature_type,
                        gene_types=args.gene_types,
                        stranded=args.stranded,
                        dumpto=args.dumpto,
                        verbose=args.verbose)


if __name__ == "__main__":
    main()
