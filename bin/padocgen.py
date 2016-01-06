from argparse import ArgumentParser
import csv
import json
import logging
from os import _exit, access, W_OK
from os.path import abspath, basename, exists, dirname, join, relpath, splitext
from uchicagoldr.item import Item
from uchicagoldr.batch import AccessionDirectory, Directory
from uchicagoldrcampubpostaccession.misc import Grouping, Page, Mvol, Output
from re import compile as re_compile
from sys import stdout, stderr

csv_headers = ['identifier',
               'project',
               'record',
               'volume',
               'issue',
               'which accessions have files for this issue',
               'is there a .txt structural file',
               'is there a -struct.xt structural file',
               'is there a pdf file',
               'were page files found',
               'number of pages in old structural metadata',
               'number of pages in new structural metadata',
               'number of pages on disk']

page_csv_headers = ['object', 'object identifier','issue identifier', 'is there an ocr file', 
                    'is there a jpeg file', 'is there a tiff file']

page_num_file_parts = [r'(\d{8})', 
                       r'_(\d{4})']

def generate_pattern_list(identifier):
    limb_files_required = [('txt', r'{identifier}.txt$'. \
                            format(identifier = identifier)),
                           ('struct', r'{identifier}.struct.txt$'. \
                            format(identifier = identifier)),
                           ('pdf', r'{identifier}.pdf$'. \
                            format(identifier = identifier)),
                           ('tiff', r'TIFF/%s_\d{4,}.tif$' % identifier),
                           ('jpeg', r'JPEG/%s_\d{4,}.jpg$' % identifier),
                           ('xml', r'XML/%s_\d{4,}.xml$' % identifier),
                           ('alto', r'ALTO/%s_\d{4,}.\w{3,4}$' % identifier)]
    prelimb_files_required = [('pdf', r'{identifier}.pdf$'. \
                               format(identifier = identifier)),
                              ('txt', r'{identifier}.txt$'. \
                               format(identifier = identifier)),
                              ('tiff',  r'tif/\d{8,}.tif$'),
                              ('jpeg', r'jpg/\d{8,}.jpg$'),
                              ('xml', r'xml/\d{{8,}.xml$'),
                              ('pos', r'pos/\d{8,}.pos$')]
    output = []
    output.extend(limb_files_required)
    output.extend(prelimb_files_required)
    return output

