import csv
import json
import logging
from os import _exit
from os.path import dirname, join, relpath
from uchicagoldr.item import AccessionItem, Item
from uchicagoldr.batch import AccessionDirectory
from re import compile as re_compile
from sys import stdout

class Page(object):
    def __init__(self, item, label, pagenum):
        self.pagenumber = pagenum
        self.representations = set([])
        self.label = label
        self.item = item

    def __eq__(self, other):
        assert isinstance(other, Page)
        if self.pagenmber == other.pagenumber:
            return 0

    def __le__(self, other):
        assert isinstnace(other, Page)
        if self.pagenumber < other.pagenumber:
            return -1

    def __gt__(self, other):
        assert isinstance(other, Page)
        if self.pagenumber > other.pagenumber:
            return 1

    def add_representation(self, n, representation_string):
        assert isinstance(n, AccessionItem)
        self.representations.add(representation_string)
        is_it_already_there = getattr(self,representation_string,None)
        if is_it_already_there:
            getattr(self, representation_string).append(n)
        else:
            setattr(self, representation_string, [n])

    def __str__(self):
        opener = "{pagenum} has {representations}".format(pagenum = str(self.pagenumber),
                                                          representations = ', '.join(self.representations))
        for rep in self.representations:
            opener += getattr(self, rep).get_file_path() + '\n'
        return opener
        

class Mvol(object):
    def __init__(self, identifier):
        self.identifier = identifier
        self.representations = set([])
        self.pages = []
        self.accessions = set([])

    def __eq__(self, other):
        assert isinstance(other, Mvol)
        if self.identifier == other.identifier:
            return 0
    def __le__(self, other):
        assert isinstnace(other, Mvol)
        if self.identifier < other.identifier:
            return -1
    def __gt__(self, other):
        assert isinstance(other, Mvol)
        if self.identifier > other.identifier:
            return 1

    def add_page(self, p, label, number):
        assert isinstance(p, AccessionItem)
        assert isinstance(number, str)
        assert isinstance(label, str)
        pagenum = int(number.lstrip('0'))
        current = [x for x in self.pages if x.pagenumber == pagenum]
        if len(current) > 0:
            current = current[0]
            current.add_representation(p, label)
        else:
            current = Page(p, label, pagenum)
            current.add_representation(p, label)
            self.pages.append(current)
        
    def add_representation(self, n, representation_string):
        assert isinstance(n, AccessionItem)
        assert self.identifier in n.get_canonical_filepath()
        self.representations.add(representation_string)
        is_it_already_there = getattr(self,representation_string,None)
        self.accessions.add(n.get_accession())
        if is_it_already_there:
            getattr(self, representation_string).append(n)
        else:
            setattr(self, representation_string, [n])

    def __str__(self):
        pages = sorted(self.pages)
        representations = [x for x in self.representations]
        file_list = []
        for n in self.representations:
            file_list.append(getattr(self, n).get_file_path())
        return "{identifier} has the following representations {representations} ". \
            format(identifier = self.identifier,
                   representations = ', '.join(self.representations)) + \
            "{files}".format(files = '\n'.join(file_list)) + \
            " and the following pages: {pages}".format(pages = '\n'.join([str(x) for x in pages]))

class Grouping(object):
    def __init__(self):
        self.items = []

    def does_it_need_a_new_item(self, identifier):
        if self.find_item(identifier):
            n = self.find_item(identifier)
            return n
        else:
            n = Mvol(identifier)
            self.items.append(n)
            return n

    def add_item(self, i):
        assert isinstance(i, Mvol)
        if len([x for x in self.items if x.identifier == i.identifier]) > 0:
            self.items.append(i)
            return True
        return False

    def sort_items(self):
        new = sorted(self.items)
        self.items = new

    def find_item(self, i):
        assert isinstance(i, str)
        check = [x for x in self.items if x.identifier == i]
        if len(check) == 1:
            return check[0]
        else:
            return None

