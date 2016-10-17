import collections
import csv
import ntpath
import os.path
import re
import subprocess
import tempfile
from itertools import groupby
from operator import itemgetter
from random import sample
from time import time

from Bio import SeqIO, AlignIO
from Bio.Align.Applications import MuscleCommandline
from scipy.stats import scoreatpercentile

f = open('syn.csv', 'r')
gene_synonyms = []
for s in csv.reader(f, delimiter='\t'):
    sf = list(filter(None, s))
    if sf:
        gene_synonyms.append(sf)
f.close()


def check_tags(descr, tags):
    final_bool = []
    for tag in tags:
        mid_count = 0
        for syn_row in gene_synonyms:
            loc_count = 0
            for syn in syn_row:
                if syn.lower() == tag.lower():
                    loc_count += 1
            if loc_count > 0:
                for syn in syn_row:
                    if syn != '' and syn.lower() in descr.lower():
                        mid_count += 1
        if mid_count > 0 or tag.lower() in descr.lower():
            final_bool.append(True)
        else:
            final_bool.append(False)
#    print(final_bool)
    return final_bool
# checks for tags from list in string, returning a list of booleans


def read_check(input_path, req_tags, un_tags, sq_format):
    if sq_format == '.gb' or sq_format == '.gbk':
        sq_format = 'gb'
    elif sq_format == '.fas' or sq_format == '.fasta':
        sq_format = 'fasta'
    i = open(input_path, 'r')
    if req_tags:
        tags_list = req_tags.split(', ')
        req_seqs = [s for s in SeqIO.parse(i, sq_format) if all(b for b in check_tags(s.description, tags_list))]
    else:
        req_seqs = [s for s in SeqIO.parse(i, sq_format)]
#    print(len(req_seqs))
    if un_tags:
        un_list = un_tags.split(', ')
        final_seqs = [s for s in req_seqs if not any(b for b in check_tags(s.description, un_list))]
    else:
        final_seqs = req_seqs
#    print(len(final_seqs))
    return final_seqs
# reads FASTA file into a list, checking the gene name


def species_name(record):
        species = re.compile('\W*([A-Z]+[a-z]+[\W_]*[a-z]*)')
        s = species.search(record.description)
        if s:
            name = s.group()
        else:
            name = str(record.description)
        name = name.lstrip('|_ ')
#        print(name)
        return name
# finds a taxon name in record description(primarily a species) and returns it


def split_list_sp(seq_list):
    seq_list.sort(key=species_name)
    sp_groups = []
    for sp, sp_list in groupby(seq_list, key=species_name):
        sp_groups.append(list(sp_list))
    return sp_groups
# splits the sequence population by species name into sub-populations of the same species


