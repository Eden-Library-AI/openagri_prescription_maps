# OpenAgri Co-develop service
This repository contais the proper code to convert Eden Library's Viewer geoJSON files into prescription maps.


## Setup
In order to set up the repository there is a docker file Under `openagri_prescription_maps/src` run:

```
docker build -t elv_jdoc .
docker run -p 5000:5000 -v /PATH/TO/input_data:/input_data -v /PATH/TO/output_data:/output_data elv_jdoc:latest
```

## API Calls

In terminal run:

```
curl -X POST http://127.0.0.1:5000/prd -d '{"input_path": "/input_data/INPUT_JSON_FILENAME.json", "output_dir": "/output_data"}' -H "Content-Type: application/json"
```
in the output directory you will get a zip file with all the necessary files for a prescription map that can be loaded in a sprayer