def main():
    try:
        parser = ArgumentParser(description="",epilog="")
        parser.add_argument("record_number",help="",action="store")
        parser.add_argument("file_list",help="",action="store")
        args = parser.parse_args()
        g = Grouping()
        try:
            files_list = open(args.file_list, 'r').readlines()
        except:
            stderr.write("cold not open file {flist}". \
                         format(flist = args.file_list))
            return 1
        for n_file in files_list:
            fullpath_dir = dirname(n_file)
            relpath_dir = relpath(fullpath_dir, '/media/repo/repository/tr/')
            accession = relpath_dir.split('/')[0]
            i = AccessionDirectory(join('/media/repo/repository/tr/', 
                                        accession), 
                                   '/media/repo/repository/tr/')
            a = Item(n_file)
            setattr(a,'accession',accession)
            the_file_path = a.get_file_path().strip()
            canonical_file_path = the_file_path.split(accession)[1].lstrip('/')
            pattern = re_compile(r'(mvol)/(\w{4})/(\w{4})/(\w{4})')
            matches = pattern.search(canonical_file_path)
            if matches:
                identifier = '-'.join([matches.group(1), matches.group(2), 
                                       matches.group(3), matches.group(4)])
                files_required = generate_pattern_list(identifier)
                n = g.does_it_need_a_new_item(identifier)
                for tup in files_required:
                    pattern = re_compile(tup[1])
                    label  = tup[0]
                    search = pattern.search(a.get_file_path())
                    if search:
                        check = True
                        is_page = False
                        for ppart in page_num_file_parts:
                            page_pattern = re_compile(ppart)
                            page_search = page_pattern. \
                                          search(a.get_file_path())
                            if page_search:
                                is_page = True
                                n.add_page(a, label, page_search.group(1), 
                                           splitext(basename( \
                                                    a.get_file_path()))[0])
                        if not is_page:
                            n.add_representation(a, label)
                g.sort_items()
            else:
                logging.error("could not match file {filename}". \
                              format(filename = the_file_path))

        mvol_csv = "mvol-%s.csv" % args.record_number
        main_csv = Output(mvol_csv)
        main_csv.add_record(csv_headers)
        for n in g.items:
            if 'Thum' in n.identifier or 'tif' in n.identifier \
               or 'test' in n.identifier:
                continue
            id_parts = n.identifier.split('-')
            has_new_struct = 'N'
            has_old_struct = 'N'
            has_pdf = 'N'
            has_pages = 'Y' if getattr(n,'pages',None) else 'N'
            struct_objids = []
            txt_objids = []
            old_style = False
            new_style = False
            pdf = getattr(n, 'pdf', None)
            new_mdata = getattr(n, 'struct', None)
            old_mdata = getattr(n, 'txt', None)
            if pdf:
                has_pdf = 'Y'
            else:
                errors.get(n.identifier).append("missing {rep}". \
                                                format(rep = rep))
            if new_mdata and isinstance(new_mdata, list):
                has_new_struct = 'Y'
                struct_mdata_files = [x.get_file_path(). \
                                      strip() for x in new_mdata]
            elif new_mdata and isinstance(new_mdata, Item):
                has_new_struct = 'Y'
                struct_mdata_files = [new_mdata.get_file_path().strip()]
            elif old_mdata and isinstance(old_mdata, list):
                has_old_struct = 'Y'
                struct_mdata_files = [x.get_file_path(). \
                                      strip() for x in old_mdata]
            elif old_mdata and isinstance(old_mdata, Item):
                has_old_struct = 'Y'
                struct_mdata_files = [old_mdata.get_file_path().strip()]
            if struct_mdata_files:
                for struct_mdata_file in struct_mdata_files:
                    try:
                        fp = open(struct_mdata_file,'r')
                        lines = fp.readlines()
                        lines = [x for x in lines if len(x.split('\t')) == 3]
                        relevant_lines = lines[1:]
                        objids = [x.replace('\t','').strip('\n') \
                                  for x in relevant_lines]
                        page_difference = len(objids) - len(n.pages)
                        if has_new_struct == 'Y':
                            struct_objids = objids
                        elif has_old_struct == 'Y':
                            txt_objids = objids
                    except UnicodeDecodeError:
                        stderr.write("{mfile} couldn't be opened\n". \
                                     format(mfile = struct_mdata_file))
            record = [n.identifier, id_parts[0], id_parts[1], 
                      id_parts[2], id_parts[3], ','.join(list(n.accessions)), 
                      has_old_struct, has_new_struct, has_pdf, 
                      has_pages, len(txt_objids),
                      len(struct_objids), len(n.pages)]
            main_csv.add_record(record)
            issue_csv_file_name = "%s-pages.csv" % n.identifier
            issue_csv = Output(issue_csv_file_name)
            issue_csv.add_record(page_csv_headers)
            sorted_pages = sorted(n.pages)
            for page in sorted_pages:
                ocr_there = "Y" if getattr(page,'pos',None) or \
                            getattr(page,'alto',None) \
                            or getattr(p, 'xml',None) else "N"
                jpeg_there = "Y" if getattr(page, 'jpeg',None) else "N"
                tiff_there = "Y" if getattr(page, 'tiff',None) else "N"
                try:
                    x = page.objectpage.split('_')[1].lstrip('0')
                    object_identifier = x.zfill(8)
                except:
                    object_identifier = page.objectpage
                page_record = [object_identifier,
                               page.objectpage, n.identifier, 
                               ocr_there, jpeg_there, tiff_there]
                issue_csv.add_record(page_record)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
