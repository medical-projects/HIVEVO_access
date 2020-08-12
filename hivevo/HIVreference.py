# vim: fdm=marker
'''
author:     Fabio Zanini/Richard Neher
date:       25/04/2015
content:    Data access module HIV patients.
'''
# Modules
import numpy as np
import pandas as pd
from Bio import SeqIO, AlignIO
from .sequence import alpha, alphaa
from .filenames import (get_custom_reference_filename,
                        get_subtype_reference_alignment_filename,
                        get_subtype_reference_allele_frequencies_filename)


class ReferenceTranslator(object):
    """docstring for ReferenceTranslater"""
    def __init__(self, ref1='HXB2', ref2='NL4-3'):
        super(ReferenceTranslator, self).__init__()
        self.ref1 = ref1
        self.ref2 = ref2

        self.refseq1 = SeqIO.read(get_custom_reference_filename(self.ref1, format='gb'), format='genbank').seq
        self.refseq2 = SeqIO.read(get_custom_reference_filename(self.ref2, format='gb'), format='genbank').seq

        from seqanpy import align_global
        (score, ali1, ali2) = align_global(str(self.refseq1), str(self.refseq2), band=200)
        self.count1 = np.cumsum(np.fromstring(ali1,'S1')!='-')-1
        self.count2 = np.cumsum(np.fromstring(ali2,'S1')!='-')-1

    def translate(self, pos, ref=None):
        if ref is None:
            ref = self.ref1
        if ref == self.ref1:
            ii = np.searchsorted(self.count1,pos)
            if ii<len(self.count2):
                return self.ref2, self.count2[ii]
            else:
                return self.ref2, -1
        elif ref ==self.ref2:
            ii = np.searchsorted(self.count2,pos)
            if ii<len(self.count1):
                return self.ref1, self.count1[ii]
            else:
                return self.ref1, -1
        else:
            print("unknown reference", ref)
            return "not found", np.nan



class HIVreference(object):
    """docstring for HIVreference"""
    def __init__(self, refname='HXB2', subtype='B', load_alignment=True):
        self.refname = refname
        self.subtype = subtype
        self.seq = SeqIO.read(get_custom_reference_filename(self.refname, format='gb'), format='genbank')
        # translate genbank encoded sequence features into a dictionary
        self.annotation = {x.qualifiers['note'][-1]:x for x in self.seq.features}

        if load_alignment:
            fn = get_subtype_reference_alignment_filename(subtype=subtype,
                                                          refname=refname)
            self.aln = np.array(AlignIO.read(fn, 'fasta'))
            self.calc_nucleotide_frequencies()

        else:
            fn = get_subtype_reference_allele_frequencies_filename(subtype=subtype,
                                                                   refname=refname)
            self.af = np.load(fn)

        self.consensus_indices = np.argmax(self.af, axis=0)
        self.consensus = alpha[self.consensus_indices]
        self.calc_entropy()


    def calc_nucleotide_frequencies(self):
        self.af = np.zeros((len(alpha)-1, self.aln.shape[1]), dtype=float)
        for ni, nuc in enumerate(alpha[:-1]):
            self.af[ni,:] = np.sum(self.aln==nuc.astype("U1"), axis=0)
        cov = np.sum(self.af, axis=0)
        self.af /= cov + 1e-10


    def calc_entropy(self):
        self.entropy = np.maximum(0,-np.sum(self.af*np.log(1e-10+self.af), axis=0))


    def map_to_sequence_collection():
        pass


    def get_ungapped(self, threshold=0.05):
        return self.af[-1,:] < 0.05


    def get_entropy_quantiles(self, q):
        from scipy.stats import scoreatpercentile
        thresholds = [scoreatpercentile(self.entropy, 100.0*i/q) for i in range(q+1)]
        return {i: {'range':(thresholds[i],thresholds[i+1]),
                    'ind':np.where((self.entropy>=thresholds[i])*(self.entropy<thresholds[i+1]))[0]}
               for i in range(q)}


    def get_entropy_in_patient_region(self, map_to_ref):
        '''
        returns entropy in a specific regions defined by a set of indices in the reference
        params:
        map_to_ref  --  either a one dimensional vector specifying indices in the reference
                        or a (3, len(region)) array with the reference coordinates in the first column
                        this is the output of Patient.map_to_external_reference
        '''
        if len(map_to_ref.shape) == 2:
            return self.entropy[map_to_ref[:, 0]]
        elif len(map_to_ref.shape) == 1:
            return self.entropy[map_to_ref]


    def get_consensus_in_patient_region(self, map_to_ref):
        '''
        returns consensus in a specific regions defined by a set of indices in the reference
        params:
        map_to_ref  --  either a one dimensional vector specifying indices in the reference
                        or a (3, len(region)) array with the reference coordinates in the first column
                        this is the output of Patient.map_to_external_reference
        '''
        if len(map_to_ref.shape) == 2:
            return self.consensus[map_to_ref[:, 0]]
        elif len(map_to_ref.shape) == 1:
            return self.consensus[map_to_ref]


    def get_consensus_indices_in_patient_region(self, map_to_ref):
        '''
        returns consensus_indices in a specific regions defined by a set of indices in the reference
        params:
        map_to_ref  --  either a one dimensional vector specifying indices in the reference
                        or a (3, len(region)) array with the reference coordinates in the first column
                        this is the output of Patient.map_to_external_reference
        '''
        if len(map_to_ref.shape) == 2:
            return self.consensus_indices[map_to_ref[:, 0]]
        elif len(map_to_ref.shape) == 1:
            return self.consensus_indices[map_to_ref]


