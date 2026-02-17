"""Utilities for generating filesystem-safe names from session names."""

import re
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


def sanitize_name_for_filesystem(name: str, max_length: int = 50) -> str:
    """
    Convert a session name into a filesystem-safe directory name.

    Examples:
        "Research & Development" -> "research-and-development"
        "My Project: v1.0" -> "my-project-v10"
        "Testing / Debug" -> "testing-debug"
        "Session 1" -> "session-1"

    Note: This function only sanitizes the name part.
    Date prefixes are added by generate_unique_directory_name().

    Args:
        name: The session name to sanitize
        max_length: Maximum length for the directory name (default: 50)

    Returns:
        A filesystem-safe directory name
    """
    # Convert to lowercase
    safe_name = name.lower().strip()

    # Replace common separators and special characters with hyphens
    safe_name = re.sub(r'[&/\\:;,\s]+', '-', safe_name)

    # Remove any remaining non-alphanumeric characters except hyphens
    safe_name = re.sub(r'[^a-z0-9\-]', '', safe_name)

    # Remove multiple consecutive hyphens
    safe_name = re.sub(r'-+', '-', safe_name)

    # Remove leading/trailing hyphens
    safe_name = safe_name.strip('-')

    # Ensure it's not empty
    if not safe_name:
        safe_name = "session"

    # Truncate to max length
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length].rstrip('-')

    return safe_name


def generate_unique_directory_name(
    base_name: str,
    parent_dir: str,
    session_id: str,
    max_length: int = 50,
    include_date: bool = True
) -> str:
    """
    Generate a unique directory name based on session name with optional date prefix.

    Creates names like:
        "2026-02-05-my-project"
        "2026-02-05-research"
        "2026-02-05-web-development"

    If include_date is False, creates names without date:
        "my-project"
        "my-project-2"
        "my-project-3"

    If the base name is too generic (like "session-1"), appends part of the UUID
    to make it more distinctive:
        "2026-02-05-session-1-a7b3"
        "session-1-a7b3" (without date)

    Args:
        base_name: The session name to use as base
        parent_dir: Parent directory path where sessions are stored
        session_id: UUID of the session (used for uniqueness)
        max_length: Maximum length for the directory name (default: 50)
        include_date: Whether to include date prefix (default: True)

    Returns:
        A unique, filesystem-safe directory name with date prefix
    """
    # Get current date in YYYY-MM-DD format
    date_prefix = datetime.now().strftime('%Y-%m-%d') if include_date else None

    # Calculate remaining space for name after date prefix
    # Date format: "2026-02-05-" = 11 characters
    available_length = max_length - 11 if include_date else max_length

    # Sanitize the base name with adjusted length
    safe_base = sanitize_name_for_filesystem(base_name, available_length - 10)

    # Check if this is a generic name (like "session-1", "session-2", etc.)
    is_generic = re.match(r'^session-?\d*$', safe_base, re.IGNORECASE)

    # If generic, append a short UUID suffix for better identification
    if is_generic:
        # Use first 4 chars of session_id for uniqueness
        uuid_suffix = session_id.split('-')[0][:4]
        safe_base = f"{safe_base}-{uuid_suffix}"

    # Add date prefix if requested
    if include_date:
        base_with_date = f"{date_prefix}-{safe_base}"
    else:
        base_with_date = safe_base

    # Check if directory already exists
    test_name = base_with_date
    counter = 2

    while True:
        test_path = os.path.join(parent_dir, test_name)
        if not os.path.exists(test_path):
            return test_name

        # Directory exists, try with counter
        # Keep it short: "2026-02-05-my-project-2" not "2026-02-05-my-project-counter-2"
        test_name = f"{base_with_date}-{counter}"
        counter += 1

        # Safety check: don't loop forever
        if counter > 1000:
            # Fall back to UUID-based naming
            if include_date:
                return f"{date_prefix}-{safe_base}-{session_id[:8]}"
            else:
                return f"{safe_base}-{session_id[:8]}"


def extract_session_name_from_directory(dir_name: str) -> str:
    """
    Convert a directory name back to a human-readable session name.

    Examples:
        "2026-02-05-research-and-development" -> "Research and Development"
        "2026-02-05-my-project-v10" -> "My Project v10"
        "2026-02-05-session-1-a7b3" -> "Session 1"
        "research-and-development" -> "Research and Development" (legacy)

    Args:
        dir_name: The directory name

    Returns:
        A human-readable session name
    """
    # Remove date prefix if present (YYYY-MM-DD-)
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', dir_name)

    # Replace hyphens with spaces
    name = name.replace('-', ' ')

    # Remove UUID suffixes (4 hex chars at end)
    name = re.sub(r'\s+[a-f0-9]{4}$', '', name)

    # Remove counter suffixes (like " 2", " 3")
    name = re.sub(r'\s+\d+$', '', name)

    # Title case each word
    name = ' '.join(word.capitalize() for word in name.split())

    return name


# Example usage and tests
if __name__ == "__main__":
    test_cases = [
        "Research & Development",
        "My Project: v1.0",
        "Testing / Debug",
        "Session 1",
        "Data Analysis (Python)",
        "Web App - Frontend",
        "Machine Learning Model",
        "Quick Test!!!",
        "   Spaces   Everywhere   ",
    ]

    print("Directory Name Generation Tests:")
    print("=" * 60)

    for test_name in test_cases:
        safe_name = sanitize_name_for_filesystem(test_name)
        print(f"{test_name:30} -> {safe_name}")

    print("\n" + "=" * 60)
    print("Uniqueness Test:")
    print("=" * 60)

    # Simulate creating multiple sessions with same name
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(3):
            session_id = f"abc-{i:03d}"
            unique_name = generate_unique_directory_name(
                "My Project",
                tmpdir,
                session_id
            )
            # Create the directory
            os.makedirs(os.path.join(tmpdir, unique_name))
            print(f"Session {i+1}: {unique_name}")