def species_muscle(seqs, iters=2, gap_open=-400):
    muscle_cline = MuscleCommandline(maxiters=iters, quiet=True, gapopen=float(gap_open))
    muscle_child = subprocess.Popen(str(muscle_cline),
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
    SeqIO.write(seqs, muscle_child.stdin, 'fasta')
    muscle_child.stdin.close()
    aligned = AlignIO.read(muscle_child.stdout, 'fasta')
    muscle_child.stdout.close()
    return aligned
# uses muscle to align a list of seqs returning aligned list


def temp_aligned_sp(sp_group_list, dir_name):
    sp_prof_file_names = []
    for sp in sp_group_list:
        with tempfile.NamedTemporaryFile(suffix='.fas', delete=False, dir=dir_name, mode='w') as tmp:
            sp_aligned = species_muscle(sp)
            AlignIO.write(sp_aligned, tmp, 'fasta')
            sp_prof_file_names.append(tmp)
    return sp_prof_file_names
# uses species_muscle to create temporary alignments for species sub-lists


def profile_muscle(fas1, fas2, iters=2, gap_open=-400):
    muscle_cline = MuscleCommandline(maxiters=iters, quiet=True, gapopen=float(gap_open),
                                     profile=True, in1=fas1, in2=fas2)
    muscle_child = subprocess.Popen(str(muscle_cline),
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
    profile_aligned_out = AlignIO.read(muscle_child.stdout, 'fasta')
    muscle_child.stdout.close()
    return profile_aligned_out
# uses muscle to align two alignments, returning the aligned list


def range_stats(aligned_subset, perc=(95, 75)):
    stats_list = [[], [], []]
    for rec in aligned_subset:
        seq_str = str(rec.seq).lower()
        length = len(seq_str)
        start = length - len(seq_str.lstrip('-n'))
        end = len(seq_str.rstrip('-n'))
        stats_list[0].append(start)
        stats_list[1].append(end)
        stats_list[2].append(len(seq_str.strip('-n')))
    stats_dict = collections.OrderedDict()
    stats_dict["perc_length"] = scoreatpercentile(stats_list[2], perc[1])
    stats_dict["med_length"] = scoreatpercentile(stats_list[2], per=50)
    stats_dict["mean_length"] = round(sum(stats_list[2]) / len(stats_list[2]), 2)
    stats_dict["max_length"] = max(stats_list[2])
    stats_dict["min_length"] = min(stats_list[2])
    stats_dict["seq_no"] = len(stats_list[0])

    return stats_dict

full_stats_dict = {"min_length": "Minimum length", "max_length": "Maximum length",
                   "mean_length": "Average length",
                   "med_length": "Median length",
                   "perc_length": "95-th percentile length",
                   "seq_no": "Number of seqs in file",
                   "file": "File name"}


def best_trunc_range(split_aligned, perc=(25, 75)):
    stats_list = [[], []]
    for sp in split_aligned:
        stats_list[0].append(range_stats(sp).get("perc_start"))
        stats_list[1].append(range_stats(sp).get("perc_end"))
    stats_dict = {"min_start": min(stats_list[0]), "max_end": max(stats_list[1]),
                  "max_start": max(stats_list[0]), "min_end": min(stats_list[1]),
                  "mean_start": sum(stats_list[0]) / len(stats_list[0]),
                  "mean_end": sum(stats_list[1]) / len(stats_list[1]),
                  "med_start": scoreatpercentile(stats_list[0], per=50),
                  "med_end": scoreatpercentile(stats_list[1], per=50),
                  "perc_start": scoreatpercentile(stats_list[0], perc[0]),
                  "perc_end": scoreatpercentile(stats_list[1], perc[1])}
    start = round(stats_dict.get("med_start"))
    end = round(stats_dict.get("med_end"))
    best_range = (start, end)
    return best_range


def align_score(rec_list, ref_range):
    score_list = []
    start = ref_range[0] - 1
    end = ref_range[1] - 1
    for rec in rec_list:
        str_seq = str(rec.seq).lower()
        len_stripped = len(str_seq.strip('-n'))
        overlap_no_spaces = re.sub('[N-]', '', str_seq[start: end], re.I)
        len_no_spaces = len(overlap_no_spaces)
        overlap_no_spaces_deg = re.sub('[BDHKMNRSVWY]', '', overlap_no_spaces, re.I)
        len_no_spaces_deg = len(overlap_no_spaces_deg)

        seq_score = [rec, len_no_spaces, len_no_spaces_deg, len_stripped]
        score_list.append(seq_score)
    return score_list
# takes the aligned sequences and returns the scores to each sequence from the profile alignment


def best_score_rec(rec_list, ref_range):
    score_list = align_score(rec_list, ref_range)
    sorted_scores = sorted(score_list, key=itemgetter(1, 2, 3), reverse=True)
    return sorted_scores[0][0]
# takes a list of scores, compares them and returns the best score


def prof_align_loop(aligned_files, temp_dir, reference=False):
    if reference:
        aligned_files = [reference] + aligned_files
    temp_fas = tempfile.NamedTemporaryFile(dir=temp_dir, suffix=".fas", delete=False).name
    print(temp_fas)
    for i in range(1, len(aligned_files)):
        if i == 1:
            prof = profile_muscle(aligned_files[0], aligned_files[1])

        else:
            prof = profile_muscle(temp_fas, aligned_files[i])
        fas1 = open(temp_fas, 'w')
        AlignIO.write(prof, fas1, 'fasta')
        fas1.close()
    wh = open(temp_fas, 'r')
    whole_aligned = [r for r in SeqIO.parse(wh, 'fasta')][1:]
    return whole_aligned


def make_copies(population, copies, del_factor, del_option,
                reference, source, output, percentage_toggled):
    # if reference path is not empty, reads it into memory
    if reference:
        r = open(reference, 'r')
        ref = SeqIO.read(r, 'fasta')
        r.close()
    else:
        ref = ''
    # if checkbox save source file is checked, writes the FASTA file without any sampling operations on it
    if source is True:
        so = open(output.replace('.fas', '(0).fas'), 'w')
        if ref:
            population = [ref] + population
        SeqIO.write(population, so, 'fasta')
        so.close()

    seq_number = len(population)
    # specifies the number of records in sample files according to the sampling procedure specified by user
    if del_option == 'delete':
        if percentage_toggled is True:
            seq_number *= 1 - (del_factor/100)
        else:
            seq_number -= del_factor
    elif del_option == 'leave':
        if percentage_toggled is True:
            seq_number *= del_factor
        else:
            seq_number = del_factor
    if seq_number > len(population):
        seq_number = len(population)
    seq_number = int(seq_number)
    # randomly samples a given number of record from the initial population into sample files (a number of times)
    if copies and del_factor:
        for s in range(1, copies+1):
            sub_pop = sample(population, seq_number)
            if ref:
                sub_pop = [ref] + sub_pop
            w = open(output.replace('.fas', '(%s).fas' % s), 'w')
            SeqIO.write(sub_pop, w, 'fasta')
            w.close()
# writes a number of copies of fasta file with a certain sampling pattern


def append_file(uni_filename, writable_seqs):
    if uni_filename:
        with open(uni_filename, 'a') as u:
            SeqIO.write(writable_seqs, u, 'fasta')
            u.close()
# appends a list of sequences to a fasta file for uniting taxa into one file


def file_analysis(param_dict, file_path):
    out_dir = param_dict["output_directory"]
    ref_path = param_dict["reference_path"]
    pos_tags = param_dict["positive_tags"]
    neg_tags = param_dict["negative_tags"]
    del_repeats = param_dict["delete_repeats"]
    uni_files = ["unite_bool"]
    cp_num = param_dict["copies_number"]
    del_factor = param_dict["deletion_factor"]
    del_option = param_dict["deletion_option"]
    source = param_dict["source_bool"]
    perc_toggle = param_dict["percentage_toggled"]
    targ_range = param_dict["reference_target_range"]

    if ref_path != '':
        r = open(ref_path, 'r')
        ref = SeqIO.read(r, 'fasta')
        r.close()
    else:
        ref = ''

    curr_time = time()
    file_name = ntpath.basename(file_path)
    extension = ntpath.splitext(file_path)[1]
    if uni_files is True:
        united_name = "united_set" + extension
    else:
        united_name = ''
    output_file_path = os.path.join(out_dir, file_name)
    population = read_check(file_path, pos_tags, neg_tags, extension)
    population.sort(key=species_name)
    if del_repeats:
        new_population = []
        split_list = split_list_sp(population)
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_files = temp_aligned_sp(split_list, tmp_dir)
            aligned = prof_align_loop(temp_files, tmp_dir, ref_path)
        split_aligned = split_list_sp(aligned)
        for sp in split_aligned:
            new_population.append(best_score_rec(sp, targ_range))
    else:
        new_population = population
    append_file(united_name, new_population)
    make_copies(new_population, cp_num, del_factor, del_option, ref_path, source, output_file_path, perc_toggle)
    elapsed = (time() - curr_time)
    print(elapsed)
    return elapsed
