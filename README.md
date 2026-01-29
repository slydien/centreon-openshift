# Centreon OpenShift Overlay

[![web-image v24.10](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml/badge.svg?branch=main&label=web-image%20v24.10)](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml)
[![web-image v25.10](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml/badge.svg?branch=main&label=web-image%20v25.10)](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml)

This repo holds OpenShift overlay Dockerfiles and helper assets for Centreon.

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
The OpenShift Helm chart lives in `helm/centreon-openshift`.

Install (namespace `centreon`):
```
helm install centreon-openshift helm/centreon-openshift -n centreon
```

Upgrade:
```
helm upgrade --install centreon-openshift helm/centreon-openshift -n centreon
```

Uninstall:
```
helm uninstall centreon-openshift -n centreon
```

Customize values:
```
helm upgrade --install centreon-openshift helm/centreon-openshift \
  -n centreon \
  -f helm/centreon-openshift/values.yaml
```
