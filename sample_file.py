import re
import sqlite3
import os
import csv
import time
import sys


class GlobalVarTest(object):

    def __init__(self):
        self.del_type = '\t'
        self.sample_fields = {4}
        # self.sample_fields = set()
        self.sample_rowid = set()
        self.saveDir = os.curdir + os.path.join(os.curdir, "\\Processed")
        self.searchType = 'txt'
        # action 1 for for break, 0 for sample
        self.query_head = True
        self.original_header = ''
        self.db_header = []
        self.original_filename = ''

    def get_query_fields(self):
        print(self.original_header)
        query_string = ""
        for n, fld in enumerate(self.original_header):
            query_string += "{:<10}({}): {}\n".format("", n, fld)

        print("Proof file evaluates longest and shortest fields, enter field number to sample by.")
        print("List multiple fields separated by space (ex: 2 4): ")
        print(query_string)
        answer = input("")
        query_fields = answer.split(" ")

        for fld in query_fields:
            if str.isdigit(fld):
                self.sample_fields.add(int(fld))

        self.sample_fields = self.sample_fields.intersection(set(range(0, len(self.original_header))))


    def query_header(self):
        # If the first line is a header record, written files will have the same header
        self.query_head = bool(input("First line as header record? (1/yes, 0/no): "))

    def query_action(self):
        # Set action ('action'), 0 to create 1 file, with 1 sample from each group
        # 1 outputs a new file for each group
        action = int(input("Sample File or File Break? (0 for sample, 1 for break): "))
        if action not in [0, 1]:
            print("Error: must be 0 or 1")
            time.sleep(3)
            sys.exit()
        else:
            self.action = action

    def query_del_type(self):
        # Set delimiter type ('del_type'), tab or comma are the only options
        del_type = int(input("Enter delimiter type (0 for tab, 1 for comma): "))
        if del_type not in [0, 1]:
            print("Error: must be 0 or 1")
            time.sleep(3)
            return
        else:
            self.del_type = (',' if del_type == 1 else '\t')

    def query_split_field(self):
        # Field position that the group selections will be based on
        self.split_field_n = int(input("Enter field number to split by: "))

    def query_search_type(self):
        # Type of file to search, written files will  be the same format
        self.searchType = input("Enter file type (ex: txt, csv, tab): ")

    def set_header(self, head):
        self.original_header = head

    def ask_questions(self):
        pass
        # self.query_header()
        # self.query_action()
        # self.query_del_type()
        # self.query_split_field()
        # self.query_search_type()
        # Create a new directory for resulting files
        # if not os.path.exists(self.saveDir):
        #     os.makedirs(self.saveDir)


class GlobalVar(object):

    def __init__(self):
        self.del_type = '\t'
        self.sample_fields = set()
        self.sample_rowid = set()
        self.saveDir = os.curdir + os.path.join(os.curdir, "\\Processed")
        self.searchType = 'txt'
        # action 1 for for break, 0 for sample
        self.query_head = True
        self.original_header = ''
        self.db_header = []
        self.original_filename = ''

    def get_query_fields(self):
        # print(self.original_header)
        query_string = ""
        for n, fld in enumerate(self.original_header):
            query_string += "{:<10}({}): {}\n".format("", n, fld)

        print("Proof file evaluates longest and shortest fields, enter field number to sample by.")
        print("List multiple fields separated by space (ex: 2 4): ")
        print(query_string)
        answer = input("")
        query_fields = answer.split(" ")

        for fld in query_fields:
            if str.isdigit(fld):
                self.sample_fields.add(int(fld))

        self.sample_fields = self.sample_fields.intersection(set(range(0, len(self.original_header))))


    def query_header(self):
        # If the first line is a header record, written files will have the same header
        self.query_head = bool(int(input("First line as header record? (1/yes, 0/no): ")))

    def query_action(self):
        # Set action ('action'), 0 to create 1 file, with 1 sample from each group
        # 1 outputs a new file for each group
        action = int(input("Sample File or File Break? (0 for sample, 1 for break): "))
        if action not in [0, 1]:
            print("Error: must be 0 or 1")
            time.sleep(3)
            sys.exit()
        else:
            self.action = action

    def query_del_type(self):
        # Set delimiter type ('del_type'), tab or comma are the only options
        del_type = int(input("Enter delimiter type (0 for tab, 1 for comma): "))
        if del_type not in [0, 1]:
            print("Error: must be 0 or 1")
            time.sleep(3)
            return
        else:
            self.del_type = (',' if del_type == 1 else '\t')

    def query_split_field(self):
        # Field position that the group selections will be based on
        self.split_field_n = int(input("Enter field number to split by: "))

    def query_search_type(self):
        # Type of file to search, written files will  be the same format
        self.searchType = input("Enter file type (ex: txt, csv, tab): ")

    def set_header(self, head):
        self.original_header = head

    def ask_questions(self):
        self.query_header()
        if not self.query_head:
            print("File must contain header, cancelling.")
            sys.exit()

        self.query_del_type()
        self.query_search_type()
        # Create a new directory for resulting files
        # if not os.path.exists(self.saveDir):
        #     os.makedirs(self.saveDir)


