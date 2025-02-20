import re
import os
import csv
import logging
import itertools
import pkg_resources
import extern
import tempfile


class OrfMUtils:
    def un_orfm_name(self, name):
        return re.sub('_\d+_\d+_\d+$', '', name)


class TaxonomyFile:
    def __init__(self, taxonomy_file_path):
        self.sequence_to_taxonomy = {}
        utils = OrfMUtils()
        with open(taxonomy_file_path) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.sequence_to_taxonomy[\
                      utils.un_orfm_name(row[0])] = row[1]

    def __getitem__(self, item):
        return self.sequence_to_taxonomy[item]

    def merge(self, another_taxonomy_file):
        for key, value in another_taxonomy_file.sequence_to_taxonomy.items():
            if key not in self.sequence_to_taxonomy:
                self.sequence_to_taxonomy[key] = value


class FastaNameToSampleName:
    @staticmethod
    def fasta_to_name(query_sequences_file):
        sample_name = os.path.basename(query_sequences_file)
        for extension in ('.fna.gz','.fq.gz','.fastq.gz','.fasta.gz','.fna','.fq','.fastq','.fasta'):
            if sample_name.endswith(extension):
                sample_name = sample_name[0:(len(sample_name)-len(extension))]
                break
        return sample_name
