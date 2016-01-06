from argparse import Action, ArgumentParser
from collections import namedtuple
import csv
from os import _exit
from os.path import abspath, exists, join
from re import compile as re_compile
from sys import stderr
from uchicagoldrcampubpostaccession.misc import Input, Output

csv_headers = ["identifier",
               "was it digitized",
               "does it have metadata",
               "does it have pdf",
               "is it valid"]

def main():
    try:
        parser = ArgumentParser(description="",epilog="")
        parser.add_argument("record_number",help="",action="store", type=str)
        parser.add_argument("-g",help="",action='store')
        args = parser.parse_args()
        assert re_compile('^\w{4,}[-]?\w{1,}?$').match(args.record_number)
        if args.g:
            assert exists(abspath(args.g))
            root_path = abspath(args.g)
        else:
            root_path = join(abspath('/media/sf_shared_with_ubuntu_guest_os'),
                             'mvol-%s' % args.record_number)
        scrc_input = Input(join(root_path,'mvol-%s-issues.csv' \
                                % args.record_number))
        ondisk_input = Input(join(root_path,'mvol-%s.csv' \
                                  % args.record_number))        
        scrc_input = [x for x in scrc_input.data][1:]
        ondisk_input = [x for x in ondisk_input.data][1:]
        report = Output('mvol-%s-report.csv' % args.record_number)
        report.add_record(csv_headers)
        for n in scrc_input:
            was_it_digitized = 'Y'
            scrc_id = n[2]
            ondisk_record = [x for x in ondisk_input if x[0] == scrc_id][0]
            if not ondisk_record:
                stderr.write("{scrc_id} does not appear on-disk.\n". \
                             format(scrc_id = scrc_id))
                record = ['N','n/a','n/a','n/a']
                report.add_record(record)
                continue

            has_pdf = ondisk_record[8]            
            has_structural_metadata = 'Y' if ondisk_record[6] == 'Y' or \
                                      ondisk_record[7] == 'Y' else 'N'
            is_it_valid = 'Y' if was_it_digitized == 'Y' and \
                          has_structural_metadata == 'Y' and \
                          has_pdf == 'Y' else 'N'

            issue_input = Input(join(root_path,'issues', '%s-pages.csv') \
                                % scrc_id)
            invalid_pages = [(x[2],x[3],x[4]) for x in issue_input.data \
                             if x[2] == 'N' or x[3] == 'N' or x[4] == 'N']
            if invalid_pages:
                is_it_valid = 'N'
            record = [scrc_id, was_it_digitized,has_structural_metadata,
                      has_pdf,is_it_valid]
            report.add_record(record)
        return 0
    except KeyboardInterrupt:
        return 131


if __name__ == "__main__":
    _exit(main())
