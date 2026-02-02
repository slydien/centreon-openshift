# Centreon OpenShift Overlay

[![web-image](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml/badge.svg?branch=main&label=web-image)](https://github.com/slydien/centreon-openshift/actions/workflows/build-web-images.yml)
[![poller-image](https://github.com/slydien/centreon-openshift/actions/workflows/build-poller-images.yml/badge.svg?branch=main&label=poller-image)](https://github.com/slydien/centreon-openshift/actions/workflows/build-poller-images.yml)
[![helm-chart](https://github.com/slydien/centreon-openshift/actions/workflows/publish-helm-chart.yml/badge.svg?branch=main&label=helm-chart)](https://github.com/slydien/centreon-openshift/actions/workflows/publish-helm-chart.yml)

This repo holds OpenShift overlay Dockerfiles and helper assets for Centreon, layering on top of the Docker images published in the Centreon repository. See Centreon’s Docker build documentation in `https://github.com/centreon/centreon/blob/develop/.github/docker/README.md`.

It provides overlays for both web and poller images, plus a Helm chart for OpenShift.

## Layout
```
.
├─ common/                          # Shared overlay assets used by web/poller images.
│  ├─ fix-permissions               # Helper to normalize file ownership/permissions.
│  └─ openshift/                    # OpenShift-specific helpers and patches.
│     ├─ sudoers                    # Sudo policy used inside OpenShift images.
│     ├─ sudo-wrapper               # Wrapper script for controlled sudo usage.
│     ├─ fix-poller-gen.py          # Adjustments for poller generation on OpenShift.
│     └─ patches/                   # Common patch set applied to base images.
│        ├─ 00-init.sh.patch        # Init script tweaks for OpenShift runtime.
│        ├─ ignore-vmware-chgrp.patch
│        ├─ poller-generate-disable-ownership.patch
│        └─ systemctl.patch
├─ docs/                            # Design notes, plans, and TODOs.
│  ├─ PLAN-helm-chart-ci-testing.md # CI testing plan for the Helm chart.
│  └─ TODO-openshift-uid-compatibility.md
├─ helm/                            # Helm charts for OpenShift deployment.
│  └─ centreon-openshift/           # Main Helm chart and templates.
│     ├─ Chart.yaml                 # Chart metadata.
│     ├─ README.md                  # Chart usage and values documentation.
│     ├─ templates/                 # Kubernetes/OpenShift manifests.
│     └─ values.yaml                # Default chart configuration.
├─ web/                             # Web image overlay (Dockerfile + patches + configs).
│  ├─ Dockerfile.alma9.openshift    # OpenShift overlay Dockerfile for web image.
│  ├─ patches/                      # Web container patch set.
│  │  ├─ 15-installation.sh.patch
│  │  ├─ 20-configuration_files.sh.patch
│  │  ├─ 70-gorgone.sh.patch
│  │  ├─ 71-vault.sh.patch
│  │  ├─ 72-authentication.sh.patch
│  │  ├─ 99-logs.sh.patch
│  │  ├─ apache-listen-8080.patch
│  │  └─ broker.json.patch
│  └─ config/                       # Service configs injected into the image.
│     ├─ httpd/                     # httpd config for RHEL/Alma variants.
│     ├─ php-fpm/                   # php-fpm config for RHEL/Alma variants.
│     ├─ apache2/                   # Apache config for Debian/Ubuntu variants.
│     └─ php-fpm-debian/            # php-fpm config for Debian/Ubuntu variants.
└─ poller/                          # Poller image overlay (Dockerfile + patches).
   ├─ Dockerfile.alma9.openshift    # OpenShift overlay Dockerfile for poller image.
   ├─ patches/                      # Poller container patch set.
   │  └─ 60-register_central.sh.patch
   └─ extra-patches/                # Additional patches applied to poller internals.
      └─ gorgone-action-chown.patch
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
