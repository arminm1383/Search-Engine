
from inverted_index.InvertedIndex import InvertedIndex
import time
from pathlib import Path

def main():
    project_root = Path(__file__).parent

    # Timer for Output Log
    start_time = time.time()

    # Instantiate and Run
    inverted_index_instance = InvertedIndex('project_root/DEV',
                                            'project_root/Result')
    inverted_index_instance.build_index() # Builds Batches
    inverted_index_instance.build_final_index() # Compiles Batches
    inverted_index_instance.write_final_index_to_disk() # Writes Output

    # End Time and Write Results
    end_time = time.time()
    inverted_index_instance.write_result_stats(end_time-start_time)

if __name__ == "__main__":
    main()