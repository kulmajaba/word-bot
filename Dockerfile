# Image setup
FROM python:3.8.2-slim
ENV PYTHONUNBUFFERED 1
RUN pip install pipenv

WORKDIR /src

# Dependencies
COPY Pipfile /src
COPY Pipfile.lock /src
RUN pipenv install --system --deploy

# Copy code
COPY src /src
COPY .env /src

# Entry point
CMD ["python", "visitorbot.py"]
