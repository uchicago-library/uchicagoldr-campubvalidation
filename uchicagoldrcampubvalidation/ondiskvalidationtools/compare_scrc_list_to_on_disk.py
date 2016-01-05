from collections import namedtuple
import csv
from os import _exit
from os.path import exists, join
from sys import stderr

def main():
    try:
        record = '0001'
        path = '/home/tdanstrom/src/ldr_projects/uchicagoldr-primary/bin/mvol-0001/'
        scrc_file = join(path, 'mvol-0001-issues.csv')
        ondisk_file = join(path, 'mvol-0001.csv')
        scrc_open = open(scrc_file, 'r')
        ondisk_open = open(ondisk_file, 'r')
        scrc_csv_data = csv.reader(scrc_open)
        ondisk_csv_data = csv.reader(ondisk_open)
        scrc_csv_lines = []
        ondisk_csv_lines = []
        for n in scrc_csv_data:
            scrc_csv_lines.append(n)
        for n in ondisk_csv_data:
            ondisk_csv_lines.append(n)
        ondisk_has_structural_metadata = []
        ondisk_records = []
        count = 0
        for n in ondisk_csv_lines[1:]:
            identifier = n[0]
            is_it_valid = False
            has_structural_metadata = False
            has_pdf = False
            potential_structural1 = n[1]
            potential_structural2 = n[2]
            potential_pdf = n[3]
            if potential_structural1 == 'Y' or potential_structural2 == 'Y':
                has_structural_metadata = True
            if potential_pdf == 'Y':
                has_pdf  = True
            page_csv_file = '%s/issues/%s-pages.csv' % ('-'.join(n[0].split('-')[0:2]),n[0])
            if exists(page_csv_file):

                page_csv_file_open = open(page_csv_file,'r')
                page_csv_file_reader = csv.reader(page_csv_file_open)
                page_csv_issue_info = []
                for p in page_csv_file_reader:
                    page_csv_issue_info.append(p)

                for r in page_csv_issue_info[1:]:
                    if r[2] == 'Y' and r[3] == 'Y' and r[4] == 'Y' and has_structural_metadata and has_pdf:
                        is_it_valid = True
                    else:
                        is_it_valid = False
                has_pages = True


            else:
                has_pages = False
                stderr.write("cannot find file {pagefile}.\n".format(pagefile = page_csv_file))
            count += 1
            record = namedtuple('ondisk_issue','identifier has_mdata has_pdf has_pages is_valid')(identifier,
                                                                                                  has_structural_metadata,
                                                                                                  has_pdf,
                                                                                                  has_pages,
                                                                                                  is_it_valid)
            ondisk_records.append(record)

        ondisk_csv_ids = [x[0] for x in ondisk_csv_lines[1:]]
        scrc_ids = [x[2] for x in scrc_csv_lines[1:]]
        ids_present_in_both = [value for value in ondisk_csv_ids if value in scrc_ids]
        ids_not_on_disk = [x for x in scrc_ids if x not in ids_present_in_both]
        report_rows = []
        for n in scrc_ids:
            if n == "":
                continue
            ondisk_record = [x for x in ondisk_records if x.identifier == n]

            if ondisk_record:
                was_digitized = 'Y'
                ondisk_record = ondisk_record[0]
            else:
                was_digitized = 'N'
                has_mdata = 'N'
                has_pdf = 'N'
                is_valid = 'N'
                report_rows.append([n,was_digitized,has_mdata,has_pdf,is_valid])
                if n == "":
                    print(n)
                continue
            if ondisk_record.has_mdata:
               has_mdata_value = 'Y'
            else:
                has_mdata_value = 'N'
            if ondisk_record.has_pdf:
                has_pdf = 'Y'
            else:
                has_pdf = 'N'
            if ondisk_record.has_pages:
                has_pages = 'Y'
            else:
                has_pages = 'N'
            if ondisk_record.is_valid:
                is_valid = 'Y'
            else:
                is_valid = 'N'
            if n not in ondisk_csv_ids:
                was_digitized = False
            report_rows.append([n,was_digitized,has_mdata_value,has_pdf,is_valid])

        report_file = "mvol-0001-report"
        with open(report_file, 'w') as reportcsvfile:

            reportwriter = csv.writer(reportcsvfile, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_ALL)
            reportwriter.writerow(["identifier","was it digitized",
                                   "does it have metadata","does it have a pdf","is it valid"])

            for row in report_rows:
                reportwriter.writerow(row)

        return 0
    except KeyboardInterrupt:
        return 131


if __name__ == "__main__":
    _exit(main())