def main():
    try:
        files_list = open("/media/sf_shared_with_ubuntu_guest_os/" + \
        "mvol-0001-files.txt",'r').readlines()
        accession_set = []
        output = {}
        g = Grouping()
        rep_labels = set([])
        for n in files_list:
            fullpath_dir = dirname(n)
            relpath_dir = relpath(fullpath_dir, '/media/repo/repository/ac/')
            accession = relpath_dir.split('/')[0]
            i = AccessionDirectory(join('/media/repo/repository/ac/', 
                                        accession), 
                                   '/media/repo/repository/ac/')
            a = AccessionItem(n,'/media/repo/repository/ac/')
            the_file_path = a.get_file_path().strip()
            a.set_canonical_filepath(a.find_canonical_filepath())
            pattern = re_compile(r'(mvol)/(\w{4})/(\w{4})/(\w{4})')
            matches = pattern.search(a.get_canonical_filepath())
            if matches:
                identifier = '-'.join([matches.group(1), matches.group(2), 
                                       matches.group(3), matches.group(4)])
                limb_files_required = [('dc',r'{identifier}.dc.xml$'.format(identifier  = identifier)),
                                       ('dc-fits',r'{identifier}.dc.xml.fits.xml$'.format(identifier  = identifier)),
                                       ('mets-fits', r'{identifier}.mets.xml.fits.xml$'.format(identifier  = identifier)),
                                       ('mets', r'{identifier}.mets.xml$'.format(identifier  = identifier)),
                                       ('txt', r'{identifier}.txt$'.format(identifier = identifier)),
                                       ('txt-fits', r'{identifier}.txt.fits.xml$'.format(identifier = identifier)),
                                       ('struct', r'{identifier}.struct.txt$'.format(identifier = identifier)),
                                       ('struct-fits', r'{identifier}.struct.txt.fits.xml$'.format(identifier = identifier)),
                                       ('pdf', r'{identifier}.pdf$'.format(identifier = identifier)),
                                       ('pdf-fits', r'{identifier}.pdf.fits.xml$'.format(identifier = identifier)),
                                       ('tiff', r'TIFF/%s_\d{4}.tif$' % identifier),
                                       ('tiff-fits', r'TIFF/%s_\d{4}.tif.fits.xml$' % identifier),
                                       ('jpeg', r'JPEG/%s_\d{4}.jpg$' % identifier),
                                       ('jpeg-fits', r'JPEG/%s_\d{4}.jpg.fits.xml$' % identifier),
                                       ('alto', r'ALTO/%s_\d{4}.\w{3,4}$' % identifier),
                                       ('alto-fits', r'ALTO/%s_\d{4}.\w{3,4}.fits.xml$' % identifier)]
    
                prelimb_files_required = [('dc', r'{identifier}.dc.xml$'.format(identifier = identifier)),
                                          ('dc-fits', r'{identifier}.dc.xml.fits.xml$'.format(identifier = identifier)),
                                          ('pdf', r'{identifier}.pdf$'.format(identifier = identifier)),
                                          ('pdf-fits', r'{identifier}.pdf.fits.xml$'.format(identifier = identifier)),
                                          ('txt', r'{identifier}.txt$'.format(identifier = identifier)),
                                          ('txt-fits', r'{identifier}.txt.fits.xml$'.format(identifier = identifier)),
                                          ('tif',  r'tif/\d{8}.tif$'),
                                          ('tif-fits', 'tif/\d{8}.tif.fits.xml$'),
                                          ('jpeg', r'jpg/\d{8}.jpg$'),
                                          ('jpg-fits', r'jpg/\d{8}.jpg.fits.xml$'),
                                          ('pos', r'pos/\d{8}.pos$'),
                                          ('pos-fits', r'pos/\d{8}.pos.fits.xml$')]

                page_num_file_parts = [r'(\d{8})', r'_(\d{4})']

                files_required = []
                files_required.extend(limb_files_required)
                files_required.extend(prelimb_files_required)
                n = g.does_it_need_a_new_item(identifier)

                for tup in files_required:
                    pattern = re_compile(tup[1])
                    label  = tup[0]
                    search = pattern.search(a.get_canonical_filepath())
                    if search:
                        check = True
                        is_page = False
                        for ppart in page_num_file_parts:
                            page_pattern = re_compile(ppart)
                            page_search = page_pattern.search(a.get_canonical_filepath())
                            if page_search:
                                is_page = True
                                n.add_page(a, label, page_search.group(1))
                        if not is_page:
                            rep_labels.add(label)
                            n.add_representation(a, label)
            else:
                logging.error("could not match file {filename}".format(filename = the_file_path))
        g.sort_items()
        rep_labels = list(rep_labels)
        with open('mvol-0001.csv', 'w') as csvfile:
            recwriter = csv.writer(csvfile, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_ALL)
            header = ['identifier']
            header.extend(rep_labels)
            header.extend(['accession'])
            header.extend(['numpages'])
            recwriter.writerow(header)
            for n in g.items:
                repnum = ""
                rowstring = []
                rowstring.append(n.identifier)
                for rep in n.representations:
                    if getattr(n, rep):
                        repnum = len(getattr(n, rep))
                    else:
                        print(getattr(n,rep))
                        repnum = 0
                    rowstring.append(str(repnum))
                rowstring.append(','.join(list(n.accessions)))
                rowstring.append(str(len(n.pages)))
                recwriter.writerow(rowstring)
            recwriter.close()
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
