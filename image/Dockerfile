FROM python:3.6

USER root

WORKDIR /app
RUN pip install colorlover \
dash \
dash_core_components \
dash_html_components \
fiona \
geoalchemy2 \
geojson \
geopandas \
netcdf4 \
progressbar \
pyproj \
pyyaml \
rasterio \
sqlalchemy \
xarray

ADD requirements.txt .
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt

ADD app.py /app/app.py
ADD index.py /app/index.py

RUN mkdir assets
RUN mkdir apps
ADD ./apps /app/apps


EXPOSE 8050

CMD ["python", "index.py"]
