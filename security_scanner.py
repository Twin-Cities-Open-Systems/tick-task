#!/usr/bin/env python3
"""
Security Scanner - Test malicious character detection on existing codebase
"""

import json
import os
import re
from pathlib import Path


class SecurityScanner:
    """Security scanner for malicious characters and hidden data"""

    def __init__(self):
        # Malicious character patterns
        self.zero_width_chars = re.compile(
            r"[\u200B-\u200D\uFEFF]"
        )  # Zero-width characters
        # Dangerous control characters (excluding normal formatting like \n, \t, \r)
        self.dangerous_control_chars = re.compile(
            r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]"
        )
        self.rtl_override = "\u202e"  # Right-to-left override
        self.invisible_chars = re.compile(
            r"[\u200E-\u200F\u202A-\u202E\u2060-\u206F]"
        )  # Invisible characters

        # Homoglyph detection (simplified - characters that look like ASCII)
        self.homoglyph_map = {
            "а": "a",
            "е": "e",
            "о": "o",
            "р": "p",
            "с": "c",
            "у": "y",
            "х": "x",
            "А": "A",
            "Е": "E",
            "О": "O",
            "Р": "P",
            "С": "C",
            "У": "Y",
            "Х": "X",
        }

    def detect_zero_width_chars(self, text):
        """Detect zero-width characters"""
        return bool(self.zero_width_chars.search(text))

    def detect_dangerous_control_chars(self, text):
        """Detect dangerous control characters"""
        return bool(self.dangerous_control_chars.search(text))

    def detect_rtl_override(self, text):
        """Detect right-to-left override"""
        return self.rtl_override in text

    def detect_invisible_chars(self, text):
        """Detect invisible characters"""
        return bool(self.invisible_chars.search(text))

    def detect_homoglyphs(self, text):
        """Detect potential homoglyph attacks"""
        for char in text:
            if char in self.homoglyph_map:
                return True
        return False

    def scan_text(self, text, filename="unknown"):
        """Scan text for security issues"""
        issues = []

        if self.detect_zero_width_chars(text):
            issues.append("Zero-width characters detected")
        if self.detect_dangerous_control_chars(text):
            issues.append("Dangerous control characters detected")
        if self.detect_rtl_override(text):
            issues.append("Right-to-left override character detected")
        if self.detect_invisible_chars(text):
            issues.append("Invisible characters detected")
        if self.detect_homoglyphs(text):
            issues.append("Potential homoglyph characters detected")

        return {
            "file": filename,
            "issues": issues,
            "safe": len(issues) == 0,
            "char_count": len(text),
            "line_count": len(text.split("\n")),
        }

    def scan_file(self, filepath):
        """Scan a single file for security issues"""
        try:
            # Try UTF-8 first
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try with error handling
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                return {
                    "file": filepath,
                    "issues": [f"Error reading file: {e}"],
                    "safe": False,
                    "char_count": 0,
                    "line_count": 0,
                }

        result = self.scan_text(content, filepath)
        return result

    def scan_directory(self, directory, extensions=None, exclude_dirs=None):
        """Scan directory for security issues"""
        if extensions is None:
            extensions = [
                ".py",
                ".md",
                ".txt",
                ".json",
                ".yml",
                ".yaml",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
            ]

        if exclude_dirs is None:
            exclude_dirs = [
                ".git",
                "__pycache__",
                "node_modules",
                ".next",
                "build",
                "dist",
            ]

        results = []

        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    result = self.scan_file(filepath)
                    if not result["safe"]:
                        results.append(result)

        return results


def main():
    """Main scanner function"""
    scanner = SecurityScanner()

    print("🔍 Security Scanner - Scanning FIN-tasks codebase")
    print("=" * 60)

    # Scan the FIN-tasks directory
    results = scanner.scan_directory("FIN-tasks")

    if not results:
        print("✅ No security issues found in codebase!")
        print("🎉 Safe to proceed with security validation implementation.")
        return

    print(f"⚠️  Found {len(results)} files with potential security issues:")
    print()

    for result in results:
        print(f"📁 {result['file']}")
        print(f"   Lines: {result['line_count']}, Characters: {result['char_count']}")
        for issue in result["issues"]:
            print(f"   🚨 {issue}")
        print()

    print("=" * 60)
    print("📋 Analysis Required:")
    print("- Review each flagged file manually")
    print("- Determine if issues are legitimate security concerns")
    print("- Consider false positives (legitimate Unicode usage)")
    print("- Refine detection rules if needed")
    print()
    print("❓ Proceed with security implementation?")


if __name__ == "__main__":
    main()
