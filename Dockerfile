FROM python:3.11

ENV SHELL=/bin/bash

RUN apt-get update \
    && apt-get install -y sudo ca-certificates curl gnupg git vim gettext tmux make tree \
    && apt-get clean

WORKDIR /src

RUN python3 -m venv /src/.venv
ENV PATH="/src/.venv/bin:$PATH"

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN cd ~/ && git clone https://github.com/primestyle-co/dotfiles && python3 dotfiles/install.py;

CMD ["/bin/bash", "-c", "source /src/.venv/bin/activate && exec bash"]
