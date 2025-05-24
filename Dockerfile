FROM alpine:3

ARG BUILD_DATETIME=unknown

LABEL org.opencontainers.image.source="https://github.com/ByTheHugo/kubeboard"
LABEL org.opencontainers.image.description="A simple web GUI to visualise the applications that are available in a Kubernetes cluster."
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.created="${BUILD_DATETIME}"

LABEL io.artifacthub.package.license="Apache-2.0"
LABEL io.artifacthub.package.category="monitoring-logging"
LABEL io.artifacthub.package.logo-url="https://raw.githubusercontent.com/ByTheHugo/kubeboard/refs/heads/master/docs/compass.png"
LABEL io.artifacthub.package.readme-url="https://raw.githubusercontent.com/ByTheHugo/kubeboard/refs/heads/master/README.md"
LABEL io.artifacthub.package.maintainers='[{"name":"Hugo CHUPIN","email":"hugo@chupin.xyz"}]'
LABEL io.artifacthub.package.keywords="kube board,kubernetes,kube,dashboard,ingress,gui"

WORKDIR /app

# hadolint ignore=DL3018
RUN apk add --update --no-cache python3 py3-pip \
  && addgroup --gid 10001 kubeboard \
  && adduser --home /app --disabled-password -u 10001 -G kubeboard kubeboard

COPY requirements.txt .

RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

RUN chown -R kubeboard:kubeboard .

USER kubeboard

CMD [ "python3", "-m", "flask", "run" ]
