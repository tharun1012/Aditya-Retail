# 📚 AI Agents Knowledge Base Training Guide

## Overview
Your AI Sales and Service agents can be trained with product manuals, brochures, troubleshooting guides, and technical documents. This makes them **extremely knowledgeable** about product features, specifications, error codes, and troubleshooting procedures.

---

## 🎯 What Can You Train the Agents With?

### Supported Document Types:
1. **Product Manuals** - Complete user manuals with features, specifications, usage instructions
2. **Installation Guides** - Step-by-step installation procedures
3. **Troubleshooting Guides** - Error codes, common issues, and solutions
4. **Technical Specifications** - Detailed technical data sheets
5. **Warranty Information** - Warranty terms, coverage details
6. **FAQ Documents** - Frequently asked questions and answers
7. **Service Bulletins** - Service advisories and updates

### Supported File Formats:
- **PDF** (.pdf) - Most common for manuals and brochures
- **Word Documents** (.docx) - Editable documents
- **Text Files** (.txt) - Plain text documents

---

## 🚀 How to Upload Training Documents

### Method 1: Via API (Programmatic Upload)

```bash
# Upload a product manual
curl -X POST "https://your-domain.com/api/knowledge-base/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@bosch_washing_machine_manual.pdf" \
  -F "title=Bosch WAJ2846IIN User Manual" \
  -F "document_type=manual" \
  -F "brand=Bosch" \
  -F "category=Washing Machine" \
  -F "product_ids=WAJ2846IIN,WAJ2016IN"
```

### Method 2: Via Admin Panel (Recommended)

**Step 1: Access Knowledge Base Management**
1. Login to Admin Panel (`/admin`)
2. Navigate to **Knowledge Base** section (if UI is implemented)

**Step 2: Upload Document**
1. Click "Upload Document" button
2. Fill in details:
   - **File**: Select PDF/DOCX/TXT file
   - **Title**: e.g., "Bosch Series 6 Washing Machine Manual"
   - **Document Type**: Select from dropdown (Manual, Troubleshooting, Installation, FAQ, Warranty)
   - **Brand**: Bosch, Siemens, Hindware, etc.
   - **Category**: Washing Machine, Refrigerator, Chimney, etc.
   - **Product IDs**: Enter product model numbers (comma-separated)
3. Click "Upload & Process"

**Step 3: Verify Upload**
- System will extract text from the document
- You'll see a success message with document ID
- Document is now available to AI agents

---

## 📖 How AI Agents Use the Knowledge Base

### Automatic Integration
The AI agents **automatically access** the knowledge base when:

1. **Customer asks about a specific product**
   - Example: "How do I clean the filter in my Bosch WAJ2846IIN?"
   - Agent searches knowledge base for product manual
   - Provides accurate step-by-step instructions

2. **Error code or issue is mentioned**
   - Example: "My washing machine shows error E18"
   - Agent finds troubleshooting guide
   - Provides exact error meaning and solution steps

3. **Technical specifications requested**
   - Example: "What's the spin speed of this model?"
   - Agent retrieves spec from manual
   - Provides precise technical details

### Knowledge Base Search Flow:

```
Customer Question
     ↓
AI Agent Analyzes Query
     ↓
Searches Knowledge Base by:
  - Product ID/Model Number
  - Brand & Category
  - Keywords (error code, feature name)
     ↓
Retrieves Relevant Documents
     ↓
Extracts Specific Information
     ↓
Provides Accurate Answer to Customer
```

---

## 💡 Best Practices for Maximum Effectiveness

### 1. **Document Naming Convention**
Use clear, descriptive titles:
- ✅ Good: "Bosch WAJ2846IIN Series 6 Front Load Washing Machine User Manual"
- ❌ Bad: "manual_final_v2.pdf"

### 2. **Always Include Product IDs**
Link documents to specific products:
```
Product IDs: WAJ2846IIN, WAJ2016IN, WAK2406IIN
```
This ensures agents retrieve the right manual for the right product.

### 3. **Categorize by Document Type**
Properly categorize documents:
- **Manual**: Complete user guides
- **Troubleshooting**: Error codes, common issues
- **Installation**: Setup and installation procedures
- **Warranty**: Terms, coverage, service information
- **FAQ**: Frequently asked questions

### 4. **Keep Documents Updated**
- Upload latest versions of manuals
- Delete outdated documents
- Update troubleshooting guides with new solutions

### 5. **Cover All Product Lines**
Upload documents for:
- All brands you sell (Bosch, Siemens, Hindware)
- All categories (Washing Machines, Refrigerators, Chimneys, Ovens, Dishwashers)
- Popular models first, then expand

---

## 🔍 Searching the Knowledge Base

### API Endpoint for Search:
```bash
# Search for specific information
curl "https://your-domain.com/api/knowledge-base/search/query?query=error%20E18&limit=5"
```

### Get Documents by Product:
```bash
# Get all documents for a specific product
curl "https://your-domain.com/api/knowledge-base/product/WAJ2846IIN/documents"
```

### Filter by Type/Brand/Category:
```bash
# Get all troubleshooting guides for Bosch washing machines
curl "https://your-domain.com/api/knowledge-base/?document_type=troubleshooting&brand=Bosch&category=Washing%20Machine"
```

---

## 📊 Knowledge Base Statistics

After uploading documents, you can view:
- Total documents in knowledge base
- Documents per product category
- Documents per brand
- Coverage percentage (products with manuals vs without)

