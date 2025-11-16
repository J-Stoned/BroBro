# 📚 Universal Content Embedding System

## Overview

This system allows you to embed **any type of business knowledge** (documents, transcripts, PDFs, text files) into your GHL WHIZ knowledge base. All content is added to the existing `ghl-youtube` collection and is immediately searchable using the hybrid BM25 + semantic search engine.

---

## ✅ What's Been Built

### Core Scripts

**1. `embed_document.py`** - Universal document embedder
- Supports: `.txt`, `.md`, `.pdf`, `.docx`, and plain text
- Auto-detects file format
- Intelligent chunking (1000 chars, 200 overlap)
- Same embedding model as YouTube pipeline (`all-MiniLM-L6-v2`)
- Adds to existing `ghl-youtube` collection
- Metadata tracking (source, type, date added)

**2. `embed_batch.py`** - Batch embedder for multiple files
- Process multiple documents at once
- Reads from JSON config file
- Progress tracking and error handling
- Success/failure reporting

### Directory Structure

```
content/
├── batch_config.json          ← Batch embedding configuration
├── test/                      ← Test documents
│   └── test_pricing.txt       ← Example pricing guide
├── sales/                     ← Sales scripts and frameworks
├── marketing/                 ← Marketing playbooks
├── case_studies/              ← Success stories
├── pricing/                   ← Pricing strategies
├── positioning/               ← Positioning frameworks
└── training/                  ← Training materials
```

---

## 🚀 Quick Start

### Prerequisites

Make sure ChromaDB server is running:
```bash
npm run start-chroma
```

### Single Document Embedding

**Embed a text file:**
```bash
python embed_document.py \
  --file "content/sales/discovery_call.txt" \
  --title "Discovery Call Framework" \
  --type "script"
```

**Embed a PDF:**
```bash
python embed_document.py \
  --file "content/case_studies/success_story.pdf" \
  --title "Real Estate Agency Case Study" \
  --type "case_study"
```

**Embed a markdown document:**
```bash
python embed_document.py \
  --file "content/pricing/agency_pricing.md" \
  --title "Agency Pricing Models" \
  --type "framework"
```

### Batch Embedding

**1. Create a batch config file (`content/batch_config.json`):**
```json
{
    "documents": [
        {
            "file": "content/sales/discovery_call.txt",
            "title": "Discovery Call Framework",
            "type": "script"
        },
        {
            "file": "content/case_studies/real_estate.pdf",
            "title": "Real Estate Agency Case Study",
            "type": "case_study"
        },
        {
            "file": "content/pricing/pricing_guide.md",
            "title": "Agency Pricing Guide",
            "type": "framework"
        }
    ]
}
```

**2. Run batch embedding:**
```bash
python embed_batch.py --config content/batch_config.json
```

---

## 📊 Command-Line Options

### `embed_document.py`

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--file` | ✅ | - | Path to document file |
| `--title` | ✅ | - | Descriptive title for the content |
| `--type` | ❌ | `business` | Content type (see below) |
| `--collection` | ❌ | `ghl-youtube` | ChromaDB collection name |
| `--chunk-size` | ❌ | `1000` | Characters per chunk |
| `--overlap` | ❌ | `200` | Character overlap between chunks |

### Content Types

Use these for the `--type` parameter:

- `business` - General business content
- `script` - Sales scripts, call frameworks
- `training` - Training materials, courses
- `case_study` - Success stories, case studies
- `playbook` - Marketing playbooks, strategies
- `framework` - Business frameworks, models
- `pricing` - Pricing strategies, models
- `positioning` - Positioning frameworks

---

## 🧪 Testing the System

### Test Document

A test pricing guide has been created at `content/test/test_pricing.txt`

**Embed it:**
```bash
python embed_document.py \
  --file "content/test/test_pricing.txt" \
  --title "GHL Agency Pricing Strategies Guide" \
  --type "pricing"
