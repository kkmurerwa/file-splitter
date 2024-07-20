import os
from datetime import datetime
import sys
import csv
import shutil

ROOT_DIRECTORY = os.getcwd()
SOURCE_DIRECTORY = f'{ROOT_DIRECTORY}/val-pics'
DESTINATION_DIRECTORY = f'{ROOT_DIRECTORY}/Copied Files'
KEY_VALUE_PAIRS_FILE = f'{ROOT_DIRECTORY}/key_value_pairs.csv'
GLOBAL_ETA = 'Calculating...'
DELETE_AFTER_COPY = True
ETA_CALCULATION_INTERVAL = 2
COPY_BY_DATE = False


def write_key_value_pairs(data_to_write):
    create_file_if_not_exists(KEY_VALUE_PAIRS_FILE)

    with open(KEY_VALUE_PAIRS_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        for key, value in data_to_write.items():
            writer.writerow([key, value])


def read_key_value_pairs():
    create_file_if_not_exists(KEY_VALUE_PAIRS_FILE)

    data_read = {}
    with open(KEY_VALUE_PAIRS_FILE, mode='r') as file:
        reader = csv.reader(file)

        for row in reader:
            key, value = row
            data_read[key] = value
    return data_read


def current_directory():
    return os.getcwd()


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_file_if_not_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('')


def copy_file(destination_folder, source, destination):
    create_directory(destination_folder)

    if not os.path.exists(destination):
        with open(source, 'rb') as f:
            with open(destination, 'wb') as f2:
                f2.write(f.read())
                return True

    return False


def move_file(destination_folder, source_folder, file_name):
    create_directory(destination_folder)

    if not os.path.exists(f'{destination_folder}/{file_name}'):
        try:
            shutil.move(f'{source_folder}/{file_name}', f'{destination_folder}/{file_name}')
            return True
        except FileNotFoundError:
            print(f'Could not move {file_name}')

    return False


def get_last_modified_date(file_path):
    if os.path.exists(file_path):
        mod_time = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_time)


def get_folder_name_from_date(date):
    return date.strftime('%Y-%m')


def print_copy_progress(copied_files, total_files, skipped_files, start_time):
    if copied_files % ETA_CALCULATION_INTERVAL == 0:
        calculate_eta(copied_files + skipped_files, total_files, start_time)

    sys.stdout.write(f'\rCopied {copied_files} of {total_files} files. Skipped {skipped_files} files. ETA: {GLOBAL_ETA}')
    sys.stdout.flush()


def get_total_files_in_directory(directory):
    print("Calculating total files in directory...")
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len(files)

    total_files_map = {
        'total_files': total_files,
    }

    write_key_value_pairs(total_files_map)

    return total_files


def calculate_eta(copied_files, total_files, start_time):
    current_time = datetime.now()
    time_elapsed = current_time - start_time

    if time_elapsed == 0:
        return

    time_remaining = (total_files - copied_files) * (time_elapsed / copied_files)

    remaining_seconds = time_remaining.total_seconds()

    global GLOBAL_ETA
    GLOBAL_ETA = format_remaining_time(remaining_seconds)


def format_remaining_time(remaining_seconds):
    if remaining_seconds > 86400:
        days = int(remaining_seconds / 86400)
        hours = int((remaining_seconds % 86400) / 3600)
        return f'{days} days {hours} hours'
    elif remaining_seconds > 3600:
        hours = int(remaining_seconds / 3600)
        minutes = int((remaining_seconds % 3600) / 60)
        return f'{hours} hours {minutes} minutes'
    elif remaining_seconds > 60:
        minutes = int(remaining_seconds / 60)
        seconds = int(remaining_seconds % 60)
        return f'{minutes} minutes {seconds} seconds'
    elif remaining_seconds > 0:
        return f'{int(remaining_seconds)} seconds'
    else:
        return '0 seconds'


def copy_files_to_timeframed_directories(directory):
    copied_files = 0
    skipped_files = 0
    start_time = datetime.now()
    copy_data_map = read_key_value_pairs()

    if 'total_files' not in copy_data_map:
        total_files = get_total_files_in_directory(directory)
    else:
        total_files = int(copy_data_map['total_files'])
        if total_files == 0:
            total_files = get_total_files_in_directory(directory)

    print(f'Copying {total_files} files...')

    for root, dirs, files in os.walk(directory):
        for file in files:
            source = os.path.join(root, file)
            modified_time = get_last_modified_date(source)
            destination_folder = f'{DESTINATION_DIRECTORY}/{get_folder_name_from_date(modified_time)}'
            if copy_file(destination_folder, source, f'{destination_folder}/{file}'):
                copied_files += 1
                if DELETE_AFTER_COPY:
                    try:
                        os.remove(source)
                    except FileNotFoundError:
                        print(f'Could not delete {source}')
            else:
                skipped_files += 1
            print_copy_progress(copied_files, total_files, skipped_files, start_time)

    time_taken = datetime.now() - start_time
    print(f'\n\nTotal time taken: {format_remaining_time(time_taken.total_seconds())}')
    print('Copying complete!')


def copy_files_to_batched_directories():
    copied_files = 0
    skipped_files = 0
    start_time = datetime.now()
    copy_data_map = read_key_value_pairs()

    if 'total_files' not in copy_data_map:
        total_files = get_total_files_in_directory(SOURCE_DIRECTORY)
    else:
        total_files = int(copy_data_map['total_files'])
        if total_files == 0:
            total_files = get_total_files_in_directory(SOURCE_DIRECTORY)

    print(f'Copying {total_files} files...')

    for root, dirs, files in os.walk(SOURCE_DIRECTORY):
        for file in files:
            source = os.path.join(root, file)
            destination_folder = f'{DESTINATION_DIRECTORY}/Batch {(copied_files % 50) + 1}'
            if copy_file(destination_folder, source, f'{destination_folder}/{file}'):
                copied_files += 1
                if DELETE_AFTER_COPY:
                    os.remove(source)
            else:
                skipped_files += 1
            print_copy_progress(copied_files, total_files, skipped_files, start_time)

    time_taken = datetime.now() - start_time
    print(f'\n\nTotal time taken: {time_taken.total_seconds()}')
    print('Copying complete!')


def move_files_to_batched_directories():
    copied_files = 0
    skipped_files = 0
    start_time = datetime.now()
    copy_data_map = read_key_value_pairs()

    if 'total_files' not in copy_data_map:
        total_files = get_total_files_in_directory(SOURCE_DIRECTORY)
    else:
        total_files = int(copy_data_map['total_files'])
        if total_files == 0:
            total_files = get_total_files_in_directory(SOURCE_DIRECTORY)

    print(f'Moving {total_files} files...')

    for root, dirs, files in os.walk(SOURCE_DIRECTORY):
        for file in files:
            source_folder = os.path.join(root, file)
            destination_folder = f'{DESTINATION_DIRECTORY}/Batch {(copied_files % 50) + 1}'
            if move_file(destination_folder, SOURCE_DIRECTORY, file):
                copied_files += 1
            else:
                skipped_files += 1
            print_copy_progress(copied_files, total_files, skipped_files, start_time)

    time_taken = datetime.now() - start_time
    print(f'\n\nTotal time taken: {time_taken.total_seconds()}')
    print('Moving complete!')



def copy_files():
    if COPY_BY_DATE:
        copy_files_to_timeframed_directories(SOURCE_DIRECTORY)
    else:
        move_files_to_batched_directories()


copy_files()