---

## 🎯 Example Use Cases

### Use Case 1: Service Agent with Error Code Knowledge
**Customer:** "My Bosch washing machine shows error E18"

**Without Knowledge Base:**
- Agent: "That's a drainage error. Please check with a technician."

**With Knowledge Base:**
- Agent: "Error E18 indicates a drainage problem. Let me help you troubleshoot:
  1. Check if the drain hose is kinked or blocked
  2. Clean the drain filter (located at bottom front panel)
  3. Ensure drain pipe isn't clogged
  4. If problem persists, the drain pump may need inspection.
  
  Would you like me to create a service ticket for a technician visit?"

### Use Case 2: Sales Agent with Specification Knowledge
**Customer:** "What's the difference between WAJ2846IIN and WAK2406IIN?"

**Without Knowledge Base:**
- Agent: "Both are Bosch washing machines. Let me show you the product pages."

**With Knowledge Base:**
- Agent: "Great question! Here's the comparison:
  
  **WAJ2846IIN (Series 6)**
  - Capacity: 8 kg
  - Spin Speed: 1200 RPM
  - Features: VarioDrum, EcoSilence Drive, SpeedPerfect
  - Price: ₹45,990
  
  **WAK2406IIN (Serie 4)**
  - Capacity: 6 kg
  - Spin Speed: 1000 RPM
  - Features: VarioDrum, ActiveWater Plus
  - Price: ₹32,990
  
  For a family of 4+, I recommend the WAJ2846IIN for its larger capacity and faster spin speed."

---

## 🔐 Security & Access Control

### Document Access Levels:
- **Public**: Available to all AI agents (manuals, FAQs)
- **Internal**: Only for service agents (service bulletins, warranty terms)
- **Restricted**: Admin only (pricing strategies, vendor contracts)

### Data Privacy:
- Documents are stored securely on your server
- Only extracted text is used for AI training
- Original files are preserved for reference
- No data is shared with third parties

---

## 🚦 Getting Started Checklist

- [ ] Collect product manuals for your top 20 best-selling products
- [ ] Organize documents by brand and category
- [ ] Upload manuals via API or admin panel
- [ ] Test AI agents by asking specific product questions
- [ ] Upload troubleshooting guides for common issues
- [ ] Add installation guides for technical products
- [ ] Set up warranty information documents
- [ ] Create FAQs for frequently asked questions
- [ ] Train staff on how to upload new documents
- [ ] Schedule monthly knowledge base updates

---

## 📞 API Endpoints Reference

### Upload Document
```
POST /api/knowledge-base/upload
Content-Type: multipart/form-data

Parameters:
- file: File (PDF/DOCX/TXT)
- title: string
- document_type: string (manual|troubleshooting|installation|faq|warranty)
- brand: string (optional)
- category: string (optional)
- product_ids: string (comma-separated, optional)
```

### Get All Documents
```
GET /api/knowledge-base/
Query Parameters:
- document_type: string (optional)
- brand: string (optional)
- category: string (optional)
```

### Search Knowledge Base
```
GET /api/knowledge-base/search/query
Query Parameters:
- query: string (required)
- document_type: string (optional)
- limit: integer (default: 10)
```

### Get Product Documents
```
GET /api/knowledge-base/product/{product_id}/documents
```

### Delete Document
```
DELETE /api/knowledge-base/{document_id}
```

---

## 💬 Support & Troubleshooting

### Common Issues:

**Issue:** Document uploaded but agents don't use the information

**Solution:**
- Verify document was successfully processed (check content length in response)
- Ensure product_ids are correctly linked
- Test search endpoint to confirm document is retrievable
- Check if document type is appropriate for the query

**Issue:** PDF extraction failed

**Solution:**
- Ensure PDF is not password-protected
- Try converting to DOCX or TXT format
- Check if PDF contains scanned images (OCR not supported yet)
- Verify file is not corrupted

**Issue:** Search not returning relevant results

**Solution:**
- Use more specific keywords
- Include product model numbers
- Try different search terms
- Check if MongoDB text index is created

---

## 🎓 Training Your Team

### For Admin Staff:
1. Learn how to upload documents properly
2. Understand document categorization
3. Know how to verify successful uploads
4. Practice searching the knowledge base

### For Customer Support:
1. Trust the AI agents' knowledge
2. Monitor conversations for accuracy
3. Report gaps in knowledge base
4. Suggest new documents to upload

### For Technical Team:
1. Understand API endpoints
2. Know how to troubleshoot extraction issues
3. Monitor knowledge base database
4. Maintain document organization

---

## 📈 Measuring Success

### Key Metrics:
1. **Knowledge Base Coverage**
   - % of products with manuals uploaded
   - Target: 80%+ for best-sellers

2. **Agent Response Accuracy**
   - % of questions answered correctly with KB
   - Target: 90%+

3. **Customer Satisfaction**
   - Feedback on AI agent helpfulness
   - Target: 4.5+ out of 5

4. **Service Ticket Reduction**
   - Decrease in tickets for "simple issues"
   - Target: 30% reduction

---

## 🔮 Future Enhancements

Coming soon:
- Image extraction from PDFs (diagrams, schematics)
- OCR support for scanned documents
- Auto-categorization using AI
- Multi-language document support
- Version control for documents
- AI-suggested knowledge gaps
- Integration with video tutorials

---

**Your AI agents are now ready to become product experts! Start uploading manuals today. 🚀**