def get_header_csv(imported_file):
    """
    Creates a string to be used for database field names
    If errors, or header contains duplicates, returns False
    """

    try:
        with open(imported_file, 'r') as o:
            csvr = csv.reader(o, delimiter=g.del_type)
            fields = next(csvr)

        if g.query_head:
            fields = clean_header(fields)
        else:
            return ['Fld' + str(x) for x in range(1, len(fields) + 1)]

        if len(fields) == len(set(fields)):
            return fields
        else:
            print("Error: Header file contains duplicate field names:")
            for field in fields:
                print(field)
            time.sleep(6)
            return False

    except Exception as e:
        print(e)
        print("File Not Found")
        time.sleep(3)
        return False


def clean_header(field):
    """
    Removes sql offending characters from the header record
    Turns empty fields into 'EMPTY'
    """
    empty_cnt = 1
    expr = re.compile('[^A-Za-z0-9]')
    lead_num = re.compile('[0-9]')

    g.set_header(field)

    # Remove any characters that aren't US alphabet letters, numbers
    # (removes spaces)
    field = [re.sub(expr, '', elem) for elem in field]
    # Field names can't start with a number, removes that too
    field = [elem[1:] if lead_num.match(elem) else elem for elem in field]

    clean_field = []
    # Field names can't be empty either, creates a new field name 'EMPTY'
    # each empty field is numbered to avoid duplicates
    for elem in field:
        if elem == '':
            clean_field.append("EMPTY{}".format(empty_cnt))
            empty_cnt += 1
        else:
            clean_field.append(elem)

    return clean_field


def new_dbfields(fields=[]):
    """
    create sql statement string for new database fields
    """

    sql_stmt = ' varchar (100), '.join(fields[:-1])
    sql_stmt = (sql_stmt +
                str(' varchar (100), {} varchar (100)'.format(fields[-1])))
    return sql_stmt


def proof_records():
    """
    Updates the list of sample row ids from list to use as proofs
    :return:
    """
    eval_fields = [g.db_header[i] for i in g.sample_fields]

    db = sqlite3.connect('split.db')

    for field in eval_fields:

        # print(("SELECT rowid FROM records "
        #        "WHERE ROWID IN (SELECT ROWID FROM "
        #        "records ORDER BY length({0}) DESC LIMIT 1);".format(field)))

        rslt = db.execute(("SELECT rowid FROM records "
                           "WHERE ROWID IN (SELECT ROWID FROM "
                           "records ORDER BY length({0}) DESC LIMIT 1);".format(field)))

        g.sample_rowid.add(rslt.fetchone()[0])

    for field in eval_fields:

        # print(("SELECT rowid FROM records "
        #        "WHERE ROWID IN (SELECT ROWID FROM "
        #        "records ORDER BY length({0}) ASC LIMIT 1);".format(field)))

        rslt = db.execute(("SELECT rowid FROM records "
                           "WHERE ROWID IN (SELECT ROWID FROM "
                           "records ORDER BY length({0}) ASC LIMIT 1);".format(field)))

        g.sample_rowid.add(rslt.fetchone()[0])

    db.close()


