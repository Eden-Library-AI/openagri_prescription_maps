# Use an official GDAL image as the base image
# https://github.com/OSGeo/gdal/tree/master/docker

FROM ghcr.io/osgeo/gdal:ubuntu-small-latest

RUN apt-get update
RUN apt-get -y install build-essential libssl-dev libffi-dev python3-venv python3-dev --fix-missing

EXPOSE 5000

# Create VENV for python
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run Flask
COPY run_flask.py .
COPY geojson_to_shapefile.py .
CMD ["python", "run_flask.py"]
