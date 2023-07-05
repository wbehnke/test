import sqlite3
import sys
import os
sys.path.append( '.' )
sys.path.append( '../production_dataset' )

from production_dataset.use_prod_dataset_util import *
from load_prod_dataset import load_prod_dataset

connection = sqlite3.connect('prod_database.db')
load_prod_dataset(connection)

## --- for playing around with SQL files -----
# test_name = "recommend_new_for_two"

# in_query_folder = "sample_queries/in/"
# in_query_file = test_name + ".sql"
# in_file = in_query_folder + in_query_file

# out_query_folder = "sample_queries/out/"
# out_query_file = test_name + ".out"
# out_file = out_query_folder + out_query_file

# run_command_from_file(connection=connection, input_filename=in_file, output_filename=out_file)
## ------------------

query = """
SELECT COUNT(*) FROM MOVIE;
"""

## a CHECK constraint violation should happen!
run_command_from_string(connection, query, True)