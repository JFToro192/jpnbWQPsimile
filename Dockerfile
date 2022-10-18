###################################
#   ESA-SNAP mundialis base image
###################################
FROM mundialis/esa-snap:8.0-ubuntu

###################################
#   Jupyterlab setup
###################################
USER root

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean && rm -rf var/lib/apt/lists/*

RUN pip install jupyter -U && pip install jupyterlab

###################################
#   ESA-SNAP setup
###################################

## Move local packages to tmp file
COPY setup/requirements.txt /tmp/base_requirements.txt

# Update snap-tools
# If not running locally GitHub Actions will take care of compiling,
# only pulling the image from DockerHub is needed then
## This line results in an infinite loop, better use the .sh
# RUN /usr/local/snap/bin/snap --nosplash --nogui --modules --refresh --update-all
# RUN /usr/local/snap/bin/snap --nosplash --nogui --modules --refresh org.esa.s3tbx.s3tbx.landsat.reader org.esa.s3tbx.s3tbx.c2rcc
## When not running behind a firewall, uncomment the next two lines

# Uncomment the following lines if required to update snap
RUN apt install locales
RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure locales
COPY setup/update-snap.sh /tmp/update-snap.sh
RUN bash /tmp/update-snap.sh

## Install requirements for python
RUN python3.6 -m pip install --upgrade pip
RUN python3.6 -m pip install --no-cache-dir --upgrade -r /tmp/base_requirements.txt

# Install snaphu
RUN wget --no-check-certificate  \
    https://web.stanford.edu/group/radar/softwareandlinks/sw/snaphu/snaphu-v2.0.5.tar.gz \
    && tar -xvf snaphu-v2.0.5.tar.gz \
    && rm snaphu-v2.0.5.tar.gz \
    && mkdir -p /usr/local/man/man1/ \
    && cd ./snaphu-v2.0.5/src \
    && make install \
    && make Clean

# Install GDAL
RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin unzip

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

###################################
#   Miniconda installation 
###################################
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN conda install -c conda-forge nb_conda_kernels ipykernel

###################################
#   WQP processing venv 
###################################

# Create SNAP processing env
COPY ./packages ./packages
RUN conda env create -f packages/environment.yml

# Add the environment to the kernels of jupyterlab
SHELL ["conda","run","-n","snapEnv","/bin/bash","-c"]
RUN python -m ipykernel install --name snapEnv --display-name "snapEnv (Python)"
RUN pip install -U -r packages/requirements.txt
RUN rm -rf packages


# TODO: setup the snappy api for using gpt from python scripts

###################################
#   WQP + snappy 
###################################

# Configuring SNAP-Python interface. 
# Reference setup
# - https://github.com/schwankner/esa-snap-with-python
# - https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface
RUN /usr/local/snap/bin/snappy-conf /usr/bin/python3.6
RUN cd /root/.snap/snap-python/snappy/ && \
    python setup.py install

###################################
#   Expose and Run Jupyter NB
###################################
SHELL ["/bin/bash","-c"]
RUN conda init
RUN echo 'conda activate snapEnv' >> ~/.bashrc

WORKDIR /home/jovyan/work

EXPOSE 8888

# FIXME: Define a bash for the kernels 
ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--NotebookApp.token='jpbn'"]