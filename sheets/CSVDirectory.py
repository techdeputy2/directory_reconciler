from __future__ import print_function

import csv

class CSVDirectory:
    def __init__(self, csvpath):
        rows = []
        with open(csvpath, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)            
            self.rows = rows

    def list(self, grade, is_band, is_student):
        results = []

        for row in [r for r in self.rows if r['Grade'] == grade]:        
            if is_band and row['Marching Instrument'] != 'Vision':
                if is_student:
                    results.append(row['Student Email'])
                else:
                    results.append(row['P1 Email'])
                    results.append(row['P2 Email'])
            elif not is_band and row['Marching Instrument'] == 'Vision':
                if is_student:
                    results.append(row['Student Email'])
                else:
                    results.append(row['P1 Email'])
                    results.append(row['P2 Email'])

        #remove duplicates and blank
        results = list(set([x.lower() for x in results]))
        if '' in results:
            results.remove('')
        results.sort()        
        return results