class HIVreferenceAminoacid(object):
    def __init__(self, region, refname='HXB2', subtype='B'):
        self.region = region
        self.refname = refname
        self.subtype = subtype

        seq = SeqIO.read(get_custom_reference_filename(self.refname, format='gb'), format='genbank')
        # translate genbank encoded sequence features into a dictionary
        annotation = {x.qualifiers['note'][-1]:x for x in seq.features}
        self.seq = annotation[region].extract(seq)

        fn = get_subtype_reference_alignment_filename(region=region,
                                                      refname=refname,
                                                      subtype=self.subtype,
                                                      type='aa')
        self.aln = np.array(AlignIO.read(fn, 'fasta'))
        self.calc_aminoacid_frequencies()

        self.consensus_indices = np.argmax(self.af, axis=0)
        self.consensus = alphaa[self.consensus_indices]
        self.calc_entropy()


    def calc_aminoacid_frequencies(self):
        self.af = np.zeros((len(alphaa)-1, self.aln.shape[1]), dtype=float)
        for ai, aa in enumerate(alphaa[:-1]):
            self.af[ai,:] = np.sum(self.aln==aa, axis=0)
        cov = np.sum(self.af, axis=0)
        self.af /= cov


    def calc_entropy(self):
        self.entropy = np.maximum(0,-np.sum(self.af*np.log(1e-10+self.af), axis=0))


    def get_ungapped(self, threshold=0.05):
        return self.af[-1,:] < 0.05


    def get_entropy_quantiles(self, q):
        from scipy.stats import scoreatpercentile
        thresholds = [scoreatpercentile(self.entropy, 100.0*i/q) for i in range(q+1)]
        return {i: {'range':(thresholds[i],thresholds[i+1]),
                    'ind':np.where((self.entropy>=thresholds[i])*(self.entropy<thresholds[i+1]))[0]}
               for i in range(q)}


    def get_entropy_in_patient_region(self, map_to_ref):
        '''
        returns entropy in a specific regions defined by a set of indices in the reference
        params:
        map_to_ref  --  either a one dimensional vector specifying indices in the reference
                        or a (2, len(region)) array with the reference coordinates in the first column
                        this is the output of Patient.map_to_external_reference_aminoacids
        '''
        if len(map_to_ref.shape) == 2:
            return self.entropy[map_to_ref[:, 0]]
        elif len(map_to_ref.shape) == 1:
            return self.entropy[map_to_ref]


    def get_consensus_in_patient_region(self, map_to_ref):
        '''
        returns consensus in a specific regions defined by a set of indices in the reference
        params:
        map_to_ref  --  either a one dimensional vector specifying indices in the reference
                        or a (2, len(region)) array with the reference coordinates in the first column
                        this is the output of Patient.map_to_external_reference_aminoacids
        '''
        if len(map_to_ref.shape) == 2:
            return self.consensus[map_to_ref[:, 0]]
        elif len(map_to_ref.shape) == 1:
            return self.consensus[map_to_ref]


    def get_consensus_indices_in_patient_region(self, map_to_ref):
        '''
        returns consensus_indices in a specific regions defined by a set of indices in the reference
        params:
        map_to_ref  --  either a one dimensional vector specifying indices in the reference
                        or a (2, len(region)) array with the reference coordinates in the first column
                        this is the output of Patient.map_to_external_reference_aminoacids
        '''
        if len(map_to_ref.shape) == 2:
            return self.consensus_indices[map_to_ref[:, 0]]
        elif len(map_to_ref.shape) == 1:
            return self.consensus_indices[map_to_ref]
