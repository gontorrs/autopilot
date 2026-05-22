FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/Code

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/aibasel/downward.git /opt/fast-downward \
    && /opt/fast-downward/build.py release

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        crewai==1.14.1 \
        requests==2.32.5

COPY Code/crew /app/Code/crew
COPY Code/pddl /app/Code/pddl
COPY Code/services /app/Code/services

WORKDIR /app/Code

CMD ["python", "-u", "services/planner_service.py"]
