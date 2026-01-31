# TODO: Fix OpenShift Arbitrary UID Compatibility Issues

## Overview

The Centreon Docker images fail to run correctly on OpenShift/MicroShift due to incompatibility with arbitrary UIDs. OpenShift assigns random UIDs (e.g., `1000130000`) to containers for security, but the current images expect specific users.

## Issues Identified

### 1. Poller Image - systemctl UID lookup failure

**Error:**
```
Traceback (most recent call last):
  File "/usr/bin/systemctl", line 6789, in <module>
    systemctl = Systemctl()
  File "/usr/bin/systemctl", line 1337, in __init__
    self._user_getlogin = os_getlogin()
  File "/usr/bin/systemctl", line 374, in os_getlogin
    return pwd.getpwuid(os.geteuid()).pw_name
KeyError: 'getpwuid(): uid not found: 1000130000'
Error executing 40-engine.sh
```

**Root Cause:** The Python-based `systemctl` replacement script tries to look up the current user by UID in `/etc/passwd`, but OpenShift's arbitrary UID is not present.

**Suggested Fix:**
- Modify the systemctl script to handle missing UIDs gracefully
- Or add NSS (Name Service Switch) configuration to map arbitrary UIDs
- Or use `nss_wrapper` to provide fake passwd entries

**File to investigate:** `40-engine.sh` startup script

---

### 2. Web Image - `su` command failures

**Error:**
```
su: Authentication failure
```

**Affected commands:**
```bash
su apache -s /bin/bash -c 'php createEngineContextConfiguration.php'
su apache -s /bin/bash -c 'php generationCache.php'
su apache -s /bin/bash -c 'rm -rf /usr/share/centreon/www/install'
```

**Root Cause:** The `su` command requires the target user to exist in `/etc/passwd` and have proper authentication. With arbitrary UIDs, neither the source nor target user may exist.

**Suggested Fix:**
- Replace `su` commands with direct execution (the container already runs as non-root)
- Use `gosu` or `su-exec` which handle this better
- Or run commands directly without user switching since OpenShift handles permissions

---

### 3. Web Image - Database schema not initialized

**Error:**
```
ERROR 1146 (42S02) at line 1: Table 'centreon.command' doesn't exist
ERROR 1146 (42S02) at line 4: Table 'centreon.view_img_dir' doesn't exist
ERROR 1146 (42S02) at line 4: Table 'centreon.auth_ressource' doesn't exist
ERROR 1146 (42S02) at line 1: Table 'centreon.contact' doesn't exist
```

**Root Cause:** The web container tries to insert data before the database schema is created. The initialization order or dependency is incorrect.

**Suggested Fix:**
- Ensure schema creation SQL runs before data insertion
- Add a wait/retry loop to check for table existence
- Or use init containers in Kubernetes to handle DB initialization

---

### 4. Web Image - Missing configuration file

**Error:**
```
sed: can't read /etc/centreon-gorgone/config.d/40-gorgoned.yaml: No such file or directory
```

**Root Cause:** The config file doesn't exist at container startup time.

**Suggested Fix:**
- Create the file during image build
- Or add a check before trying to modify it
- Or generate it dynamically at startup

---

## Priority

| Issue | Severity | Impact |
|-------|----------|--------|
| systemctl UID lookup | High | Poller cannot start |
| su authentication failure | High | Web initialization fails |
| Database schema missing | High | Web cannot function |
| Missing config file | Medium | Startup script fails |

## Related Files

- `poller/Dockerfile.alma9.openshift`
- `web/Dockerfile.alma9.openshift`
- `common/openshift/` (helpers and patches)

## References

- [OpenShift Guidelines for Images](https://docs.openshift.com/container-platform/latest/openshift_images/create-images.html#use-uid_create-images)
- [Arbitrary User IDs in OpenShift](https://cookbook.openshift.org/users-and-role-based-access-control/why-do-my-applications-run-as-a-random-user-id.html)
- [nss_wrapper for UID mapping](https://cwrap.org/nss_wrapper.html)
