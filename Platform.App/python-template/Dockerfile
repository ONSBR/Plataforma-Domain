FROM pmoneda/domain_base:latest

WORKDIR /app
COPY . .
ENV POSTGRES_HOST "postgres-hom.czqebrnlxa8n.us-east-1.rds.amazonaws.com"
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV DB_NAME sager
EXPOSE 9110
ENTRYPOINT if [ "$DOMAIN_API" -eq "1" ]; then python main.py && gunicorn -b 0.0.0.0:9110 --timeout 300000 app.wsgi:app;else python run.py; fi
