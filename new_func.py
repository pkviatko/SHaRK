from Bio import SeqIO, AlignIO
import re
from itertools import groupby


def read_seq(path, form, alph):
    with open(path, 'r') as s:
        sequences = [seq for seq in SeqIO.parse(s, form, alph)]
    return sequences

# def filter_seq(seqs, tags, strategy):


def tax_name(record, level):
    tax_regex = {'species': '\W*([A-Z]+[a-z]+[\W_]*[a-z]*)',
                 'genus': '\W*([A-Z]+[a-z]+)',
                 'family': '\W*([A-Z]+[a-z]+idea|aceae)'}
    taxon = re.compile(tax_regex.get(level))
    s = taxon.search(record.description)
    if s:
        name = s.group()
    else:
        name = str(record.description)
    name = name.strip('|_ ')
    #        print(name)
    return name


def split_by_tax(seqs, split_level):
    seqs.sort(key=tax_name(level=split_level))
    sample_list = []
    for sp, sp_list in groupby(seqs, key=tax_name):
        sample_list.append(list(sp_list))
    return sample_list



