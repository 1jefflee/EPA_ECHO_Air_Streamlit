FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    netbase \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r requirements.txt

EXPOSE 8501

COPY . .

ENTRYPOINT ["streamlit", "run"]

CMD ["app.py", "--server.address=0.0.0.0", "--server.port=8501"]