# Centreon OpenShift Overlay

[![web-image](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml/badge.svg?branch=main&label=web-image)](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml)
[![helm-chart](https://github.com/slydien/centreon-openshift/actions/workflows/publish-helm-chart.yml/badge.svg?branch=main&label=helm-chart)](https://github.com/slydien/centreon-openshift/actions/workflows/publish-helm-chart.yml)

This repo holds OpenShift overlay Dockerfiles and helper assets for Centreon, layering on top of the Docker images published in the Centreon repository. See Centreon’s Docker build documentation: https://github.com/centreon/centreon/blob/develop/.github/docker/README.md

It is structured to support multiple components (web now, poller later).

## Layout
```
.
├─ common/
│  ├─ fix-permissions
│  └─ openshift/
│     ├─ sudoers
│     ├─ sudo-wrapper
│     └─ patches/
│        ├─ apache-listen-8080.patch
│        └─ poller-generate-disable-ownership.patch
├─ web/
│  ├─ Dockerfile.alma9.openshift
│  └─ config/
│     ├─ httpd/
│     │  ├─ 10-centreon.conf
│     │  └─ zzz-openshift-runtime.conf
│     ├─ php-fpm/
│     │  └─ centreon.conf
│     ├─ apache2/
│     │  ├─ centreon.conf
│     │  ├─ ports.conf
│     │  └─ zzz-openshift-runtime.conf
│     └─ php-fpm-debian/
│        └─ centreon.conf
└─ poller/
   └─ (placeholders for future poller overlays)
```

## Build examples
Web (Alma9):
```
docker build -f web/Dockerfile.alma9.openshift \
  -t slydien/centreon-web-alma9:24.10-openshift \
  --build-arg=REGISTRY_URL=docker.io/slydien \
  --build-arg=FROM_IMAGE_VERSION=24.10 \
  --build-arg=STABILITY=stable \
  --platform=linux/amd64 .
```

## Helm chart
See `helm/centreon-openshift/README.md` for chart usage and values documentation.
