# This class is depreciated by the complete transition to the
# new conceptual framework - where collections will only be family objects

from uchicagoldr.batch import AccessionDirectory
from uchicagoldr.item import AccessionItem
from uchicagoldr.batch import Batch
from uchicagoldr.item import Item

class Collection(object):
    def __init__(self, init_accessions=None):
        self.accessions = []

        if init_accessions is not None:
            for x in init_accessions:
                self.accessions.append(x)

    def createMetaAccession(self):
        metaAccessionDict = {}
        for accession in self.accessions:
            for item in accession.get_items():
                # Clobber entries from previous accessions, keep the newest
                metaAccessionDict[item.get_canonical_filepath()] = \
                    item.get_root_path()
        metaAccessionList = []
        for canonicalFilepath in metaAccessionDict:
            metaAccessionList.append(
                                     metaAccessionDict[canonicalFilepath] +
                                     "/" + canonicalFilepath)
        metaAccession = Batch()
        for reconstructedFilePath in metaAccessionList:
            metaAccession.add_item(Item(reconstructedFilePath))

        return metaAccession