def export_proof_records():

    db = sqlite3.connect('split.db')
    limit = max(10, len(g.sample_rowid))

    select_fields = ", ".join(g.db_header)

    samples = ",".join([str(i) for i in g.sample_rowid])

    sql = ("SELECT {0} FROM (SELECT *, '' AS r FROM records AS a "
           "WHERE ROWID IN ({1}) UNION ALL SELECT *, random() "
           "AS r FROM records AS b WHERE ROWID NOT IN ({1}) "
           "ORDER BY r DESC LIMIT 50) AS c LIMIT {2};".format(select_fields, samples, str(limit)))

    # print(g.sample_rowid)
    # print(sql)
    rslt = db.execute(sql)

    write_rec = "{0}_PROOF.{1}".format(os.path.splitext(g.original_filename)[0], g.searchType)

    with open(write_rec, 'w+', newline='') as s:
        csvw = csv.writer(s, delimiter=g.del_type, quoting=csv.QUOTE_ALL)
        if g.query_head:
            csvw.writerow(g.original_header)
        for line in rslt.fetchall():
            csvw.writerow(line)

    db.close()


def header_info():
    """
    returns a list with the header info
    [0]: The name of the field to break by (as defined in split_field_n)
    [1]: The schema of the split.db database.  Can be used to
         get field header names
    """
    db = sqlite3.connect('split.db')
    qry = db.execute("PRAGMA TABLE_INFO (records);")

    split_field_name = {}

    for n, elem in enumerate([a for a in qry], 1):
        split_field_name[n] = elem

    db.close()

    try:
        return [split_field_name[g.split_field_n][1], split_field_name.values()]
    except Exception:
        print("Ooops, something went wrong, check field break index")
        time.sleep(3)
        db.close()
        sys.exit()


def import_records(import_file, headers):
    """
    Import records from [import_file]
    Creates new db file, split.db
    Use list [headers] to create new database
    """
    db = sqlite3.connect('split.db')
    db.execute('drop table if exists records;')
    db.execute('create table records ({0});'.format(new_dbfields(headers)))

    print('Importing {}'.format(import_file))

    with open(import_file, 'r') as f:
        read = csv.reader(f, delimiter=g.del_type)
        for n, row in enumerate(read, 1):

            inserts = '","'.join(["%s"] * len(row))
            fields = tuple(row)

            query = ('INSERT INTO records VALUES ("' + inserts + '");') % (fields)

            db.execute(query)

    if g.query_head:
        db.execute("DELETE FROM records WHERE rowid = 1;")

    db.commit()
    db.close()


def import_file(file_import):
    """
    Imports records from [file_import] after getting the
    headers.  If get_header function fails, does not import
    If import attempt is made, returns True
    """
    headers = get_header_csv(file_import)
    g.original_filename = file_import
    g.db_header = headers
    g.get_query_fields()

    if headers:
        import_records(file_import, headers)
        proof_records()
        export_proof_records()
        return True


if __name__ == '__main__':
    global g
    # g = GlobalVarTest()
    g = GlobalVar()
    g.ask_questions()
    # import_file('33351 unitypoint 236789 mailing mf.txt')

    dir_list = os.listdir(os.curdir)
    for proc_file in dir_list:
        if proc_file[-(len(g.searchType)):] == g.searchType:
            print("Processing: " + proc_file)
            import_file(proc_file)

            # if os.path.isfile(os.path.join(os.curdir, 'split.db')):
            #     os.remove(os.path.join(os.curdir, 'split.db'))
