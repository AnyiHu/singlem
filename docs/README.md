# SingleM
Welcome.

SingleM is a tool for profiling shotgun metagenomes. It has a particular strength in detecting microbial lineages which are not in reference databases. The method it uses also makes it suitable for some related tasks, such as assessing eukaryotic contamination, finding bias in genome recovery, computing ecological diversity metrics, and lineage-targeted MAG recovery.

SingleM has been applied to >200,000 public metagenomes. The resulting data are available at a companion website [sandpiper](https://sandpiper.qut.edu.au).

There are several tools, after [installation](/Installation):

* [singlem pipe](/usage/pipe) - the main workflow (`singlem pipe`) which generates OTU tables and [GTDB](https://gtdb.ecogenomic.org/) taxonomic profiles. 
* [singlem appraise](/usage/appraise) - How much of a metagenome do the genomes or assembly represent?
* [singlem makedb](/usage/makedb) & [query](/usage/query)- Create a database from an OTU table, for sequence similarity searching.
* [single summarise](/usage/summarise) - Mechanical transformations of a `singlem pipe` results.
* [singlem renew](/usage/renew) - Given previously generated results, re-run the pipeline with a new reference sequence/taxonomy database.
* [singlem condense](/usage/condense) - Given an OTU table, summarise the results into a taxonomic profile.

## Help
If you have any questions or comments, raise a [GitHib issue](https://github.com/wwood/singlem/issues) or just send us an [email](https://research.qut.edu.au/cmr/team/ben-woodcroft/).

### Glossary

* **OTU table** - A table containing window sequences per metagenome/contig and marker gene. It may be in default form (a TSV with 6 columns, like below), or an extended form with more detail in further columns. The extended form is generated with the `--output-extras` option to `singlem pipe`, `renew` and `summarise`. Columns:
  1. marker name
  2. sample name
  3. sequence of the OTU
  4. number of reads detected from that OTU
  5. estimated coverage of a genome from this OTU
  6. "median" taxonomic classification of each of the reads in the OTU i.e. the most specific taxonomy that 50%+ of the reads agree with.
```
gene    sample  sequence        num_hits        coverage        taxonomy
4.21.ribosomal_protein_S19_rpsS my_sequences  TGGTCGCGCCGTTCGACGGTCACTCCGGACTTCATCGGCCTACAGTTCGCCGTGCACATC    1       1.64    Root; d__Bacteria; p__Proteobacteria; c__Deltaproteobacteria; o__Desulfuromonadales
4.21.ribosomal_protein_S19_rpsS my_sequences  TGGTCGCGGCGCTCAACCATTCTGCCCGAGTTCGTCGGCCACACCGTGGCCGTTCACAAC    1       1.64    Root; d__Bacteria; p__Acidobacteria; c__Solibacteres; o__Solibacterales; f__Solibacteraceae; g__Candidatus_Solibacter; s__Candidatus_Solibacter_usitatus
```
* **Archive OTU table** - Similar to an OTU table with `--output-extras`, but in JSON form for machine readability.
* **SingleM package** - Reference data for one particular marker gene.
* **SingleM metapackage** - A collection of SingleM packages, with additional indices.
* **SingleM database** - An OTU table which has been converted to SQLite3 format and sequence similarity search indexes.

### FAQ
#### Can you target the 16S rRNA gene instead of the default set of single copy marker genes with SingleM?
Yes. By default, SingleM builds OTU tables from protein genes rather than 16S because this in general gives more strain-level resolution due to redundancy in the genetic code. If you are really keen on using 16S, then you can use SingleM with a 16S SingleM package (spkg). There is a [repository of auxiliary packages](https://github.com/wwood/singlem_extra_packages) at which includes a 16S package that is suitable for this purpose. The resolution won't be as high taxonomically, and there are issues around copy number variation, but it could be useful to use 16S for various reasons e.g. linking it to an amplicon study or using the GreenGenes taxonomy. For now there's no 16S spkg that gets installed by default, you have to use the `--singlem-packages` flag in `pipe` mode pointing to a separately downloaded package - see [https://github.com/wwood/singlem_extra_packages](https://github.com/wwood/singlem_extra_packages). Searching for 16S reads is also much slower than searching for protein-encoding reads.

#### How should SingleM be run on multiple samples?
There are two ways. It is possible to specify multiple input files to the `singlem pipe` subcommand directly by space separating them. Alternatively `singlem pipe` can be run on each sample and OTU tables combined using `singlem summarise`. The results should be identical, though there are some performance trade-offs. For large numbers of samples (>100) it is probably preferable to run each sample individually or in smaller groups.

#### What is the difference between the num_hits and coverage columns in the OTU table generated by the pipe mode?
`num_hits` is the number of reads found from the sample in that OTU. The
`coverage` is the expected coverage of a genome with that OTU sequence i.e. the
average number of bases covering each position in a genome after read mapping.
This is calculated from `num_hits`. In particular, `num_hits` is the 'kmer
coverage' formula used by genome assembly programs, and so `coverage` is
calculated according to the following formula, adapted from the one given in
the Velvet assembler's
[manual](https://raw.githubusercontent.com/dzerbino/velvet/master/Manual.pdf):

```
coverage = num_hits * L / (L - k + 1)
```

Where `L` is the length of a read and `k` is the length of the OTU sequence including inserts and gaps (usually `60` bp).


## License
SingleM is developed by the [Woodcroft lab](https://research.qut.edu.au/cmr/team/ben-woodcroft/) at the [Centre for Microbiome Research](https://research.qut.edu.au/cmr), School of Biomedical Sciences, QUT, with contributions several including [Samuel Aroney](https://github.com/AroneyS) and [Rossen Zhao](https://github.com/rzhao-2) and many others. It is licensed under [GPL3 or later](https://gnu.org/licenses/gpl.html).
