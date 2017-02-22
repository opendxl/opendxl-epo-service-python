############################################################
# Dockerfile used to run the ePO DXL service (Python)
############################################################

# Base image from Python 2.7 (alpine)
FROM python:2.7-alpine

# Install required packages
RUN pip install requests
RUN pip install dxlclient

# Build service
COPY . /tmp/build
WORKDIR /tmp/build
RUN python ./setup.py bdist_wheel

# Install service
RUN pip install dist/*.whl

# Cleanup build
RUN rm -rf /tmp/build

################### INSTALLATION END #######################
#
# Run the service.
#
# NOTE: The configuration files for the service must be
#       mapped to the path: /opt/dxleposervice/config
#
# For example, specify a "-v" argument to the run command
# to mount a directory on the host as a data volume:
#
#   -v /host/dir/to/config:/opt/dxleposervice/config
#
CMD ["python", "-m", "dxleposervice", "/opt/dxleposervice-config"]