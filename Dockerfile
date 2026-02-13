FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download VAD and turn detector models at build time
RUN python -c "from livekit.plugins import silero; silero.VAD.load()"

# Copy application code
COPY . .

# Run the agent
CMD ["python", "agent.py", "start"]
