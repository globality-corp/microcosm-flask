#
#  Globality autogenerated Docker configuration
#
#  This file is auto generated with globality-build.
#  You should not make any changes to this file manually
#
#  Any changes made to this file will be overwritten in the
#  next version of the build.
#
#  See: http://github.com/globality-corp/globality-build
#
#

# ----------- deps -----------
# Install from Debian Stretch with modern Python support
FROM python:slim-stretch as deps

#
# Most services will use the same set of packages here, though a few will install
# custom dependencies for native requirements.
#

ARG EXTRA_INDEX_URL
ENV EXTRA_INDEX_URL ${EXTRA_INDEX_URL}

ENV CORE_PACKAGES locales
ENV BUILD_PACKAGES build-essential libffi-dev
ENV OTHER_PACKAGES libssl-dev


RUN apt-get update && \
    apt-get install -y --no-install-recommends ${CORE_PACKAGES} ${BUILD_PACKAGES} && \
    apt-get install -y --no-install-recommends ${OTHER_PACKAGES} && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*


# ----------- base -----------

FROM deps as base

# Install dependencies
#
# Since many Python distributions require a compile for their native dependencies
# we install a compiler and any required development libraries before the installation
# and then *remove* the the compiler when we are done.
#
# We can control dependency freezing by managing the contents of `requirements.txt`.
#
# We can speed up the installation a little bit by breaking out the common
# pip dependencies into their own layer, but avoid this optimization for
# now to improve clarity.
#
# We also install the web application server (which should not be one of our
# explicit dependencies).
#
# Many services will need to modify this step for Python libraries with other
# native dependencies.


# Work in /src
#
# We'll copy local source code here for development.
WORKDIR src

# Set a proper locale
#
# UTF-8 everywhere.

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen "en_US.UTF-8" && \
    /usr/sbin/update-locale LANG=en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Install top-level files
#
# These are enough to install dependencies and have a stable base layer
# when source code changes.

# copy pyproject.toml and HISTORY.rst only if they exist
COPY README.md MANIFEST.in setup.cfg setup.py pyproject.tom[l] HISTORY.rs[t] conftest.p[y] /src/

RUN pip install --no-cache-dir --upgrade --extra-index-url ${EXTRA_INDEX_URL} /src/ && \
    apt-get remove --purge -y ${BUILD_PACKAGES} && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*


# ----------- final -----------
FROM base

# Setup invocation
#
# We expose the application on the standard HTTP port and use an entrypoint
# to customize the `dev` and `test` targets.

ENV NAME microcosm_flask
COPY entrypoint.sh /src/
ENTRYPOINT ["./entrypoint.sh"]

# Install source
#
# We should not need to reinstall dependencies here, but we do need to import
# the distribution properly. We also save build arguments to the image using
# microcosm-compatible environment variables.


ARG BUILD_NUM
ARG SHA1
ENV MICROCOSM_FLASK__BUILD_INFO_CONVENTION__BUILD_NUM ${BUILD_NUM}
ENV MICROCOSM_FLASK__BUILD_INFO_CONVENTION__SHA1 ${SHA1}
COPY $NAME /src/$NAME/
RUN pip install --no-cache-dir --extra-index-url $EXTRA_INDEX_URL -e .
