import csv
import os

from filelock import FileLock

#########################################################
# Constants
#########################################################

CSV_FILE_DELIMITER = '\t'
HEADERS_WRITTEN = False

# Fieldnames
AVOID_LIST_CSV_FIELDNAMES = ['trial', 'percentage', 'propagation_round',
                             'adoption_setting', 'prefix_for_outcome',
                             'attacker_asns', 'victim_asn', 'avoid_list_len', 'avoid_list']

#########################################################
# Variables that need to be updated from __main__
#########################################################

collect_avoid_list_metadata = False  # Defines control switch of enable/disabling metadata collection for avoid list
output_filename = None
base_path = None

avoid_list_csv_filename = ''
avoid_list_csv_lock_filename = ''
avoid_list_csv_flock = None


#########################################################
# Functions
#########################################################

def write_csv_file_header(csv_file_name, fieldnames, delimiter):
    # Write Header of CSV Files
    with open(csv_file_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()


def write_avoid_list_csv_header():
    # Setup Metadata collection CSV
    global avoid_list_csv_filename
    global avoid_list_csv_lock_filename
    global avoid_list_csv_flock
    avoid_list_csv_filename = ''.join([base_path, '/', output_filename, '_avoid_list_metadata.csv'])
    avoid_list_csv_lock_filename = ''.join([avoid_list_csv_filename, '.lock'])
    avoid_list_csv_flock = FileLock(avoid_list_csv_lock_filename)
    # Write their headers
    write_csv_file_header(avoid_list_csv_filename, AVOID_LIST_CSV_FIELDNAMES, CSV_FILE_DELIMITER)


def clean_up_lock_files():
    if collect_avoid_list_metadata:
        os.remove(avoid_list_csv_lock_filename)
