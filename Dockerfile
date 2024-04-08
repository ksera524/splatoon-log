FROM python:3-alpine

ENV PYTHONIOENCODING utf-8
WORKDIR /app

RUN apk add --update \
        chromium \
        chromium-chromedriver \
    && rm -rf /var/cache/apk/*

# Copy necessary scripts and configuration files
COPY main.py slack.py requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run when the container starts
CMD ["python", "main.py"]
