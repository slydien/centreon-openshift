# Centreon OpenShift Overlay

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
│  ├─ Dockerfile.alma8.openshift
│  ├─ Dockerfile.alma9.openshift
│  ├─ Dockerfile.bookworm.openshift
│  ├─ Dockerfile.jammy.openshift
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

Web (Alma8):
```
docker build -f web/Dockerfile.alma8.openshift \
  -t slydien/centreon-web-alma8:24.10-openshift \
  --build-arg=REGISTRY_URL=docker.io/slydien \
  --build-arg=FROM_IMAGE_VERSION=24.10 \
  --build-arg=STABILITY=stable \
  --platform=linux/amd64 .
```

Web (Bookworm):
```
docker build -f web/Dockerfile.bookworm.openshift \
  -t slydien/centreon-web-bookworm:24.10-openshift \
  --build-arg=REGISTRY_URL=docker.io/slydien \
  --build-arg=FROM_IMAGE_VERSION=24.10 \
  --build-arg=STABILITY=stable \
  --platform=linux/amd64 .
```

Web (Jammy):
```
docker build -f web/Dockerfile.jammy.openshift \
  -t slydien/centreon-web-jammy:24.10-openshift \
  --build-arg=REGISTRY_URL=docker.io/slydien \
  --build-arg=FROM_IMAGE_VERSION=24.10 \
  --build-arg=STABILITY=stable \
  --platform=linux/amd64 .
```
