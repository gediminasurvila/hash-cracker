FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
john \
john-data \
hashcat \
hashcat-data \
ocl-icd-libopencl1 \
curl \
libssl-dev \
libgomp1 \
dpkg \
&& rm -rf /var/lib/apt/lists/* \
&& apt-get clean


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /tmp/uploads

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production 
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]