#!/usr/bin/env python3
import math
import re
import subprocess
from collections import Counter
from pathlib import Path


RULES = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "credential-url": re.compile(r"https?://[^\s/:]+:[^\s/@]+@"),
    "literal-secret": re.compile(
        r"(?i)(?:password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"'][^\"'${}{}/\\\s]{8,}[\"']"
    ),
}
TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9+/=_-]{32,}(?![A-Za-z0-9])")
TEXT_SUFFIXES = {
    ".csv", ".ini", ".js", ".json", ".md", ".py", ".sh", ".txt", ".xml", ".yaml", ".yml"
}


def entropy(value):
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def candidate_files(root):
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    for relative in result.stdout.splitlines():
        path = root / relative
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield relative, path


def main():
    root = Path(__file__).resolve().parents[1]
    findings = []
    scanned = 0

    for relative, path in candidate_files(root):
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), 1):
            for rule_name, pattern in RULES.items():
                if pattern.search(line):
                    findings.append((relative, line_number, rule_name))
            if "sha256:" not in line:
                for match in TOKEN_PATTERN.finditer(line):
                    token = match.group(0)
                    if len(set(token)) >= 12 and entropy(token) >= 4.5:
                        findings.append((relative, line_number, "high-entropy-token"))

    if findings:
        for relative, line_number, rule_name in sorted(set(findings)):
            print(f"{relative}:{line_number}: {rule_name}")
        raise SystemExit(1)

    print(f"Secret scan passed for {scanned} tracked and untracked candidate files")


if __name__ == "__main__":
    main()
