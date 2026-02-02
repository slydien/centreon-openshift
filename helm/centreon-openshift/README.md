# Centreon OpenShift Helm Chart

This chart deploys Centreon web, database, and optional poller components on OpenShift.

## Installing the chart

```bash
helm install centreon-openshift . -n centreon
```

## Upgrading the chart

```bash
helm upgrade --install centreon-openshift . -n centreon
```

## Configuration

The following table lists the configurable parameters of the chart and their default values.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| global.imagePullPolicy | string | `Always` | Global image pull policy for all images |
| global.imagePullSecrets | list | `[]` | List of imagePullSecrets names to use for pulling images |
| global.podSecurityContext | object | `{}` | Pod-level security context (OpenShift assigns a UID, so keep this empty) |
| global.securityContext.runAsNonRoot | bool | `true` |  |
| global.securityContext.allowPrivilegeEscalation | bool | `false` |  |
| global.securityContext.capabilities.drop[0] | string | `ALL` |  |
| global.securityContext.seccompProfile.type | string | `RuntimeDefault` |  |
| rbac.endpointSlice.enabled | bool | `true` | Create RBAC allowing the service account to read EndpointSlices |
| rbac.endpointSlice.serviceAccountName | string | `default` | Service account name used for EndpointSlice RBAC |
| routes.web.enabled | bool | `true` | Create an OpenShift Route for the web service |
| routes.web.host | string | `""` | Route host (leave empty to let OpenShift assign) |
| routes.web.tls.termination | string | `edge` | TLS termination type (edge, passthrough, reencrypt) |
| routes.web.tls.insecureEdgeTerminationPolicy | string | `Redirect` | Insecure edge termination policy (None, Allow, Redirect) |
| services.web.enabled | bool | `true` | Deploy the web service |
| services.web.replicas | int | `1` | Number of replicas for the web Deployment |
| services.web.image | string | `slydien/centreon-web-alma9:24.10-openshift` | Image for the web service |
| services.web.ports[0].name | string | `http` | Service port name for HTTP |
| services.web.ports[0].port | int | `80` | Service port |
| services.web.ports[0].targetPort | int | `8080` | Container target port |
| services.web.ports[1].name | string | `gorgone` | Service port name for gorgone |
| services.web.ports[1].port | int | `8085` |  |
| services.web.ports[1].targetPort | int | `8085` |  |
| services.web.env.CENTREON_DISABLE_OWNERSHIP_CHANGES | int | `1` | Disable ownership changes in the container |
| services.web.env.MYSQL_ROOT_PASSWORD | string | `centreon` | MySQL root password |
| services.web.env.MYSQL_USER | string | `centreon` | MySQL user |
| services.web.env.MYSQL_PASSWORD | string | `centreon` | MySQL password |
| services.web.env.MYSQL_EXTRA_FLAGS | string | `"--secure-file-priv="` | Extra MySQL flags |
| services.web.env.MARIADB_ROOT_PASSWORD | string | `centreon` | MariaDB root password |
| services.web.env.MARIADB_USER | string | `centreon` | MariaDB user |
| services.web.env.MARIADB_PASSWORD | string | `centreon` | MariaDB password |
| services.web.env.MARIADB_EXTRA_FLAGS | string | `"--secure-file-priv="` | Extra MariaDB flags |
| services.web.env.MYSQL_HOST | string | `db` | MySQL host name |
| services.web.env.LDAP_HOST | string | `""` | LDAP host name |
| services.web.env.OPENID_HOST | string | `""` | OpenID host name |
| services.web.env.SAML_HOST | string | `""` | SAML host name |
| services.web.env.VAULT_HOST | string | `""` | Vault host name |
| services.web.env.VAULT_ROLE_ID | string | `""` | Vault role ID |
| services.web.env.VAULT_SECRET_ID | string | `""` | Vault secret ID |
| services.web.env.CENTREON_DATASET | string | `"1"` | Centreon dataset selection |
| services.web.env.CENTREON_LANG | string | `en_US` | Centreon language |
| services.web.probes.startup.httpGet.path | string | `/centreon/api/latest/platform/versions` |  |
| services.web.probes.startup.httpGet.port | int | `8080` |  |
| services.web.probes.startup.initialDelaySeconds | int | `15` | Startup probe initial delay in seconds |
| services.web.probes.startup.periodSeconds | int | `10` | Startup probe period in seconds |
| services.web.probes.startup.timeoutSeconds | int | `3` | Startup probe timeout in seconds |
| services.web.probes.startup.failureThreshold | int | `60` | Startup probe failure threshold |
| services.web.probes.readiness.httpGet.path | string | `/centreon/api/latest/platform/versions` |  |
| services.web.probes.readiness.httpGet.port | int | `8080` |  |
| services.web.probes.readiness.initialDelaySeconds | int | `15` | Readiness probe initial delay in seconds |
| services.web.probes.readiness.periodSeconds | int | `5` | Readiness probe period in seconds |
| services.web.probes.readiness.timeoutSeconds | int | `3` | Readiness probe timeout in seconds |
| services.web.probes.readiness.failureThreshold | int | `12` | Readiness probe failure threshold |
| services.web.probes.liveness.httpGet.path | string | `/centreon/api/latest/platform/versions` |  |
| services.web.probes.liveness.httpGet.port | int | `8080` |  |
| services.web.probes.liveness.initialDelaySeconds | int | `60` | Liveness probe initial delay in seconds |
| services.web.probes.liveness.periodSeconds | int | `10` | Liveness probe period in seconds |
| services.web.probes.liveness.timeoutSeconds | int | `3` | Liveness probe timeout in seconds |
| services.web.resources.requests.cpu | string | `10m` |  |
| services.web.resources.requests.memory | string | `64Mi` |  |
| services.web.resources.limits.cpu | string | `"1"` |  |
| services.web.resources.limits.memory | string | `1000Mi` |  |
| services.db.enabled | bool | `true` | Deploy the database service |
| services.db.replicas | int | `1` | Number of replicas for the database Deployment |
| services.db.image | string | `bitnamilegacy/mariadb:10.11` | Image for the database service |
| services.db.ports[0].name | string | `mysql` | Service port name for MySQL |
| services.db.ports[0].port | int | `3306` | Service port |
| services.db.ports[0].targetPort | int | `3306` | Container target port |
| services.db.env.MARIADB_ROOT_PASSWORD | string | `centreon` | MariaDB root password |
| services.db.env.MARIADB_ROOT_HOST | string | `"%"` | MariaDB root host |
| services.db.env.MARIADB_DATABASE | string | `centreon` | MariaDB database name |
| services.db.env.MARIADB_USER | string | `centreon` | MariaDB user |
| services.db.env.MARIADB_PASSWORD | string | `centreon` | MariaDB password |
| services.db.env.MARIADB_EXTRA_FLAGS | string | `"--secure-file-priv="` | Extra MariaDB flags |
| services.db.resources.requests.cpu | string | `10m` |  |
| services.db.resources.requests.memory | string | `64Mi` |  |
| services.db.resources.limits.cpu | string | `"1"` |  |
| services.db.resources.limits.memory | string | `1000Mi` |  |
| services.poller.enabled | bool | `true` | Deploy the poller service |
| services.poller.replicas | int | `1` | Number of replicas for the poller Deployment |
| services.poller.image | string | `ghcr.io/slydien/centreon-poller-alma9:24.10-openshift` | Image for the poller service |
| services.poller.headless | bool | `false` | Use per-pod IP for registration; service does not need to be headless |
| services.poller.ports[0].name | string | `gorgone-core` |  |
| services.poller.ports[0].port | int | `5556` |  |
| services.poller.ports[0].targetPort | int | `5556` |  |
| services.poller.env.WEB_HOST | string | `""` | Hostname of the web service for the poller (use service FQDN for cross-namespace compatibility) |
| services.poller.env.WEB_GORGONE_PORT | string | `"8085"` | Gorgone API port on the web service |
| services.poller.env.WEB_API_USERNAME | string | `admin` | API username for poller registration |
| services.poller.env.WEB_API_PASSWORD | string | `"Centreon!2021"` | API password for poller registration |
| services.poller.initWait.enabled | bool | `true` | Wait for web + db before starting poller |
| services.poller.initWait.image | string | `"alpine:3.19"` | Init container image used to wait for dependencies |
| services.poller.initWait.webUrl | string | `""` | Web health URL to wait on |
| services.poller.initWait.dbHost | string | `"db"` | DB host to wait on |
| services.poller.initWait.dbPort | int | `3306` | DB port to wait on |
| services.poller.initWait.timeoutSeconds | int | `300` | Max wait time in seconds |
| services.poller.resources.requests.cpu | string | `10m` |  |
| services.poller.resources.requests.memory | string | `64Mi` |  |
| services.poller.resources.limits.cpu | string | `"1"` |  |
| services.poller.resources.limits.memory | string | `1000Mi` |  |
