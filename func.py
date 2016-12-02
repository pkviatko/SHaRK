import collections
import csv
import ntpath
import os.path
from os import stat
import re
import subprocess
import tempfile
from functools import partial
from itertools import groupby
from multiprocessing.dummy import Pool as ThreadPool
from operator import itemgetter
from os import cpu_count
from random import sample
from time import time

from Bio import SeqIO, AlignIO
from Bio.Align.Applications import MuscleCommandline
from scipy.stats import scoreatpercentile

FULL_STATS_DICT = {"min_length": "Minimum length", "max_length": "Maximum length",
                   "mean_length": "Average length", "med_length": "Median length",
                   "perc_length": "95-th percentile length", "seq_no": "Number of seqs in file",
                   "file": "File name"}

SYNONYM_FILE = r'syn.csv'

f = open(SYNONYM_FILE, 'r')
tag_synonyms = []
for s in csv.reader(f, delimiter='\t'):
    sf_nonempty = set(filter(None, s))
    sf = {syn.lower() for syn in sf_nonempty}
    if sf:
        tag_synonyms.append(sf)
f.close()


def check_tags(descr, tags):
    final_bool = []
    for tag in tags:
        mid_count = False
        for syn_row in tag_synonyms:
            if tag.lower() in syn_row and any(syn in descr.lower() for syn in syn_row):
                mid_count = True
        if mid_count or tag.lower() in descr.lower():
            final_bool.append(True)
        else:
            final_bool.append(False)
#    print(final_bool)
    return final_bool
# checks for tags from list in string, returning a list of booleans


def read_check(input_path, req_tags, un_tags, sq_format):
    if sq_format in {'.gb', '.gbk'}:
        sq_format = 'gb'
    elif sq_format in {'.fas', '.fasta'}:
        sq_format = 'fasta'
    i = open(input_path, 'r')
    if req_tags:
        tags_list = req_tags.split(', ')
        req_seqs = [seq for seq in SeqIO.parse(i, sq_format) if all(b for b in check_tags(seq.description, tags_list))]
    else:
        req_seqs = [seq for seq in SeqIO.parse(i, sq_format)]
    if un_tags:
        un_list = un_tags.split(', ')
        final_seqs = [seq for seq in req_seqs if not any(b for b in check_tags(seq.description, un_list))]
    else:
        final_seqs = req_seqs
    return final_seqs
# reads FASTA file into a list, checking the tag name


def species_name(record):
        species = re.compile('\W*([A-Z]+[a-z]+[\W_]*[a-z]*)')
        s = species.search(record.description)
        if s:
            name = s.group()
        else:
            name = str(record.description)
        name = name.strip('|_ ')
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


