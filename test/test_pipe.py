#!/usr/bin/env python

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
import subprocess
import os.path
import tempfile
import tempdir
from string import split
import extern
import sys
import json

path_to_script = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','bin','singlem')
path_to_data = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data')

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path
from singlem.pipe import SearchPipe

class Tests(unittest.TestCase):
    headers = split('gene sample sequence num_hits coverage taxonomy')
    maxDiff = None

    def test_minimal(self):
        expected = [
            self.headers,
            ['4.11.ribosomal_protein_L10','minimal','TTACGTTCACAATTACGTGAAGCTGGTGTTGAGTATAAAGTATACAAAAACACTATGGTA','2','4.88','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus'],
            ['4.12.ribosomal_protein_L11_rplK','minimal','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales']]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --debug pipe --sequences %s/1_pipe/minimal.fa --otu_table /dev/stdout --threads 4" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(extern.run(cmd).split("\n")))
       
    def test_insert(self):
        expected = [self.headers,['4.12.ribosomal_protein_L11_rplK','insert','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','2','4.95','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales']]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --quiet pipe --sequences %s/1_pipe/insert.fna --otu_table /dev/stdout --threads 4" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(subprocess.check_output(cmd, shell=True).split("\n")))
        
    def test_print_insert(self):
        expected = [self.headers,['4.12.ribosomal_protein_L11_rplK','insert','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','1','2.44','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.12.ribosomal_protein_L11_rplK','insert','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTtttCAAGCAGGTGTG','1','2.51','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales']]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --debug pipe --sequences %s/1_pipe/insert.fna --otu_table /dev/stdout --threads 4 --include_inserts" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(extern.run(cmd).split("\n")))
            
    def test_known_tax_table(self):
        expected = [self.headers,['4.12.ribosomal_protein_L11_rplK','minimal','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales'],
                    ['4.11.ribosomal_protein_L10','minimal','TTACGTTCACAATTACGTGAAGCTGGTGTTGAGTATAAAGTATACAAAAACACTATGGTA','2','4.88','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --quiet pipe --sequences %s/1_pipe/minimal.fa --otu_table /dev/stdout --threads 4" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(subprocess.check_output(cmd, shell=True).split("\n")))
        
        expected = [self.headers,['4.12.ribosomal_protein_L11_rplK','minimal','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','some1'],
                    ['4.11.ribosomal_protein_L10','minimal','TTACGTTCACAATTACGTGAAGCTGGTGTTGAGTATAAAGTATACAAAAACACTATGGTA','2','4.88','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Staphylococcaceae; g__Staphylococcus']
                    ]
        exp = sorted(["\t".join(x) for x in expected]+[''])
        
        with tempfile.NamedTemporaryFile(prefix='singlem_test_known') as t:
            t.write('\n'.join(["\t".join(x) for x in expected[:2]]))
            t.flush() 

            cmd = "%s --quiet pipe --sequences %s/1_pipe/minimal.fa --otu_table /dev/stdout --threads 4 --known_otu_tables %s"\
                 % (path_to_script,
                    path_to_data,
                    t.name)
            self.assertEqual(exp, sorted(extern.run(cmd).split("\n")))
            
    def test_diamond_assign_taxonomy(self):
        with tempfile.NamedTemporaryFile(suffix='.fasta') as f:
            query = "\n".join(['>HWI-ST1243:156:D1K83ACXX:7:1109:18214:9910 1:N:0:TCCTGAGCCTAAGCCT',
                'GTTAAATTACAAATTCCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTGAACATCATGGGATTCTGTAAAGAGT',''])
            f.write(query)
            f.flush()
            
            cmd = "%s --debug pipe --sequences %s --otu_table /dev/stdout --assignment_method diamond --threads 4" % (path_to_script,
                                                            f.name)
            
            expected = [self.headers,['4.12.ribosomal_protein_L11_rplK',os.path.basename(f.name)[:-6],'CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','1','2.44','Root; d__Bacteria; p__Firmicutes; c__Bacilli; o__Bacillales; f__Bacillaceae; g__Bacillus; s__Bacillus_sp._1NLA3E']]
            expected = ["\t".join(x) for x in expected]+['']
            observed = extern.run(cmd).split("\n")
            self.assertEqual(expected, observed)
            
    def test_diamond_example_assign_taxonomy(self):
        expected = [self.headers,['4.12.ribosomal_protein_L11_rplK','minimal','CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG','4','9.76','2506520047'],
                    ['4.11.ribosomal_protein_L10','minimal','TTACGTTCACAATTACGTGAAGCTGGTGTTGAGTATAAAGTATACAAAAACACTATGGTA','2','4.88','2541047520']
                    ]
        exp = sorted(["\t".join(x) for x in expected]+[''])

        cmd = "%s --debug pipe --sequences %s/1_pipe/minimal.fa --otu_table /dev/stdout --threads 4 --assignment_method diamond_example" % (path_to_script,
                                                                                                    path_to_data)
        self.assertEqual(exp, sorted(extern.run(cmd).split("\n")))
        
    def test_one_read_two_orfs_two_diamond_hits(self):
        # what a pain the real world is
        seq = '''>HWI-ST1240:128:C1DG3ACXX:7:2204:6599:65352 1:N:0:GTAGAGGATAGATCGC
ACCCACAGCTCGGGGTTGCCCTTGCCCGACCCCATGCGTGTCTCGGCGGGCTTCTGGTGACGGGCTTGTCCGGGAAGACGCGGATCCAGACCTTGCCTCCGCGCTTGACGTGCCGGGTCATCGCGATACGGGCCGCCTCGATCTGACGTGC
'''
        expected = [
            self.headers,
            ['4.14.ribosomal_protein_L16_L10E_rplP		CGCGTCTTCCCGGACAAGCCCGTCACCAGAAGCCCGCCGAGACACGCATGGGGTCGGGCA	1	1.64	2509601019']]
        exp = sorted(["\t".join(x) for x in expected]+[''])
        with tempfile.NamedTemporaryFile(prefix='singlem_test',suffix='.fa') as t:
            t.write(seq)
            t.flush()
            cmd = "%s --quiet pipe --sequences %s --otu_table /dev/stdout --threads 4 --assignment_method diamond_example" % (path_to_script,
                                                                                                    t.name)
            self.assertEqual(exp,
                             sorted(extern.run(cmd).
                                    replace(
                                        os.path.basename(t.name).replace('.fa',''),
                                        '').
                                    split("\n")))

    def test_jplace_output(self):
        expected_jpace = {u'fields': [u'classification',
  u'distal_length',
  u'edge_num',
  u'like_weight_ratio',
  u'likelihood',
  u'pendant_length'],
 u'metadata': 'the_metadata',
 u'placements': {u'CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG': {u'nm': [[u'CCTGCAGGTAAAGCGAATCCAGCACCACCAGTTGGTCCAGCATTAGGTCAAGCAGGTGTG',
     2]],
   u'p': [[u'g__Bacillus',
     8.59375e-06,
     178,
     0.142857142864,
     -19892.7622511,
     0.322551664432],
    [u'g__Bacillus',
     8.59375e-06,
     179,
     0.142857142864,
     -19892.7622511,
     0.322551664432],
    [u'g__Bacillus',
     8.59375e-06,
     254,
     0.142857142864,
     -19892.7622511,
     0.322551674793],
    [u'g__Virgibacillus',
     8.59375e-06,
     304,
     0.142857142864,
     -19892.7622511,
     0.322551394722],
    [u'g__Virgibacillus',
     8.59375e-06,
     305,
     0.142857142864,
     -19892.7622511,
     0.322551394722],
    [u'g__Exiguobacterium',
     8.59375e-06,
     376,
     0.142857142864,
     -19892.7622511,
     0.322551677204],
    [u'g__Brevibacillus',
     0.0005315625,
     324,
     0.142857142818,
     -19892.7622511,
     0.32255147376]]}},
 u'tree': 'tree_thanks',
 u'version': 3}
        
        with tempdir.TempDir() as d:
            cmd = "%s pipe --sequences %s --otu_table /dev/null --output_jplace %s" % (
                path_to_script,
                os.path.join(path_to_data,'1_pipe','jplace_test.fna'),
                os.path.join(d, "my_jplace"))
            extern.run(cmd)
            j = json.load(open(
                os.path.join(d, 'my_jplace_jplace_test_4.12.ribosomal_protein_L11_rplK.jplace')))
            j['tree'] = 'tree_thanks'
            j['metadata'] = 'the_metadata'
            self.assertEqual(expected_jpace, j)

    def test_nucleotide_package(self):
        inseqs = '''>HWI-ST1243:156:D1K83ACXX:7:1105:6981:63483 1:N:0:AAGAGGCAAAGGAGTA
GATATGGAGGAACACCAGTGGCGAAGGCGACTTTCTGGTCTGTAACTGACGCTGATGTGC
>HWI-ST1243:156:D1K83ACXX:7:1109:8070:99586 1:N:0:CGTACTAGCTAAGCCT
CAGAGATATGGAGGAACACCAGTGGCGAAGGCGACTTTCTGGTCTGTAACTGACGCTGAT
>HWI-ST1243:156:D1K83ACXX:7:1106:7275:39452 1:N:0:GTAGAGGAAAGGAGTA
GATATGGAGGAACACCAGTGGCGAAGGCGACTTTCTGGTCTGTAACTGGCGCTGATGTGC
>HWI-ST1243:156:D1K83ACXX:7:1106:4406:71922 1:N:0:TCCTGAGCCTAAGCCT
GAGATATGGAGGAACACCAGTGGCGAAGGCGACTTTCTGGTCTGTAACTGACGCTGATGT
'''
        with tempfile.NamedTemporaryFile(suffix='.fa') as n:
            n.write(inseqs)
            n.flush()

            cmd = "%s pipe --sequences %s --otu_table /dev/stdout --singlem_packages %s" % (
                path_to_script, n.name, os.path.join(path_to_data,'61_otus.v3.gpkg.spkg'))
            extern.run(cmd)


if __name__ == "__main__":
    unittest.main()
