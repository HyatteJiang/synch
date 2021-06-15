FROM python:3
RUN git clone https://hub.fastgit.org/HyatteJiang/mysqlparse.git
WORKDIR /mysqlparse
RUN python setup.py install
RUN mkdir -p /synch
WORKDIR /synch
COPY pyproject.toml poetry.lock /synch/
RUN pip3 install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-root
COPY . /synch
RUN poetry install
RUN pip3 install pymysql==0.9.3