```

**Verify in search:**
```bash
python search_api.py "agency pricing strategies" -n 5
```

You should see the test document in the search results!

**Check collection count:**
```bash
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('ghl-youtube')
print(f'Total documents: {collection.count()}')
"
```

---

## 📁 Supported File Formats

### ✅ Natively Supported

- **Text files** (`.txt`) - Plain text documents
- **Markdown** (`.md`) - Markdown formatted documents

### 📦 Requires Installation

**PDF Support:**
```bash
pip install PyPDF2
```

**Word Document Support:**
```bash
pip install python-docx
```

---

## 💡 Content Organization Guidelines

### What to Add

**✅ High-Value Content:**
- Sales scripts and frameworks
- Objection handling guides
- Case studies with real numbers
- Pricing strategies and models
- Marketing playbooks
- Training materials
- Business frameworks
- Positioning guides

**❌ Avoid:**
- Generic theory without action steps
- Outdated information
- Duplicate content already in KB
- Content not relevant to GHL users
- Copyrighted material without permission

### Content Organization Best Practices

**By Function:**
```
content/
├── sales/           ← All sales-related content
├── marketing/       ← Marketing strategies
├── operations/      ← Business operations
└── training/        ← Training materials
```

**By Priority:**
```
content/
├── priority1/       ← Must-have content
├── priority2/       ← High-impact content
└── reference/       ← Reference materials
```

**By Client Type:**
```
content/
├── agencies/        ← Agency-focused content
├── consultants/     ← Consultant resources
└── freelancers/     ← Freelancer guides
```

---

## 🔍 How It Works

### Embedding Pipeline

1. **File Reading** - Auto-detects format and reads content
2. **Text Cleaning** - Normalizes whitespace and formatting
3. **Chunking** - Splits into 1000-char chunks with 200-char overlap
4. **Embedding** - Uses `all-MiniLM-L6-v2` model (same as YouTube)
5. **Storage** - Adds to `ghl-youtube` collection in ChromaDB
6. **Metadata** - Tracks source, type, chunks, date, etc.

### Metadata Structure

Each embedded chunk includes:
```python
{
    "source": "business_content",
    "title": "Document Title",
    "type": "script",
    "chunk_index": 0,
    "total_chunks": 4,
    "file_path": "content/sales/script.txt",
    "date_added": "2025-11-01T12:00:00",
    "content_format": "document",
    "video_id": "doc_document_title"
}
```

---

## 🎯 Priority Content to Add

### Phase 1: Sales & Closing (Immediate Value)
- [ ] Discovery call scripts
- [ ] Objection handling guides
- [ ] Closing techniques
- [ ] Follow-up sequences
- [ ] Proposal templates

### Phase 2: Pricing & Positioning (High Impact)
- [ ] Value-based pricing models
- [ ] Package structuring guides
- [ ] Retainer frameworks
- [ ] ROI calculation tools
- [ ] Pricing psychology

### Phase 3: Marketing & Lead Gen (Scale)
- [ ] Funnel building playbooks
- [ ] Ad creation frameworks
- [ ] Content marketing strategies
- [ ] Email/SMS sequences
- [ ] Social media approaches

### Phase 4: Agency Building (Long-term)
- [ ] Team structure guides
- [ ] Hiring and training SOPs
- [ ] Client onboarding processes
- [ ] Project management workflows
- [ ] Scaling strategies

### Phase 5: Case Studies (Proof)
- [ ] Real estate automation success
- [ ] E-commerce scaling stories
- [ ] Service business transformations
- [ ] B2B lead generation wins
- [ ] Local business automation

---

## 🐛 Troubleshooting

### ChromaDB Not Running

**Error:** `Could not connect to a Chroma server`

**Solution:**
```bash
npm run start-chroma
```

### PDF Import Issues

**Error:** `PyPDF2 not installed`

**Solution:**
```bash
pip install PyPDF2
```

### Word Document Issues

**Error:** `python-docx not installed`

**Solution:**
```bash
pip install python-docx
```

### Encoding Issues

If you see encoding errors, ensure your files are UTF-8 encoded.

### Docker Not Running

If ChromaDB won't start, make sure Docker Desktop is running:
```bash
# Windows
cmd.exe /c "start """" ""C:\Program Files\Docker\Docker\Docker Desktop.exe"""

# Wait 30 seconds, then:
npm run start-chroma
```

---

## 📈 Success Metrics

Track these to measure system effectiveness:

- **Total documents** in `ghl-youtube` collection
- **Search queries** hitting business content
- **Relevance scores** for business queries
- **User feedback** on content quality
- **Content gaps** identified from queries

---

## 🔄 Maintenance

### Weekly
- Add 3-5 new business documents
- Focus on most-requested topics
- Verify search quality

### Monthly
- Review content gaps from user queries
- Update/refresh outdated content
- Expand high-performing topics

### Quarterly
- Audit entire content library
- Remove or update stale content
- Analyze search patterns

---

## 🎓 Examples

### Example 1: Sales Script

**File:** `content/sales/discovery_call.txt`
```bash
python embed_document.py \
  --file "content/sales/discovery_call.txt" \
  --title "Discovery Call Framework - Complete Script" \
  --type "script"
```

### Example 2: Case Study

**File:** `content/case_studies/real_estate_success.pdf`
```bash
python embed_document.py \
  --file "content/case_studies/real_estate_success.pdf" \
  --title "Real Estate Agency Case Study - 10x Growth" \
  --type "case_study"
```

### Example 3: Pricing Guide

**File:** `content/pricing/agency_pricing.md`
```bash
python embed_document.py \
  --file "content/pricing/agency_pricing.md" \
  --title "Agency Pricing Models and Strategies" \
  --type "framework"
```

### Example 4: Batch Embedding

**Config:** `content/batch_config.json`
```json
{
    "documents": [
        {
            "file": "content/sales/discovery_call.txt",
            "title": "Discovery Call Framework",
            "type": "script"
        },
        {
            "file": "content/sales/objection_handling.txt",
            "title": "Objection Handling Guide",
            "type": "training"
        },
        {
            "file": "content/case_studies/success_story.pdf",
            "title": "Real Estate Success Story",
            "type": "case_study"
        }
    ]
}
```

**Run:**
```bash
python embed_batch.py --config content/batch_config.json
```

---

## 🚀 Next Steps

1. **Start Docker Desktop** if not running
2. **Start ChromaDB**: `npm run start-chroma`
3. **Test the system** with the test document
4. **Add your first real content** (sales script, case study, etc.)
5. **Verify search** finds your content
6. **Scale up** by adding more documents

---

## 📞 Support

If you encounter issues:

1. Check this README first
2. Verify ChromaDB is running
3. Check Docker Desktop is running
4. Review error messages
5. Test with the example test document first

---

## 🎉 System Features

- ✅ Auto-detects file format
- ✅ Handles txt, md, pdf, docx
- ✅ Intelligent chunking strategy
- ✅ Same embedding model as YouTube pipeline
- ✅ Metadata tracking
- ✅ Batch processing support
- ✅ Progress indicators
- ✅ Error handling
- ✅ Immediately searchable
- ✅ No code changes needed for search

**Build your knowledge base to 500+ documents and beyond!** 🚀
