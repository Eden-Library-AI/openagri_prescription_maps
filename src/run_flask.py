from flask import Flask, jsonify, request
from geojson_to_shapefile import *
import sys

app = Flask(__name__)

@app.route('/prd', methods=['POST'])
def production_map():
    data = request.get_json()
    print(data, file=sys.stderr)
    generate_production_map_shapefile(data["input_path"], data["output_dir"])
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
