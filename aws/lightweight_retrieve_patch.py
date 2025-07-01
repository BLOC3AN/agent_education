#!/usr/bin/env python3
"""
AWS Free Tier Lightweight Patch for retrieve.py
This script patches the retrieve.py file to disable sentence-transformers dependency
"""

import os
import sys

def patch_retrieve_file():
    """Patch retrieve.py to disable sentence-transformers for AWS Free Tier"""

    retrieve_file_path = "/app/src/tools/retrieve.py"

    if not os.path.exists(retrieve_file_path):
        print(f"❌ File {retrieve_file_path} not found")
        return False

    # Read the original file
    with open(retrieve_file_path, 'r') as f:
        content = f.read()

    # Create the patched content
    patched_content = content.replace(
        "from sentence_transformers import CrossEncoder",
        "# from sentence_transformers import CrossEncoder  # Disabled for AWS Free Tier"
    ).replace(
        "reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')",
        "# reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')  # Disabled for AWS Free Tier\n    return None"
    ).replace(
        "self.use_reranking = True",
        "self.use_reranking = False  # Disabled for AWS Free Tier"
    )

    # Write the patched content
    with open(retrieve_file_path, 'w') as f:
        f.write(patched_content)

    print("✅ Successfully patched retrieve.py for AWS Free Tier")
    return True

if __name__ == "__main__":
    # Check if we're in AWS lightweight mode
    if os.getenv("AWS_LIGHTWEIGHT_MODE") == "true":
        print("🔧 Applying AWS Free Tier patches...")
        if patch_retrieve_file():
            print("✅ All patches applied successfully")
        else:
            print("❌ Failed to apply patches")
            sys.exit(1)
    else:
        print("ℹ️ AWS_LIGHTWEIGHT_MODE not enabled, skipping patches")
