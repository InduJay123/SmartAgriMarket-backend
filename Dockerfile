FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev pkg-config default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Upgrade pip first, then install requirements with retries
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir --retries 5 --timeout 60 -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]