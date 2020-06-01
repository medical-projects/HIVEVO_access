# vim: fdm=indent
'''
author:     Fabio Zanini
date:       20/05/15
content:    Support module for file names and paths.
'''
# Modules
import os


# Globals

# Data folder: use env variable if found, else fallback onto standard locations
if 'HIVEVO_ROOT_DATA_FOLDER' in os.environ:
    root_data_folder = os.environ['HIVEVO_ROOT_DATA_FOLDER']

# USB disk
elif os.path.isdir('/media/FZ_MPI/HIV_Sweden/'):
    root_data_folder = '/media/FZ_MPI/HIV_Sweden/'

# Web server
elif os.path.isdir('/var/www/hivwholeweb/'):
    root_data_folder = '/var/www/hivwholeweb/app/hiv/static/data/'

# Fabio's hard drive
elif os.path.isdir('/home/fabio/') and (not os.path.isdir('/ebio/ag-neher/share/data')):
    root_data_folder = '/home/fabio/university/phd/sequencing/data/'

# MPI's or BZs file server
else:
    root_data_folder = '/scicore/home/neher/GROUP/data/MiSeq_HIV_Karolinska/'
    #root_data_folder = '/ebio/ag-neher/share/data/MiSeq_HIV_Karolinska/'

root_data_folder = root_data_folder.rstrip(os.path.sep)+os.path.sep

# NOTE: we use the website folder for consistency
# NOTE: the website folder does not include cross-sectional alignments and stuff
reference_folder = root_data_folder+'reference/'
root_data_folder = root_data_folder+'website/'


# NOTE: this is a bit of a hack
import hivevo
self = os.path.abspath(hivevo.__path__[0])+'/'
if os.path.isdir(self+'hivevo'):
    local_data_folder = self + 'data/'
else:
    local_data_folder = self + '../data/'

table_folder = local_data_folder + 'tables/'



# Functions
def get_table_filename(kind, format='tsv'):
    return table_folder+kind+'.'+format


def get_sample_table_filenames(pnames=None):
    import glob
    if pnames is None:
        return glob.glob(table_folder+'samples_*.tsv')
    else:
        return [table_folder+'samples_'+pname+'.tsv' for pname in pnames]


def get_custom_reference_filename(reference, format='fasta'):
    '''Get the filename of a custom reference sequence'''
    filename = reference
    filename = filename+'.'+format
    return reference_folder+filename


def get_subtype_reference_alignment_filename(subtype='B', format='fasta', refname='HXB2',
                                             type='nuc', region='genomewide'):
    '''Get the filename of a reference alignment'''
    filename = region+'.'+subtype+'.'+type+'.aligned.'+format
    return reference_folder+'alignments/pairwise_to_'+refname+'/'+filename


def get_subtype_reference_allele_frequencies_filename(subtype='B', format='npy', refname='HXB2'):
    '''Get the filename of a reference alignment'''
    filename = 'genomewide.'+subtype+'.nuc.aligned_afs'+'.'+format
    return reference_folder+'alignments/pairwise_to_'+refname+'/'+filename


def get_subtype_reference_entropy_filename(subtype='B', format='npy', refname='HXB2'):
    '''Get the filename of a reference alignment'''
    filename = 'genomewide.'+subtype+'.nuc.aligned_afs'+'.'+format
    return reference_folder+'alignments/pairwise_to_'+refname+'/'+filename


def get_ctl_epitope_map_filename(pcode):
    '''Get the filename of the CTL epitope predictions from MHCi'''
    filename = root_data_folder+'CTL/mhci/ctl_'+pcode+'.tsv'
    return filename


def get_allele_counts_filename(samplename, region,
                               type='nuc',
                               format='npy'):
    '''Get the filename of the allele counts for a patient sample'''
    filename = ('allele_counts_'+
                samplename+'_'+
                region+
                '.'+format)

    if type == 'nuc':
        filename = 'single_nucleotide_variants/'+filename
    elif type == 'aa':
        filename = 'single_aminoacid_variants/'+filename
    elif type == 'codon':
        filename = 'single_codon_variants/'+filename
    else:
        raise ValueError('Data type not understood')

    filename = root_data_folder+filename

    return filename


def get_insertions_filename(samplename, region):
    '''Get the filename of the insertions for a patient sample'''
    filename = ('insertions_'+
                samplename+'_'+
                region+
                '.pickle')
    filename = 'insertions/'+filename
    filename = root_data_folder+filename
    return filename


def get_allele_cocounts_filename(samplename, region,
                               type='nuc',
                               format='npy'):
    '''Get the filename of the allele counts for a patient sample'''
    filename = ('cocounts_'+
                samplename+'_'+
                region+
                '.'+format)

    if type == 'nuc':
        filename = 'pair_nucleotide_variants/'+filename
    elif type == 'aa':
        filename = 'pair_aminoacid_variants/'+filename
    elif type == 'codon':
        filename = 'pair_codon_variants/'+filename
    else:
        raise ValueError('Data type not understood')

    filename = root_data_folder+filename

    return filename


def get_mapped_filtered_filename(samplename, fragment, format='bam'):
    '''Get the filename of the mapped and filtered reads to initial reference'''
    filename = samplename+'_'+fragment+'.'+format
    filename = root_data_folder+'reads/'+filename
    return filename


def get_initial_reference_filename(pname, fragment, format='fasta'):
    '''Get the filename of the initial reference for a patient'''
    filename = 'reference_'+pname+'_'+fragment+'.'+format
    filename = root_data_folder+'sequences/'+filename
    return filename


def get_coordinate_map_filename(pname, refname='HXB2', format='tsv'):
    '''Get the filename of the map to HXB2 or other ref coordinates'''
    filename = 'coordinate_map_'+pname+'_'+refname+'_genomewide.'+format
    filename = root_data_folder+'coordinate_maps/'+filename
    return filename


def get_haplotype_alignment_filename(pname, region, format='fasta'):
    '''Get the filenae of a haplotype alignment'''
    if region[:len('insertion_')] == 'insertion_':
        filename = 'haplotype_alignment_'+pname+'_'+region[len('insertion_'):]+'.'+format
        filename = 'insertions/'+filename
    else:
        filename = 'haplotype_alignment_'+pname+'_'+region+'.'+format
        filename = 'alignments/'+filename
    filename = root_data_folder+filename
    return filename

