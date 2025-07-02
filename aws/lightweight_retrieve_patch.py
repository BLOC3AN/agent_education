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

def patch_qdrant_file():
    """Patch qdrant_vectordb.py to use lightweight embeddings for AWS Free Tier"""

    qdrant_file_path = "/app/src/RAG/qdrant_vectordb.py"

    if not os.path.exists(qdrant_file_path):
        print(f"❌ File {qdrant_file_path} not found")
        return False

    # Read the original file
    with open(qdrant_file_path, 'r') as f:
        content = f.read()

    # Add import for lightweight embeddings at the top
    if "from lightweight_embeddings import get_lightweight_embeddings" not in content:
        # Find the import section and add our import
        import_section = content.find("import uuid")
        if import_section != -1:
            # Insert after the uuid import
            insert_pos = content.find("\n", import_section) + 1
            new_import = "from lightweight_embeddings import get_lightweight_embeddings\n"
            content = content[:insert_pos] + new_import + content[insert_pos:]

    # Replace fastembed Document usage with lightweight embeddings
    patched_content = content.replace(
        'dense_documents = [\n                models.Document(text=doc, model="BAAI/bge-small-en")\n                for doc in documents\n            ]',
        '# Using lightweight TF-IDF embeddings for AWS Free Tier\n            embedder = get_lightweight_embeddings()\n            dense_documents = embedder.embed_documents(documents)'
    ).replace(
        'dense_query = models.Document(text=query_text, model=self.model_emmbedding)',
        '# Using lightweight TF-IDF embeddings for AWS Free Tier\n            embedder = get_lightweight_embeddings()\n            dense_query = embedder.embed_query(query_text)'
    ).replace(
        'vector={\n                        self.vector_name : dense_documents[i],\n                    },',
        'vector={\n                        self.vector_name : dense_documents[i].tolist(),\n                    },'
    ).replace(
        'query=dense_query,',
        'query=dense_query.tolist(),'
    )

    # Write the patched content
    with open(qdrant_file_path, 'w') as f:
        f.write(patched_content)

    print("✅ Successfully patched qdrant_vectordb.py to use lightweight embeddings")
    return True

if __name__ == "__main__":
    # Check if we're in AWS lightweight mode
    if os.getenv("AWS_LIGHTWEIGHT_MODE") == "true":
        print("🔧 Applying AWS Free Tier patches...")

        success = True

        # Patch retrieve.py
        if not patch_retrieve_file():
            success = False

        # Patch qdrant_vectordb.py
        if not patch_qdrant_file():
            success = False

        if success:
            print("✅ All patches applied successfully")
        else:
            print("❌ Failed to apply some patches")
            sys.exit(1)
    else:
        print("ℹ️ AWS_LIGHTWEIGHT_MODE not enabled, skipping patches")
