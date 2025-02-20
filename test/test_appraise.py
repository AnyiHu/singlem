
#!/usr/bin/env python3

#=======================================================================
# Authors: Ben Woodcroft
#
# Unit tests.
#
# Copyright
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.
# If not, see <http://www.gnu.org/licenses/>.
#=======================================================================

import unittest
import os.path
import sys
from io import StringIO
import tempfile

path_to_script = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','bin','singlem')
path_to_data = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data')
DEFAULT_WINDOW_SIZE = 60

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path
from singlem.appraiser import Appraiser
from singlem.otu_table_collection import OtuTableCollection
from singlem.otu_table import OtuTable
from singlem.metapackage import Metapackage

class Tests(unittest.TestCase):
    headers = str.split('gene sample sequence num_hits coverage taxonomy')
    maxDiff = None

    def setUp(self):
        OtuTable._clear_cache()

    def _sort_appraisal_results(self, appraisal_results):
        sorted_appraisal_results = list(sorted(
            appraisal_results,
            key=lambda x: (x.metagenome_sample_name, x.num_binned, x.num_assembled, x.num_not_found)))
        return sorted_appraisal_results

    def test_hello_world(self):
        metagenome_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','minimal','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(1, len(app.appraisal_results))
        a = app.appraisal_results[0]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual(1, len(a.binned_otus))
        self.assertEqual('GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                         a.binned_otus[0].sequence)
        self.assertEqual(1, len(a.not_found_otus))
        self.assertEqual('CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG',
                         a.not_found_otus[0].sequence)

    def test_multiple_samples(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)
        a = res[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)

    def test_clusterer_all_cluster_all_good(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATT','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATA','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 sequence_identity=0.5,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(1, len(app.appraisal_results))
        a = app.appraisal_results[0]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(11/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)


    def test_clusterer_all_cluster_some_good(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','minimal',     'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATA','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 sequence_identity=0.7,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(1, len(app.appraisal_results))
        a = app.appraisal_results[0]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)


    def test_clusterer_all_cluster_two_samples(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','maximal',     'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATA','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 sequence_identity=0.7,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        res = sorted(app.appraisal_results)
        self.assertEqual(2, len(app.appraisal_results))
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)
        self.assertEqual(1, len(a.binned_otus))
        self.assertEqual('GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                         a.binned_otus[0].sequence)
        self.assertEqual(0, len(a.not_found_otus))
        a = res[0]
        self.assertEqual('maximal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)
        self.assertEqual(1, len(a.not_found_otus))
        self.assertEqual('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                         a.not_found_otus[0].sequence)
        self.assertEqual(0, len(a.binned_otus))


    def test_clusterer_all_cluster_two_samples_some_cluster(self):
        # non-As and genome cluster together but are not exactly the same
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.12.ribosomal_protein_L11_rplK','minimal','AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','12','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','maximal',     'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'],
                    ['4.11.ribosomal_protein_L10','maximal',     'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATG','5','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATA','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
                    ['4.11.ribosomal_protein_L10','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATT','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 sequence_identity=0.7,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(12/4)}, a.num_not_found)
        self.assertEqual(1, len(a.binned_otus))
        self.assertEqual(1, len(a.not_found_otus))
        self.assertEqual('GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                         a.binned_otus[0].sequence)
        self.assertEqual('minimal',
                         a.binned_otus[0].sample_name)
        self.assertEqual('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                         a.not_found_otus[0].sequence)
        self.assertEqual('minimal',
                         a.not_found_otus[0].sample_name)

        a = res[0]
        self.assertEqual('maximal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(5/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)
        self.assertEqual(1, len(a.binned_otus))
        self.assertEqual(1, len(a.not_found_otus))
        self.assertEqual('GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATG',
                         a.binned_otus[0].sequence)
        self.assertEqual('maximal',
                         a.binned_otus[0].sample_name)
        self.assertEqual('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                         a.not_found_otus[0].sequence)
        self.assertEqual('maximal',
                         a.not_found_otus[0].sample_name)

    def test_print_appraisal(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)
        a = res[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)

        to_print = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print)
        self.assertEqual("sample\tdomain\tnum_binned\tnum_not_found\tpercent_binned\nminimal\td__Archaea\t0\t0\t0.0\nminimal\td__Bacteria\t2\t0\t100.0\nanother\td__Archaea\t0\t0\t0.0\nanother\td__Bacteria\t0\t1\t0.0\ntotal\td__Archaea\t0\t0\t0.0\naverage\td__Archaea\t0.0\t0.0\tnan\ntotal\td__Bacteria\t2\t1\t66.7\naverage\td__Bacteria\t1.0\t0.5\t50.0\n", to_print.getvalue())

        to_print = StringIO()
        found_otu_table_io = StringIO()
        not_found_otu_table_io = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print,
                                  binned_otu_table_io=found_otu_table_io,
                                  unaccounted_for_otu_table_io=not_found_otu_table_io)
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'])
                          ])+"\n",
                         found_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'])])+"\n",
                         not_found_otu_table_io.getvalue())

    def test_print_assembly_appraise(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        assembly_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        assemblies = "\n".join(["\t".join(x) for x in assembly_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        assembly_collection = OtuTableCollection()
        assembly_collection.add_otu_table(StringIO(assemblies))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 assembly_otu_table_collection=assembly_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)

        to_print = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print, doing_assembly=True)
        self.assertEqual("sample\tdomain\tnum_binned\tnum_assembled\tnum_not_found\tpercent_binned\tpercent_assembled\nminimal\td__Archaea\t0\t0\t0\t0.0\t0.0\nminimal\td__Bacteria\t0\t2\t0\t0.0\t100.0\nanother\td__Archaea\t0\t0\t0\t0.0\t0.0\nanother\td__Bacteria\t0\t0\t1\t0.0\t0.0\ntotal\td__Archaea\t0\t0\t0\t0.0\t0.0\naverage\td__Archaea\t0.0\t0.0\t0.0\tnan\tnan\ntotal\td__Bacteria\t0\t2\t1\t0.0\t66.7\naverage\td__Bacteria\t0.0\t1.0\t0.5\t0.0\t50.0\n", to_print.getvalue())

        to_print = StringIO()
        found_otu_table_io = StringIO()
        not_found_otu_table_io = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print,
                                  doing_assembly=True,
                                  assembled_otu_table_io=found_otu_table_io,
                                  unaccounted_for_otu_table_io=not_found_otu_table_io)
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'])
                          ])+"\n",
                         found_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'])])+"\n",
                         not_found_otu_table_io.getvalue())

        # Check that unbinned is the same as assembled OTUs when no binning is done
        to_print = StringIO()
        assembled_otu_table_io = StringIO()
        unbinned_otu_table_io = StringIO()
        not_found_otu_table_io = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print,
                                  doing_assembly=True,
                                  assembled_otu_table_io=assembled_otu_table_io,
                                  unbinned_otu_table_io=unbinned_otu_table_io,
                                  unaccounted_for_otu_table_io=not_found_otu_table_io)
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'])
                          ])+"\n",
                         assembled_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'])
                          ])+"\n",
                         unbinned_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'])])+"\n",
                         not_found_otu_table_io.getvalue())


    def test_print_assembly_appraise_all_binned(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        assembly_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        assemblies = "\n".join(["\t".join(x) for x in assembly_otu_table])

        genomes = assemblies

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        assembly_collection = OtuTableCollection()
        assembly_collection.add_otu_table(StringIO(assemblies))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 assembly_otu_table_collection=assembly_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)
        a = res[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(4/4)}, a.num_not_found)

        to_print = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print, doing_assembly=True)
        self.assertEqual("sample\tdomain\tnum_binned\tnum_assembled\tnum_not_found\tpercent_binned\tpercent_assembled\nminimal\td__Archaea\t0\t0\t0\t0.0\t0.0\nminimal\td__Bacteria\t2\t2\t0\t100.0\t100.0\nanother\td__Archaea\t0\t0\t0\t0.0\t0.0\nanother\td__Bacteria\t0\t0\t1\t0.0\t0.0\ntotal\td__Archaea\t0\t0\t0\t0.0\t0.0\naverage\td__Archaea\t0.0\t0.0\t0.0\tnan\tnan\ntotal\td__Bacteria\t2\t2\t1\t66.7\t66.7\naverage\td__Bacteria\t1.0\t1.0\t0.5\t50.0\t50.0\n", to_print.getvalue())

        # Check that unbinned is the same as assembled OTUs when no binning is done
        to_print = StringIO()
        assembled_otu_table_io = StringIO()
        unbinned_otu_table_io = StringIO()
        not_found_otu_table_io = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print,
                                  doing_assembly=True,
                                  assembled_otu_table_io=assembled_otu_table_io,
                                  unbinned_otu_table_io=unbinned_otu_table_io,
                                  unaccounted_for_otu_table_io=not_found_otu_table_io)
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'])
                          ])+"\n",
                         assembled_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          ])+"\n",
                         unbinned_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers),
                          "\t".join(['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'])])+"\n",
                         not_found_otu_table_io.getvalue())

    def test_print_appraisal_output_found_in(self):
        metagenome_otu_table = [self.headers,
                    ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])

        genomes_otu_table = [self.headers,['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']
                    ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 output_found_in=True,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[1]
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual('genome', a.binned_otus[0].data[a.binned_otus[0].fields.index('found_in')])
        a = res[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual('', a.not_found_otus[0].data[a.not_found_otus[0].fields.index('found_in')])

        to_print = StringIO()
        found_otu_table_io = StringIO()
        not_found_otu_table_io = StringIO()
        appraiser.print_appraisal(app, packages, True, to_print,
                                  binned_otu_table_io=found_otu_table_io,
                                  unaccounted_for_otu_table_io=not_found_otu_table_io,
                                  output_found_in=True)
        self.assertEqual("\n".join([
                          "\t".join(self.headers + ['found_in']),
                          "\t".join(['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales', 'genome'])
                          ])+"\n",
                         found_otu_table_io.getvalue())
        self.assertEqual("\n".join([
                          "\t".join(self.headers + ['found_in']),
                          "\t".join(['4.11.ribosomal_protein_L10','another','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus', ''])])+"\n",
                         not_found_otu_table_io.getvalue())

    def test_contamination(self):
        metagenome_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'minimal',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
            [
                '4.16.ribosomal_protein_S5',
                'minimal',
                'GGTACCGGCGTCATCGCCGGTGGCGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '8','12.50','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])
        genomes_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'AGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC', #one base pair different to the one above
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.16.ribosomal_protein_S5',
                'genome',
                'GGTACCGGCGTCATCGCCGGTGGCGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '1','1.06','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']
        ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(1, len(app.appraisal_results))
        a = app.appraisal_results[0]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(8/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_not_found)


    def test_contamination_near_enough(self):
        metagenome_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'minimal',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
            [
                '4.16.ribosomal_protein_S5',
                'another',
                'GGTACCGGCGTCATCGCCGGTGGCGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '8','12.50','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])
        genomes_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'AGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC', #one base pair different to the one above
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.16.ribosomal_protein_S5',
                'genome',
                'GGTACCGGCGTCATCGCCGGTGGGGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',#one base pair different to the one above
                '1','1.06','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']
        ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[0]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(8/4)}, a.num_not_found)
        a = res[1]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_not_found)

        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 sequence_identity=0.9,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        def compare_res(res): return res.metagenome_sample_name
        sorted_results = list(sorted(app.appraisal_results, key=compare_res))
        a = sorted_results[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(8/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)
        a = sorted_results[1]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_not_found)

    def test_for_concatenated_genomes(self):
        metagenome_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'minimal',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
            [
                '4.16.ribosomal_protein_S5',
                'another',
                'GGTACCGGCGTCATCGCCGGTGGCGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '8','12.50','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])
        genomes_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.16.ribosomal_protein_S5',
                'genome',
                'GGTACCGGCGTCATCGCCGGTGGGGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',#one base pair different to the one above
                '1','1.06','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria'],
            [
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.16.ribosomal_protein_S5',
                'genome',
                'GGTACCGGCGTCATCGCCGGTGGGGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',#one base pair different to the one above
                '1','1.06','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']
        ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = sorted(app.appraisal_results)
        a = res[0]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(8/4)}, a.num_not_found)
        a = res[1]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_not_found)

    def test_assembly_input(self):
        metagenome_otu_table = [
            self.headers,
            ['4.12.ribosomal_protein_L11_rplK','minimal','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
            ['4.11.ribosomal_protein_L10','minimal','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'],
            ['4.14.ribosomal_protein_L16_L10E_rplP','minimal','CAAAAAAAAAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','5','10.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])
        assembly_otu_table = [
            self.headers,
            ['4.12.ribosomal_protein_L11_rplK','assembly','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.007','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
            ['4.11.ribosomal_protein_L10','assembly','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','1','1.01','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']]
        assemblies = "\n".join(["\t".join(x) for x in assembly_otu_table])

        genomes_otu_table = [
            self.headers,
            ['4.12.ribosomal_protein_L11_rplK','genome','GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC','1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli']]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        assembly_collection = OtuTableCollection()
        assembly_collection.add_otu_table(StringIO(assemblies))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 assembly_otu_table_collection=assembly_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(1, len(app.appraisal_results))
        a = app.appraisal_results[0]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(11/4)}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(5/4)}, a.num_not_found)
        self.assertEqual('minimal', a.metagenome_sample_name)
        self.assertEqual(1, len(a.binned_otus))
        self.assertEqual('GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                         a.binned_otus[0].sequence)
        self.assertEqual(2, len(a.assembled_otus))
        self.assertEqual(sorted(['GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                                 'CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG']),
                         sorted([o.sequence for o in a.assembled_otus]))
        self.assertEqual(1, len(a.not_found_otus))
        self.assertEqual('CAAAAAAAAAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG',
                         a.not_found_otus[0].sequence)

    @unittest.skip("SRA otu tables have SingleM packages not in four_package.smpkg")
    def test_appraise_plot_real_data(self):
        """Not a real test, just developing the code"""
        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        with open(os.path.join(path_to_data, 'appraise_example2', 'SRR5040536.reads.long_sample_names.otu_table.csv')) as f:
            metagenome_collection.add_otu_table(f)
        genome_collection = OtuTableCollection()
        with open(os.path.join(path_to_data, 'appraise_example2', 'SRR5040536.binned.otu_table.csv')) as f:
            genome_collection.add_otu_table(f)
        assembly_collection = OtuTableCollection()
        with open(os.path.join(path_to_data, 'appraise_example2', 'SRR5040536.assembly.otu_table.csv')) as f:
            assembly_collection.add_otu_table(f)
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 assembly_otu_table_collection=assembly_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)

        with tempfile.NamedTemporaryFile(mode='w',suffix='.svg',prefix='single_test_appraisal.') as f:
            app.plot(
                output_svg_base='/tmp/a.svg',#f.name,
                cluster_identity = 0.89,
                doing_assembly=True,
                doing_binning=True
            )

    def test_appraise_assembly_imperfectly(self):
        metagenome_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'minimal',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '7','17.07','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
            [
                '4.16.ribosomal_protein_S5',
                'another',
                'GGTACCGGCGTCATCGCCGGTGGCGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '8','12.50','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria'],
            [
                '4.16.ribosomal_protein_S5',
                'another',
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATGGCCGGCATCCGC', # way different to the one above
                '9','17.50','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']]
        metagenomes = "\n".join(["\t".join(x) for x in metagenome_otu_table])
        genomes_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.12.ribosomal_protein_L11_rplK',
                'genome',
                'AGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC', #one base pair different to the one above
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.16.ribosomal_protein_S5',
                'genome',
                'GGTACCGGCGTCATCGCCGGTGGGGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '1','1.06','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']
        ]
        genomes = "\n".join(["\t".join(x) for x in genomes_otu_table])
        assemblies_otu_table = [
            self.headers,[
                '4.12.ribosomal_protein_L11_rplK',
                'assembly',
                'GGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC',
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.12.ribosomal_protein_L11_rplK',
                'assembly',
                'AGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATC', #one base pair different to the one above
                '1','1.02','Root; d__Bacteria; p__Firmicutes; c__Bacilli'],
            [
                '4.16.ribosomal_protein_S5',
                'assembly',
                'GGTACCGGCGTCATCGCCGGTGGGGCGGCACGCGCCATCTTGGAGATGGCCGGCATCCGC',
                '1','1.06','Root; d__Bacteria; p__Actinobacteria; c__Actinobacteria']
        ]
        assemblies = "\n".join(["\t".join(x) for x in assemblies_otu_table])

        appraiser = Appraiser()
        metagenome_collection = OtuTableCollection()
        metagenome_collection.add_otu_table(StringIO(metagenomes))
        genome_collection = OtuTableCollection()
        genome_collection.add_otu_table(StringIO(genomes))
        assembly_collection = OtuTableCollection()
        assembly_collection.add_otu_table(StringIO(assemblies))
        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 assembly_otu_table_collection=assembly_collection,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = self._sort_appraisal_results(app.appraisal_results)
        a = res[0]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round((8+9)/4)}, a.num_not_found)
        a = res[1]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)

        packages = Metapackage.acquire(os.path.join(path_to_data, 'four_package.smpkg')).singlem_packages
        app = appraiser.appraise(genome_otu_table_collection=genome_collection,
                                 metagenome_otu_table_collection=metagenome_collection,
                                 assembly_otu_table_collection=assembly_collection,
                                 sequence_identity=0.9,
                                 packages=packages,
                                 window_size=DEFAULT_WINDOW_SIZE)
        self.assertEqual(2, len(app.appraisal_results))
        res = self._sort_appraisal_results(app.appraisal_results)
        a = res[0]
        self.assertEqual('another', a.metagenome_sample_name)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(8/4)}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(8/4)}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(9/4)}, a.num_not_found)
        a = res[1]
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_binned)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': round(7/4)}, a.num_assembled)
        self.assertEqual({'d__Archaea': 0, 'd__Bacteria': 0}, a.num_not_found)


if __name__ == "__main__":
    unittest.main()
