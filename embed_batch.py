#!/usr/bin/env python3
"""
Batch embed multiple documents at once.

Reads a JSON config file with document list.
"""

import json
import argparse
from pathlib import Path
from embed_document import embed_document

def embed_batch(config_file):
    """
    Embed multiple documents from a config file.

    Config format:
    {
        "documents": [
            {
                "file": "path/to/file.txt",
                "title": "Document Title",
                "type": "business"
            },
            ...
        ]
    }
    """

    print(f"\n📋 Reading batch config: {config_file}")

    with open(config_file, 'r') as f:
        config = json.load(f)

    documents = config.get('documents', [])
    print(f"📚 Found {len(documents)} documents to embed\n")

    success_count = 0
    fail_count = 0

    for i, doc in enumerate(documents, 1):
        print(f"\n{'='*60}")
        print(f"Document {i}/{len(documents)}")
        print(f"{'='*60}")

        file_path = doc['file']
        title = doc['title']
        content_type = doc.get('type', 'business')

        if not Path(file_path).exists():
            print(f"⚠️  Skipping - file not found: {file_path}")
            fail_count += 1
            continue

        success = embed_document(
            file_path=file_path,
            title=title,
            content_type=content_type
        )

        if success:
            success_count += 1
        else:
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {len(documents)}")

    return success_count, fail_count

def main():
    parser = argparse.ArgumentParser(
        description="Batch embed multiple documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example config file (batch_config.json):
{
    "documents": [
        {
            "file": "sales/discovery_call.txt",
            "title": "Discovery Call Framework",
            "type": "script"
        },
        {
            "file": "case_studies/real_estate.pdf",
            "title": "Real Estate Agency Case Study",
            "type": "case_study"
        },
        {
            "file": "training/pricing.docx",
            "title": "Agency Pricing Guide",
            "type": "training"
        }
    ]
}

Usage:
  python embed_batch.py --config batch_config.json
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to batch config JSON file'
    )

    args = parser.parse_args()

    if not Path(args.config).exists():
        print(f"❌ Config file not found: {args.config}")
        return 1

    success, failed = embed_batch(args.config)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
