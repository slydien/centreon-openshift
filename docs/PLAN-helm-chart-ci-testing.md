# Implementation Plan: Helm Chart CI Testing with CRC/MicroShift

## Overview

This document outlines the plan to integrate the [crc-org/crc-github-action](https://github.com/crc-org/crc-github-action) into the CI pipeline to test the Helm chart by deploying it to a MicroShift (lightweight OpenShift) environment during CI.

### Goals

1. Automatically test Helm chart deployments on PRs that modify:
   - Helm chart files (`helm/**`)
   - Docker image files (`web/Dockerfile*`, `poller/Dockerfile*`)
2. Build Docker images when Dockerfiles are modified
3. Deploy the Centreon stack to MicroShift
4. Verify all pods pass health checks
5. Report deployment success/failure

---

## Architecture

### Workflow Strategy: Two-Stage Build-Then-Test (Option C)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Pull Request Created                         │
│            (modifies helm/** OR **/Dockerfile*)                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Job 1: Detect Changes                          │
│  - Determine which files changed (Dockerfiles vs Helm only)         │
│  - Set output flags for downstream jobs                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│  Job 2a: Build Web Image      │   │  Job 2b: Build Poller Image   │
│  (only if web Dockerfile      │   │  (only if poller Dockerfile   │
│   changed)                    │   │   changed)                    │
│  - Build image locally        │   │  - Build image locally        │
│  - Export as artifact         │   │  - Export as artifact         │
└───────────────────────────────┘   └───────────────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Job 3: Test Helm Deployment                       │
│  - Free up disk space (~43GB available)                             │
│  - Setup CRC with MicroShift preset                                 │
│  - Load built images (if any) OR use GHCR images                    │
│  - Install Helm chart                                               │
│  - Wait for pods to become ready (health checks)                    │
│  - Report success/failure                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Resource Requirements

### GitHub Runner (ubuntu-latest)

| Resource | Available | After Cleanup |
|----------|-----------|---------------|
| CPU | 2 cores | 2 cores |
| RAM | 7 GB | 7 GB |
| Disk | ~20 GB free | ~43 GB free |
| Architecture | x86_64 (amd64) | x86_64 (amd64) |

> **Note**: Centreon images are only available for x86_64 architecture. GitHub's `ubuntu-latest` runners are x86_64 by default, so this is compatible.

### MicroShift Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 2 cores |
| RAM | 2 GB | 4 GB |
| Disk | 2 GB | 10+ GB |

### Centreon Stack Requirements (Estimated)

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Web | 0.5 core | 1 GB | 1 GB |
| Database (MariaDB) | 0.5 core | 512 MB | 1 GB |
| Poller | 0.5 core | 512 MB | 500 MB |
| **Total** | 1.5 cores | 2 GB | 2.5 GB |

**Conclusion**: The standard `ubuntu-latest` runner with disk cleanup should be sufficient.

---

## Implementation Details

### New Workflow File

**Path**: `.github/workflows/test-helm-deployment.yml`

### Workflow Triggers

```yaml
on:
  pull_request:
    paths:
      - 'helm/**'
      - 'web/Dockerfile*'
      - 'poller/Dockerfile*'
      - 'common/**'
      - '.github/workflows/test-helm-deployment.yml'
```

### Job 1: Detect Changes

**Purpose**: Determine which components changed to optimize the build process.

**Outputs**:
- `web_changed`: true/false
- `poller_changed`: true/false
- `helm_changed`: true/false

**Implementation**:
```yaml
detect-changes:
  runs-on: ubuntu-latest
  outputs:
    web_changed: ${{ steps.changes.outputs.web }}
    poller_changed: ${{ steps.changes.outputs.poller }}
    helm_changed: ${{ steps.changes.outputs.helm }}
  steps:
    - uses: actions/checkout@v4
    - uses: dorny/paths-filter@v3
      id: changes
      with:
        filters: |
          web:
            - 'web/**'
            - 'common/**'
          poller:
            - 'poller/**'
            - 'common/**'
          helm:
            - 'helm/**'
```

### Job 2a/2b: Build Images (Conditional)

**Purpose**: Build Docker images only when their source files change.

**Strategy**:
- Build images using Docker Buildx
- Save images as tar archives
- Upload as GitHub artifacts for the test job

**Implementation**:
```yaml
build-web-image:
  needs: detect-changes
  if: needs.detect-changes.outputs.web_changed == 'true'
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: docker/setup-buildx-action@v3
    - name: Build web image
      uses: docker/build-push-action@v6
      with:
        context: .
        file: web/Dockerfile.alma9.openshift
        platforms: linux/amd64  # x86_64 only
        build-args: |
          REGISTRY_URL=docker.io/slydien
          FROM_IMAGE_VERSION=24.10
          STABILITY=stable
        tags: centreon-web-alma9:test
        outputs: type=docker,dest=/tmp/web-image.tar
    - uses: actions/upload-artifact@v4
      with:
        name: web-image
        path: /tmp/web-image.tar
        retention-days: 1
```

### Job 3: Test Helm Deployment

**Purpose**: Deploy the Helm chart to MicroShift and verify health checks pass.

**Steps**:

1. **Free Disk Space** (~43 GB available after cleanup)
   ```yaml
   - uses: jlumbroso/free-disk-space@v1.3.1
     with:
       tool-cache: false
       android: true
       dotnet: true
       haskell: true
       large-packages: true
       docker-images: true
       swap-storage: true
   ```

2. **Setup CRC/MicroShift**
   ```yaml
   - uses: crc-org/crc-github-action@v1
     with:
       preset: microshift
       # Using defaults for CPU/memory/disk
   ```

3. **Download Built Images** (if any)
   ```yaml
   - uses: actions/download-artifact@v4
     if: needs.detect-changes.outputs.web_changed == 'true'
     with:
       name: web-image
       path: /tmp
   ```

4. **Load Images into CRC**
   ```yaml
   - name: Load images into MicroShift
     run: |
       # Load locally built images
       if [ -f /tmp/web-image.tar ]; then
         podman load -i /tmp/web-image.tar
       fi
       if [ -f /tmp/poller-image.tar ]; then
         podman load -i /tmp/poller-image.tar
       fi
   ```

5. **Install Helm Chart**
   ```yaml
   - name: Install Helm chart
     run: |
       helm install centreon ./helm/centreon-openshift \
         --namespace centreon \
         --create-namespace \
         --set services.web.image.repository=<appropriate-image> \
         --set services.poller.image.repository=<appropriate-image> \
         --wait \
         --timeout 15m
   ```

6. **Verify Health Checks**
   ```yaml
   - name: Wait for pods to be ready
     run: |
       kubectl wait --for=condition=ready pod \
         -l app.kubernetes.io/instance=centreon \
         -n centreon \
         --timeout=600s

       # Additional health check verification
       kubectl get pods -n centreon
       kubectl describe pods -n centreon
   ```

7. **Debug on Failure** (optional)
   ```yaml
   - name: Debug info on failure
     if: failure()
     run: |
       kubectl get all -n centreon
       kubectl describe pods -n centreon
       kubectl logs -l app.kubernetes.io/instance=centreon -n centreon --all-containers
   ```

---

## Complete Workflow File

```yaml
name: Test Helm Chart Deployment

on:
  pull_request:
    paths:
      - 'helm/**'
      - 'web/Dockerfile*'
      - 'poller/Dockerfile*'
      - 'common/**'
      - '.github/workflows/test-helm-deployment.yml'
  workflow_dispatch:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      web_changed: ${{ steps.changes.outputs.web }}
      poller_changed: ${{ steps.changes.outputs.poller }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            web:
              - 'web/**'
              - 'common/**'
            poller:
              - 'poller/**'
              - 'common/**'

  build-web-image:
    needs: detect-changes
    if: needs.detect-changes.outputs.web_changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build web image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: web/Dockerfile.alma9.openshift
          platforms: linux/amd64
          build-args: |
            REGISTRY_URL=docker.io/slydien
            FROM_IMAGE_VERSION=24.10
            STABILITY=stable
          tags: centreon-web-alma9:test
          outputs: type=docker,dest=/tmp/web-image.tar
      - uses: actions/upload-artifact@v4
        with:
          name: web-image
          path: /tmp/web-image.tar
          retention-days: 1

  build-poller-image:
    needs: detect-changes
    if: needs.detect-changes.outputs.poller_changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build poller image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: poller/Dockerfile.alma9.openshift
          platforms: linux/amd64
          build-args: |
            REGISTRY_URL=ghcr.io/slydien
            FROM_IMAGE_VERSION=24.10
            STABILITY=stable
          tags: centreon-poller-alma9:test
          outputs: type=docker,dest=/tmp/poller-image.tar
      - uses: actions/upload-artifact@v4
        with:
          name: poller-image
          path: /tmp/poller-image.tar
          retention-days: 1

  test-deployment:
    needs: [detect-changes, build-web-image, build-poller-image]
    # Always run, even if build jobs were skipped
    if: always() && !cancelled() && !contains(needs.*.result, 'failure')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Free disk space
        uses: jlumbroso/free-disk-space@v1.3.1
        with:
          tool-cache: false
          android: true
          dotnet: true
          haskell: true
          large-packages: true
          docker-images: true
          swap-storage: true

      - name: Setup CRC (MicroShift)
        uses: crc-org/crc-github-action@v1
        with:
          preset: microshift

      - name: Download web image artifact
        if: needs.detect-changes.outputs.web_changed == 'true'
        uses: actions/download-artifact@v4
        with:
          name: web-image
          path: /tmp

      - name: Download poller image artifact
        if: needs.detect-changes.outputs.poller_changed == 'true'
        uses: actions/download-artifact@v4
        with:
          name: poller-image
          path: /tmp

      - name: Load and push images to MicroShift registry
        run: |
          # Determine image sources
          WEB_IMAGE="ghcr.io/slydien/centreon-web-alma9:24.10-openshift"
          POLLER_IMAGE="ghcr.io/slydien/centreon-poller-alma9:24.10-openshift"

          # Load locally built images if available
          if [ -f /tmp/web-image.tar ]; then
            echo "Loading locally built web image..."
            podman load -i /tmp/web-image.tar
            WEB_IMAGE="localhost/centreon-web-alma9:test"
          fi

          if [ -f /tmp/poller-image.tar ]; then
            echo "Loading locally built poller image..."
            podman load -i /tmp/poller-image.tar
            POLLER_IMAGE="localhost/centreon-poller-alma9:test"
          fi

          # Export for later steps
          echo "WEB_IMAGE=$WEB_IMAGE" >> $GITHUB_ENV
          echo "POLLER_IMAGE=$POLLER_IMAGE" >> $GITHUB_ENV

      - name: Setup Helm
        uses: azure/setup-helm@v4

      - name: Create namespace
        run: kubectl create namespace centreon

      - name: Install Helm chart
        run: |
          helm install centreon ./helm/centreon-openshift \
            --namespace centreon \
            --set services.web.image.repository=${WEB_IMAGE%:*} \
            --set services.web.image.tag=${WEB_IMAGE#*:} \
            --set services.poller.image.repository=${POLLER_IMAGE%:*} \
            --set services.poller.image.tag=${POLLER_IMAGE#*:} \
            --timeout 15m

      - name: Wait for pods to be ready
        run: |
          echo "Waiting for all pods to be ready..."
          kubectl wait --for=condition=ready pod \
            -l app.kubernetes.io/instance=centreon \
            -n centreon \
            --timeout=600s

          echo "All pods are ready!"
          kubectl get pods -n centreon

      - name: Verify services
        run: |
          echo "=== Pod Status ==="
          kubectl get pods -n centreon -o wide

          echo "=== Services ==="
          kubectl get svc -n centreon

          echo "=== Routes ==="
          kubectl get routes -n centreon 2>/dev/null || echo "Routes not available in MicroShift"

      - name: Debug info on failure
        if: failure()
        run: |
          echo "=== All Resources ==="
          kubectl get all -n centreon

          echo "=== Pod Descriptions ==="
          kubectl describe pods -n centreon

          echo "=== Pod Logs ==="
          for pod in $(kubectl get pods -n centreon -o jsonpath='{.items[*].metadata.name}'); do
            echo "--- Logs for $pod ---"
            kubectl logs $pod -n centreon --all-containers --tail=100 || true
          done

          echo "=== Events ==="
          kubectl get events -n centreon --sort-by='.lastTimestamp'
```

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `.github/workflows/test-helm-deployment.yml` | Create | New workflow for Helm chart testing |
| `helm/centreon-openshift/values.yaml` | Potentially modify | May need adjustments for test environment |

---

## Testing the Implementation

### Manual Testing Steps

1. Create a PR that modifies `helm/centreon-openshift/values.yaml`
2. Verify the workflow triggers
3. Check that:
   - Change detection works correctly
   - Build jobs are skipped (only Helm changed)
   - MicroShift starts successfully
   - Helm chart installs without errors
   - Pods become ready within timeout
   - Health checks pass

4. Create another PR that modifies `web/Dockerfile.alma9.openshift`
5. Verify that:
   - Web image build job runs
   - Built image is used in deployment test

---

## Estimated Workflow Duration

| Stage | Estimated Time |
|-------|---------------|
| Change detection | ~30 seconds |
| Image build (if needed) | ~3-5 minutes |
| Disk space cleanup | ~2-3 minutes |
| CRC/MicroShift setup | ~3-5 minutes |
| Helm install | ~1-2 minutes |
| Pod readiness (health checks) | ~5-10 minutes |
| **Total (Helm only)** | **~12-20 minutes** |
| **Total (with image build)** | **~15-25 minutes** |

---

## Future Improvements

1. **Smoke Tests**: Add actual HTTP requests to verify the Centreon web UI loads
2. **Integration Tests**: Run API tests against the deployed stack
3. **Matrix Testing**: Test multiple Centreon versions (24.10, 25.10)
4. **Caching**: Cache CRC/MicroShift setup to speed up subsequent runs
5. **OpenShift Preset**: Switch to full OpenShift for Route testing (requires pull secret)
6. **Parallel Jobs**: Run multiple version tests in parallel

---

## References

- [CRC GitHub Action](https://github.com/crc-org/crc-github-action)
- [MicroShift Documentation](https://github.com/openshift/microshift)
- [Free Disk Space Action](https://github.com/jlumbroso/free-disk-space)
- [GitHub-hosted Runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
