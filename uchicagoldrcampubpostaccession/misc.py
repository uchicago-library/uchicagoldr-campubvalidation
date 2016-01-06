from csv import reader, writer, QUOTE_ALL
from os import access, R_OK, W_OK
from os.path import abspath, dirname, exists
from uchicagoldr.item import AccessionItem, Item

# scrc_open = open(scrc_file, 'r')
# ondisk_open = open(ondisk_file, 'r')
# scrc_csv_data = csv.reader(scrc_open)
# ondisk_csv_data = csv.reader(ondisk_open)

class Input(object):
    data = None

    def __init__(self, file_name):
        print(file_name)
        assert exists(abspath(file_name))
        assert access(abspath(file_name),R_OK)
        opened_file = open(abspath(file_name),'r')
        self.data = reader(opened_file)

    def __iter__(self):
        return [x for x in self.data]

class Output(object):
    data_object = None

    def __init__(self,file_name):
        new_file_name_path = abspath(file_name)
        assert access(dirname(new_file_name_path), W_OK)
        new_file = open(new_file_name_path, 'w')
        new_csv_writer = writer(new_file, delimiter=',', quotechar='"',
                                quoting=QUOTE_ALL)
        self.data_object = new_csv_writer

    def add_record(self, a_list):
        assert isinstance(a_list, list)
        assert len(a_list) > 0
        self.data_object.writerow(a_list)


class Page(object):
    def __init__(self, item, label, pagenum, objectpage):
        self.pagenumber = pagenum
        self.objectpage = objectpage
        self.representations = set([])
        self.abel = label
        self.items = []

    def __eq__(self, other):
        assert isinstance(other, Page)
        if self.pagenmber == other.pagenumber:
            return 0

    def __le__(self, other):
        assert isinstance(other, Page)
        if self.pagenumber < other.pagenumber:
            return -1

    def __gt__(self, other):
        assert isinstance(other, Page)
        if self.pagenumber > other.pagenumber:
            return 1

    def add_representation(self, n, representation_string):
        assert isinstance(n, Item)
        self.representations.add(representation_string)
        is_it_already_there = getattr(self,representation_string,None)
        if is_it_already_there:
            getattr(self, representation_string).append(n)
        else:
            setattr(self, representation_string, [n])

    def __str__(self):
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
        assert isinstance(p, Item)
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
        assert isinstance(n, Item)
        assert self.identifier in n.get_file_path()
        self.representations.add(representation_string)
        is_it_already_there = getattr(self,representation_string,None)
        self.accessions.add(n.accession)
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
