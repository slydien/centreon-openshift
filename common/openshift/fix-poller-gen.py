#!/usr/bin/env python3
from pathlib import Path
import re

path = Path("/usr/share/centreon/www/class/centreon-clapi/centreon.Config.Poller.class.php")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()

if "CENTREON_DISABLE_OWNERSHIP_CHANGES" in text:
    raise SystemExit(0)

block = (
    "\n        $disableOwnershipChanges = false;\n"
    "        $envVal = getenv('CENTREON_DISABLE_OWNERSHIP_CHANGES');\n"
    "        if ($envVal !== false) {\n"
    "            $envVal = strtolower(trim((string) $envVal));\n"
    "            $disableOwnershipChanges = in_array($envVal, ['1', 'true', 'yes', 'on'], true);\n"
    "        }\n"
)

pattern = r"(\n\s*)if \(posix_getuid\(\) === 0"

def repl(match: re.Match) -> str:
    indent = match.group(1)
    return indent + block + indent + "if (!$disableOwnershipChanges && posix_getuid() === 0"

text, count = re.subn(pattern, repl, text, count=1)

if count == 0:
    marker = "        $setFilesOwner = 1;\n"
    if marker in text:
        text = text.replace(marker, marker + block.lstrip("\n"), 1)

text = text.replace(
    "if ($setFilesOwner == 0)",
    "if ($setFilesOwner == 0 && !$disableOwnershipChanges)",
)

path.write_text(text)
