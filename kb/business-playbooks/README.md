# Business Playbooks Knowledge Base

This directory contains business and marketing playbooks that are embedded into the BroBro knowledge base.

## Current Collection

### Alex Hormozi Series

All playbooks by Alex Hormozi focused on lead generation, offers, and business growth:

1. **100M Playbook: Lead Nurture**
   - Category: Lead Generation
   - Focus: How to get more leads to respond, schedule, and show
   - Key Topics: Lead nurture, follow-up systems, conversion optimization

2. **100M Leads**
   - Category: Lead Generation  
   - Focus: How to get strangers to want to buy your stuff
   - Key Topics: Lead acquisition, traffic generation, advertising strategies

3. **100M Offers**
   - Category: Offers
   - Focus: How to make offers so good people feel stupid saying no
   - Key Topics: Offer creation, value stacking, pricing strategies

4. **100M Money Models**
   - Category: Business Models
   - Focus: How to make money with different business models
   - Key Topics: Revenue models, monetization strategies, business frameworks

5. **100M Ads**
   - Category: Advertising
   - Focus: Advertising strategies and frameworks
   - Key Topics: Ad creation, copywriting, conversion optimization

## Embedding Status

✅ All 5 playbooks copied to knowledge base
⏳ Ready to embed into ChromaDB

## How to Embed These Playbooks

### Option 1: Batch Embed All (Recommended)

Run the batch script to embed all playbooks at once:

```bash
cd "C:\Users\justi\BroBro"
scripts\embed-hormozi-playbooks.bat
```

### Option 2: Embed Individual Playbooks

Embed one playbook at a time:

```bash
python scripts\embed-business-book.py "kb\business-playbooks\100M-Playbook-Lead-Nurture.pdf" --title "100M Playbook: Lead Nurture" --author "Alex Hormozi" --category "lead-generation"
```

## How the AI Will Use These

Once embedded, the BroBro AI assistant will be able to:

- **Answer questions** about lead generation strategies from Hormozi's frameworks
- **Suggest offers** based on the 100M Offers principles
- **Recommend workflows** that align with proven nurture sequences
- **Provide business model advice** from Money Models
- **Create ad copy** using 100M Ads principles

## Integration with GHL

These playbooks complement your GHL automation by:

1. **Strategic Context** - AI understands WHY certain automations work
2. **Best Practices** - Recommendations based on proven frameworks
3. **Offer Creation** - Help building irresistible offers inside GHL
4. **Lead Nurture** - Designing follow-up sequences that convert
5. **Workflow Design** - Aligning GHL workflows with business fundamentals

## Collection Details

- **Storage Location**: `C:\Users\justi\BroBro\kb\business-playbooks\`
- **ChromaDB Collection**: `ghl-business`
- **Embedding Model**: `all-MiniLM-L6-v2`
- **Chunk Size**: Intelligent chunking with chapter detection
- **Metadata**: Includes page numbers, chapters, and categories

## Next Steps

After embedding:

1. Test the knowledge base by asking questions like:
   - "What does Alex Hormozi say about lead nurture?"
   - "How should I structure my offer according to 100M Offers?"
   - "What are the best practices for follow-up sequences?"

2. Check the ChromaDB collection:
   ```bash
   python query-kb.js "lead nurture strategies"
   ```

3. Use in workflows:
   - The AI will automatically reference these when helping you build GHL systems
   - Suggestions will be backed by proven frameworks

## Adding More Playbooks

To add additional business books or playbooks:

1. Download/save the PDF to this directory
2. Run the embed script:
   ```bash
   python scripts\embed-business-book.py "kb\business-playbooks\[filename].pdf" --title "Book Title" --author "Author" --category "category"
   ```

Categories to use:
- `lead-generation` - Lead gen and acquisition
- `offers` - Offer creation and pricing
- `business-models` - Business frameworks
- `advertising` - Ad creation and copywriting
- `automation` - Automation strategies
- `sales` - Sales processes and scripts
- `best-practices` - General business wisdom

---

**Last Updated**: 2025-11-01
**Status**: Ready for embedding ✅
