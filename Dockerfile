FROM python:3.10.12-slim

COPY requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt && \
    rm -rf requirements.txt

WORKDIR /app
COPY agent.py agent.py

ENTRYPOINT ["python", "agent.py"]
