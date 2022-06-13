# data-api.py
"""
This is a simple Flask api that returns some data saved into a
    'data_complete.csv' file in the root script directory.

Endpoints:
    /complete: Returns a 200 code, and a JSON with the key 'data' containing
        the full dataset
    /partial: Returns a 200 code, and a partial set of data, formatted as with
        /complete, and taken from the top. Takes the URL parameter 'size', with
        values 'small', 'medium', 'large' (default 'small'), and returns the 
        first 0.1%, 1%, or 10% records, rounded down. The 'data' key will be 
        empty if the parameter value is not enough to return at least 1 record.
    /random: Works as /partial, but the data is taken at random from the entire
        dataset. Rows are randomized as well.
    /paged: Takes in two URL parameters ('start' and 'end'), and returns the
        rows of data in between (first row is #1). If 'start' is larger than 
        the dataset size, the 'data' key in response is empty. If 'start' is
        within the dataset but 'end' is larger than the size, returns as much
        as it can.
    /: Just a simple html index page, to avoid 404.
"""
from flask import Flask, request, jsonify
import pandas as pd
import math

app = Flask(__name__) # define the Flask app

df = pd.read_csv('data_complete.csv') # read the csv data into pandas dataframe
total_rows = df.shape[0]

# pre-export complete dataset for faster loading of /complete
complete_dataset = df.to_dict('records')
complete_response = jsonify(
    {
        'data': complete_dataset
    }
)

# map the values of the size parameter to the percentage of rows returned
partial_sizes = {
    'small': 0.001,
    'medium': 0.01,
    'large': 0.1
}

@app.route('/complete', methods=['GET'])
def get_complete_data():
    """
    Returns the complete dataset as a JSON with the 'data' key containing it
    """
    return complete_response, 200

@app.route('/partial', methods=['GET'])
def get_partial_data():
    """
    Returns a partial set of data, taken from the top. Takes the URL parameter
    'size' with values 'small', 'medium', 'large' (default 'small') and returns
    the top 0.1%, 1% or 10% of data respectively. Returns 400 and error message
    if wrong parameter value is passed.
    """
    response = {}

    # check for the right parameter value, or none passed (default to small)
    size = request.args.get('size', 'small')
    if size not in partial_sizes.keys():
        # if passed the wrong parameter, return 400 and error message
        response['error'] = "'size' parameter takes only values 'small',"\
            " 'medium' or 'large'"
        return jsonify(response), 400

    # calculate number of rows to return, and default 'data' key to empty
    rows_to_return = math.floor( total_rows * partial_sizes.get(size) )
    response['data'] = []
    # if there's anything to return, overwrite the 'data' key with those rows
    if rows_to_return > 0:
        response['data'] = df[:rows_to_return].to_dict('records')

    return jsonify(response), 200

@app.route('/random', methods=['GET'])
def get_random_data():
    """
    """
    response = {}

    # check for the right parameter value, or none passed (default to small)
    size = request.args.get('size', 'small')
    if size not in partial_sizes.keys():
        # if passed the wrong parameter, return 400 and error message
        response['error'] = "'size' parameter takes only values 'small',"\
            " 'medium' or 'large'"
        return jsonify(response), 400

    # calculate number of rows to return, and default 'data' key to empty
    rows_to_return = math.floor( total_rows * partial_sizes.get(size) )
    response['data'] = []
    # if there's anything to return, get a random sample of data and use that
    if rows_to_return > 0:
        response['data'] = df.sample(rows_to_return).to_dict('records')

    return jsonify(response), 200


@app.route('/paged', methods=['GET'])
def get_paged_data():
    pass

@app.route('/')
def index():
    return '<h1>This is empty...</h1>\n<p>(...yeah, I know)</p>'

if __name__ == '__main__':
    app.run()