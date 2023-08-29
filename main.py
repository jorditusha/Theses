import datetime

from find_diagrams_main import extract_data
from get_drawio_per_repo import do_extensive_search

results_file_name = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M') + ".csv"

if __name__ == "__main__":
    extract_data(file_name_sink=results_file_name)

    final_file_name = do_extensive_search(sink_file=results_file_name)


