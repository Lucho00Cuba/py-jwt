FROM alpine:latest

ARG DUMB_INIT
ARG BUILD_DATE

LABEL maintainer="lomv0209@gmail.com" \
      owner="JustMe" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/Lucho00Cuba/py-jwt.git"

# ------ https://github.com/Yelp/dumb-init ------
ENV DUMB_INIT_VERSION=${DUMB_INIT:-1.2.0}
ADD https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_amd64 /bin/dumb-init
# -----------------------------------------------

WORKDIR /app

COPY ./src/* .

RUN apk add --update --no-cache python3 py3-pip gcc python3-dev linux-headers libc-dev build-base && \
    rm -rf /var/cache/apk/* && \
    chmod +x /bin/dumb-init && \
    chmod +x /app/main.py && \
    pip install -r requirements.txt

ENV FLASK_APP="/app/main.py"

EXPOSE 8080

ENTRYPOINT ["/bin/dumb-init"]

CMD ["python3" ,"main.py"]