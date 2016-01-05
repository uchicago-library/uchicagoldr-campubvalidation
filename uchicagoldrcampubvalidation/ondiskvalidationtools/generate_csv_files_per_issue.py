import csv
import json
import logging
from os import _exit
from os.path import basename, exists, dirname, join, relpath, splitext
from uchicagoldr.item import AccessionItem, Item
from uchicagoldr.batch import AccessionDirectory
from re import compile as re_compile
from sys import stdout, stderr

class Page(object):
    def __init__(self, item, label, pagenum, objectpage):
        self.pagenumber = pagenum
        self.objectpage = objectpage
        self.representations = set([])
        self.label = label
        self.items = []

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
        # opener = "{pagenum} has {representations}".format(pagenum = str(self.pagenumber),
        #                                                   representations = ', '.join(self.representations))
        # for rep in self.representations:
        #     opener += getattr(self, rep).get_file_path() + '\n'
        return "{pagenum} {reps}".format(pagenum = str(self.pagenumber), reps=str(self.representations))


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

    def add_page(self, p, label, number, objectnumber):
        assert isinstance(p, AccessionItem)
        assert isinstance(number, str)
        assert isinstance(label, str)
        pagenum = int(number.lstrip('0'))
        current = [x for x in self.pages if x.pagenumber == pagenum]
        if len(current) > 0:
            current = current[0]
            current.add_representation(p, label)
        else:
            current = Page(p, label, pagenum, objectnumber)
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
        record = '0002'
        files_list = open("/media/sf_shared_with_ubuntu_guest_os/" + \
        "mvol-00002-files-v2.txt",'r').readlines()
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
                
                limb_files_required = [('txt', r'{identifier}.txt$'.format(identifier = identifier)),
                                       ('struct', r'{identifier}.struct.txt$'.format(identifier = identifier)),
                                       ('pdf', r'{identifier}.pdf$'.format(identifier = identifier)),
                                       ('tiff', r'TIFF/%s_\d{4,}.tif$' % identifier),
                                       ('jpeg', r'JPEG/%s_\d{4,}.jpg$' % identifier),
                                       ('xml', r'XML/%s_\d{4,}.xml$' % identifier),
                                       ('alto', r'ALTO/%s_\d{4,}.\w{3,4}$' % identifier)]

    
                prelimb_files_required = [('pdf', r'{identifier}.pdf$'.format(identifier = identifier)),
                                          ('txt', r'{identifier}.txt$'.format(identifier = identifier)),
                                          ('tiff',  r'tif/\d{8,}.tif$'),
                                          ('jpeg', r'jpg/\d{8,}.jpg$'),
                                          ('xml', r'xml/\d{{8,}.xml$'),
                                          ('pos', r'pos/\d{8,}.pos$')]

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
                                n.add_page(a, label, page_search.group(1), 
                                           splitext(basename(a.get_canonical_filepath()))[0])
                        if not is_page:

                            n.add_representation(a, label)
            else:
                logging.error("could not match file {filename}".format(filename = the_file_path))
        g.sort_items()
        rep_labels = ['is there a .txt structural file','is there a -struct.xt structural file','is there a pdf file']
        errors = {}
        errors_txt_file = "errors-%s.txt" % record
        error_file = open(errors_txt_file,"a")
        mvol_csv = "mvol-%s.csv" % record
        with open(mvol_csv, 'w') as csvfile:
            recwriter = csv.writer(csvfile, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_ALL)
            header = ['issue identifier']
            header.extend(rep_labels)
            header.extend(['which accessions have files for this issue'])
            header.extend(['were page files found','number of pages in structural metadata', 'number of pages on disk'])
            recwriter.writerow(header)
            for n in g.items:
                repnum = ""
                rowstring = []
                if 'Thum' in n.identifier or 'tif' in n.identifier or 'test' in n.identifier:
                    continue
                rowstring.append(n.identifier)
                for rep in ['struct', 'txt', 'pdf']:
                    l = getattr(n, rep, None)
                    if l:
                        num_value = "Y"
                    else: 
                        num_value = "N"
                        try:
                            errors.get(n.identifier).append("missing {rep}".format(rep = rep))
                        except:
                            errors[n.identifier] = ["missing {rep}".format(rep = rep)]
                        error_file.write("\"{id}\",\"missing {rep}\"\n".format(id = identifier, rep = rep))
                    rowstring.append(str(num_value))
                s1 = getattr(n,'struct',None)
                s2 = getattr(n,'txt',None)
                if s1:
                    struct_mdata_files = s1
                elif s2:
                    struct_mdata_files = s2
        
                if isinstance(struct_mdata_files, list):
                    struct_mdata_files = [x.get_file_path().strip() for x in struct_mdata_files]
                else:
                    struct_mdata_files = [x.get_file_path().strip()]
                objids = []
                for struct_mdata_file in struct_mdata_files:
                    try:
                        fp = open(struct_mdata_file,'r')
                        lines = fp.readlines()
                        relevant_lines = lines[1:]
                        objids = [x.replace('\t','').strip('\n') for x in relevant_lines]
                    except UnicodeDecodeError:
                        stderr.write("{mfile} couldn't be opened\n".format(mfile = struct_mdata_file))
                        objids = []
                rowstring.append(','.join(list(n.accessions)))
                are_pages = 'Y' if len(n.pages) > 0 else 'N'
                rowstring.append(are_pages)
                rowstring.append(len(objids))
                rowstring.append(len(n.pages))
                if len(n.pages) == 0:
                    try:
                        errors.get(n.identifier).append("no pages")
                    except:
                        errors[n.identifier] = ["no pages"]
                    error_file.write("\"{id}\",\"no pages\"\n".format(id = identifier))
                recwriter.writerow(rowstring)
                pages_csv = "%s-pages.csv" % n.identifier
                pages_errors_csv = "%s-pages-errors.csv" % n.identifier
                with open(pages_csv,'w') as pagescsvfile:
                    pageswriter = csv.writer(pagescsvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
                    pageswriter.writerow(['object','issue identifier',
                                          'is there an ocr file',
                                          'is there a jpeg file',
                                          'is there a tiff file'])
                    sorted_pages = sorted(n.pages)
                    
                    for p in sorted_pages:
                        error_row = []
                        ocr_there = "Y" if getattr(p,'pos',None) or getattr(p,'alto',None) or getattr(p, 'xml',None) else "N"
                        jpeg_there = "Y" if getattr(p, 'jpeg',None) else "N"
                        tiff_there = "Y" if getattr(p, 'tiff',None) else "N"
                        pageswriter.writerow([p.objectpage, n.identifier, 
                                              ocr_there, jpeg_there, tiff_there])

        errors_csv_filename = "errors-%s" % record
        with open(errors_csv_filename, "w") as errorfile:
            newrecwriter = csv.writer(errorfile, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_ALL)

            for key,value in errors.items():
                newrecwriter.writerow([key,','.join(value)])

        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
