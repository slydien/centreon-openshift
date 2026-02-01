# Centreon OpenShift Overlay

[![web-image](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml/badge.svg?branch=main&label=web-image)](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml)
[![poller-image](https://github.com/slydien/centreon-openshift/actions/workflows/build-poller-images.yml/badge.svg?branch=main&label=poller-image)](https://github.com/slydien/centreon-openshift/actions/workflows/build-poller-images.yml)
[![helm-chart](https://github.com/slydien/centreon-openshift/actions/workflows/publish-helm-chart.yml/badge.svg?branch=main&label=helm-chart)](https://github.com/slydien/centreon-openshift/actions/workflows/publish-helm-chart.yml)

This repo holds OpenShift overlay Dockerfiles and helper assets for Centreon, layering on top of the Docker images published in the Centreon repository. See Centreon’s Docker build documentation in `https://github.com/centreon/centreon/blob/develop/.github/docker/README.md`.

It provides overlays for both web and poller images, plus a Helm chart for OpenShift.

## Layout
```
.
├─ common/
│  ├─ fix-permissions
│  └─ openshift/
│     ├─ sudoers
│     ├─ sudo-wrapper
│     ├─ patches/
│        ├─ apache-listen-8080.patch
│        ├─ ignore-vmware-chgrp.patch
│        └─ poller-generate-disable-ownership.patch
│     └─ fix-poller-gen.py
├─ helm/
│  └─ centreon-openshift/
│     ├─ Chart.yaml
│     ├─ README.md
│     ├─ templates/
│     └─ values.yaml
├─ web/
│  ├─ Dockerfile.alma9.openshift
│  ├─ patches/
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
   ├─ Dockerfile.alma9.openshift
   ├─ patches/
   └─ extra-patches/
```

## Build examples
Web (Alma9):
```
docker build -f web/Dockerfile.alma9.openshift \
  -t ghcr.io/slydien/centreon-web-alma9:24.10-openshift \
  --build-arg=REGISTRY_URL=ghcr.io/slydien \
  --build-arg=FROM_IMAGE_VERSION=24.10 \
  --build-arg=STABILITY=stable \
  --platform=linux/amd64 .
```

Poller (Alma9):
```
docker build -f poller/Dockerfile.alma9.openshift \
  -t ghcr.io/slydien/centreon-poller-alma9:24.10-openshift \
  --build-arg=REGISTRY_URL=ghcr.io/slydien \
  --build-arg=FROM_IMAGE_VERSION=24.10 \
  --build-arg=STABILITY=stable \
  --platform=linux/amd64 .
```

## Helm chart
See `helm/centreon-openshift/README.md` for chart usage and values documentation.