def species_muscle(seqs, iters=1, gap_open=-400):
    muscle_cline = [r"muscle", "-maxiters", str(iters), "-quiet", "-gapopen", str(float(gap_open)), "-diags"]
    muscle_child = subprocess.Popen(muscle_cline,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
    SeqIO.write(seqs, muscle_child.stdin, 'fasta')
    muscle_child.stdin.close()
    aligned = AlignIO.read(muscle_child.stdout, 'fasta')
    muscle_child.stdout.close()
    return aligned
# uses muscle to align a list of seqs returning aligned list


def temp_aligned_sp(sp_group_list, dir_name):
    pool = ThreadPool(cpu_count()+1)
    sp_temp_file_list = pool.map(partial(temp_align_file, dir_name=dir_name), sp_group_list)
    pool.close()
    pool.join()
    return sp_temp_file_list


def temp_align_file(sp, dir_name):
    with tempfile.NamedTemporaryFile(suffix='.fas', delete=False, dir=dir_name, mode='w') as tmp:
        sp_aligned = species_muscle(sp)
        AlignIO.write(sp_aligned, tmp, 'fasta')
        return tmp.name
# uses species_muscle to create temporary alignments for species sub-lists


def profile_muscle(fas2, fas1, iters=1, gap_open=-400):
    muscle_cline = [r"muscle", "-maxiters", str(iters), "-quiet", "-gapopen", str(float(gap_open)), "-diags",
                    "-profile", "-in1", str(fas1), "-in2", str(fas2)]
    muscle_child = subprocess.Popen(muscle_cline,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
    profile_aligned_out = AlignIO.read(muscle_child.stdout, 'fasta')
    muscle_child.stdout.close()
    return profile_aligned_out[1:]
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
        pool = ThreadPool(cpu_count()+1)
        whole_aligned = pool.map(partial(profile_muscle, fas1=reference), aligned_files)
        pool.close()
        pool.join()
        whole_aligned = [item for sublist in whole_aligned for item in sublist]
    return whole_aligned


def make_copies(population, copies, del_factor, del_option,
                reference, source, tax, output, percentage_toggled, session_report):
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
        session_report.o_files += 1
        session_report.o_seqs += len(population)
        SeqIO.write(population, so, 'fasta')
        so.close()

    if tax:
        split_pop = split_list_sp(population)
        for group in split_pop:
            sp = open(output.replace('.fas', '_%s.fas' % species_name(group[0])), 'w')
            if ref:
                group = [ref] + group
            SeqIO.write(group, sp, 'fasta')

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
            session_report.o_files += 1
            session_report.o_seqs += len(sub_pop)
            SeqIO.write(sub_pop, w, 'fasta')
            w.close()
# writes a number of copies of fasta file with a certain sampling pattern


def append_file(uni_filename, writable_seqs, session_report):
    if uni_filename:
        session_report.o_seqs += len(writable_seqs)
        with open(uni_filename, 'a') as u:
            SeqIO.write(writable_seqs, u, 'fasta')
            u.close()
# appends a list of sequences to a fasta file for uniting taxa into one file


def file_analysis(param_dict, file_path, session_report):
    curr_time = time()

    out_dir = param_dict["output_directory"]
    ref_path = param_dict["reference_path"]
    pos_tags = param_dict["positive_tags"]
    neg_tags = param_dict["negative_tags"]
    del_repeats = param_dict["delete_repeats"]
    uni_files = param_dict["unite_bool"]
    cp_num = param_dict["copies_number"]
    del_factor = param_dict["deletion_factor"]
    del_option = param_dict["deletion_option"]
    source = param_dict["source_bool"]
    perc_toggle = param_dict["percentage_toggled"]
    targ_range = param_dict["reference_target_range"]
    align_opt = param_dict["alignment_option"]
    tax_split = param_dict["split_by_taxon"]

    file_name = ntpath.basename(file_path)
    extension = ntpath.splitext(file_path)[1]
    if uni_files is True:
        united_file = "united_name.fas"
        united_name = os.path.join(out_dir, united_file)
        session_report.o_files += 1
    else:
        united_name = ''
    output_file_path = os.path.join(out_dir, file_name)
    population = read_check(file_path, pos_tags, neg_tags, extension)
    population.sort(key=species_name)
    if del_repeats:
        new_population = []
        if align_opt == "simple":
            for rec in population:
                if len(new_population):
                    if species_name(rec) == species_name(new_population[-1]):
                        if compare_align_score(new_population[-1], rec) == 2:
                            new_population = new_population[:-1]
                            new_population.append(rec)

                    else:
                        new_population.append(rec)
                else:
                    new_population.append(rec)
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                if align_opt == "sub":
                    split_list = split_list_sp(population)
                    temp_files = temp_aligned_sp(split_list, tmp_dir)
                elif align_opt == "whole":
                    whole_aligned = species_muscle(population)
                    temp_fas = tempfile.NamedTemporaryFile(suffix=".fas", dir=tmp_dir).name
                    fas = open(temp_fas, 'w')
                    AlignIO.write(whole_aligned, fas, 'fasta')
                    fas.close()
                    temp_files = [temp_fas]
                elif align_opt == "even":
                    part = round(len(population) / (len(population) // 75 + 1)) + 1
                    split_list = [population[i: i + part] for i in range(0, len(population), part)]
                    temp_files = temp_aligned_sp(split_list, tmp_dir)
                aligned = prof_align_loop(temp_files, tmp_dir, ref_path)
            split_aligned = split_list_sp(aligned)
            for sp in split_aligned:
                new_population.append(best_score_rec(sp, targ_range))
    else:
        new_population = population
    append_file(united_name, new_population, session_report)
    make_copies(new_population, cp_num, del_factor, del_option, ref_path, source, tax_split,
                output_file_path, perc_toggle, session_report)
    elapsed = (time() - curr_time)
    print(elapsed)
    session_report.runtime += elapsed
    return elapsed


def compare_align_score(seq1, seq2):
    sq1 = str(seq1.seq)
    sq2 = str(seq2.seq)
    strp_sq1 = re.sub('[nN-]', '', sq1)
    strp_sq2 = re.sub('[nN-]', '', sq2)
    if len(strp_sq1) < len(strp_sq2):
        verdict = 2
    else:
        verdict = 1
    # print(str(len(strp_sq1)) + ' and ' + str(len(strp_sq2)))
    return verdict


class TruncStats:
    def __init__(self):
        self.ends = []
        self.starts = []

    def get_start_end(self, rec):
        whole = len(rec.seq.lower())
        start = whole - len(rec.seq.lower().lstrip('-n'))
        self.starts.append(start)
        end = len(rec.seq.lower().rstrip('-n'))
        self.ends.append(end)

    def trunc_ranges(self):
        trunc_dict = collections.OrderedDict()
        trunc_dict["Minimum truncation range"] = [max(self.starts), min(self.ends)]
        trunc_dict["Maximum truncation range"] = [min(self.starts), max(self.ends)]
        trunc_dict["Mean truncation range"] = [round(sum(self.starts)/len(self.starts), 1),
                                               round(sum(self.ends)/len(self.ends), 1)]
        trunc_dict["Median truncation range"] = [round(scoreatpercentile(self.starts, per=50), 1),
                                                 round(scoreatpercentile(self.ends, per=50), 1)]
        trunc_dict["Percentile truncation range"] = [round(scoreatpercentile(self.starts, per=87.5), 1),
                                                     round(scoreatpercentile(self.ends, per=12.5), 1)]
        return trunc_dict


class SessionStats:
    def __init__(self):
        self.i_files = 0
        self.i_seqs = 0
        self.o_files = 0
        self.o_seqs = 0
        self.runtime = 0.0

    def produce_dict(self):
        run_dict = collections.OrderedDict()
        run_dict["input files"] = self.i_files
        run_dict["input sequences"] = self.i_seqs
        run_dict["output files"] = self.o_files
        run_dict["output sequences"] = self.o_seqs
        run_dict["runtime"] = round(self.runtime, 4)
        return run_dict
