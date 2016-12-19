#Interface

##Primary processing tab.

Opening file(s). Press `Ctrl + O` or [button] to open a single or multiple files. Or enter the path into the corresponding [field]. Files can be in FASTA or GenBank format.

Choosing output directory. Press `Ctrl + S` or [button] to choose a directory for output files. Or enter the path into the corresponding [field]. Output files are named as `original_name(n).extension` where `n` is the number of the copy or 0 for original file.

To choose a reference file press `Ctrl + R` or [button]. Or enter the path into the corresponding [field]. The file must contain a single sequence in FASTA or GenBank format.

Enter positive and negative tags into the corresponding [field].

To delete repeats and untie files tick the corresponding [check boxes]. The resulting united file name will be `united.extension`.


##Alignment tab.

As of now, most alignment options are outside of user's reach.
Alignment is is used solely for the purpose of sequence comparison, so there are four option in corresponding [combo box]:
1. Alignment of the whole file
2. Alignment of the taxon subsets
3. Alignment of even subsets
4. Sequence comparison without alignment
For now, alignment of even subsets works several times faster than taxon subsets, while 10-100 times faster than whole file alignment. Comparison without alignment is ~100 times faster than comparisons using alignment.


##Re-sampling tab.

Save source file.

Split files by taxon.

Show performance report.

Set copies number.

Set replica content: deletion/saving of percent/number of sequences.

Instructions for re-sampling tab.


