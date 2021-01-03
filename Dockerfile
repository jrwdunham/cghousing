FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
  software-properties-common \
  vim \
  wget \
  build-essential \
  curl \
  alien \
  libaio1 \
  libaio-dev \
  libxrender1 \
  libfontconfig1 \
  rpm2cpio \
  cpio \
  unzip \
  libsasl2-dev \
  libldap2-dev \
  libssl-dev

ENV DEBIAN_FRONTEND noninteractive

RUN wget -qO- "https://yihui.name/gh/tinytex/tools/install-unx.sh" | sh
RUN mkdir /src
RUN rm -rf /src/TinyTeX
RUN mv /root/.TinyTeX /src/TinyTeX
RUN ln -s /src/TinyTeX/bin/x86_64-linux/pdflatex /usr/local/bin/pdflatex
RUN ln -s /src/TinyTeX/bin/x86_64-linux/tlmgr /usr/local/bin/tlmgr
RUN /src/TinyTeX/bin/x86_64-linux/tlmgr path add \
    && /src/TinyTeX/bin/x86_64-linux/tlmgr install \
        amsfonts \
        amsmath \
        auxhook \
        catchfile \
        fancyhdr \
        fancyvrb \
        float \
        fourier \
        fouriernc \
        fvextra \
        geometry \
        gettitlestring \
        hyperref \
        hyphenat \
        ifplatform \
        kvoptions \
        lastpage \
        lineno \
        minted \
        ms \
        ncntrsbk \
        parskip \
        psnfss \
        rerunfilecheck \
        textpos \
        url \
        xcolor \
        xstring \
        cm-super

# End LaTeX install, begin Python/Django install

RUN apt-get install -y \
    postgresql \
    gcc \
    python-dev \
    musl-dev \
    curl \
    libmagic-dev

RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python get-pip.py

RUN mkdir /static
RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV CG_DEPLOY_TYPE=prod
ENV CG_STATIC_ROOT=/static

EXPOSE 8000