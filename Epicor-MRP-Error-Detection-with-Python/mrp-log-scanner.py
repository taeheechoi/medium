from pathlib import Path
from multiprocessing import Pool
from mmap import mmap, ACCESS_READ

# Define source folder, search words, and file extension
script_folder = Path(__file__).resolve().parent
source_folder = f'{script_folder}/sample'
search_words = ['Object reference not set to an instance of an object',
                'not responding', 'Lock request time out period exceeded',
                "Abandoned during process 'Defunct"]
file_extension = 'log'


def get_file_list(folder):
    """
    Returns a list of files with the specified file extension in the given folder.
    """
    path = Path(folder)
    print(path.resolve())
    return list(path.glob(f'*.{file_extension}'))


def find_word_in_file(file_path):
    """
    Searches for the specified words in a file using memory-mapping.
    Returns the first matching word and the file path.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        with mmap(file.fileno(), length=0, access=ACCESS_READ) as mp:
            for word in search_words:
                if mp.find(bytes(word, 'utf-8')) != -1:
                    return word, str(file_path)


def word_search_from_source():
    """
    Searches for the specified words in all the files with the specified file extension in the source folder.
    Returns a list of tuples containing the matching word and the file path.
    """
    pool_results = []
    with Pool() as pool:
        pool_results += pool.map(find_word_in_file,
                                 get_file_list(source_folder))
    search_results = [result for result in pool_results if result]
    return search_results


if __name__ == '__main__':

    # Search for the specified words in the source folder
    search_results = word_search_from_source()

    # Create a message string with the search results
    message = '\n'.join(
        [f'Word: "{result[0]}" found at the {result[1]}' for result in search_results])

    print(message)
