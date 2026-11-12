# 📚 Knowledge Base Upload Guide - Simple & Easy

## ✅ **DO NOT Rename Files!**

### **You can upload files EXACTLY as downloaded from brand websites.**

The system doesn't use filenames to identify content. Instead, it uses:
1. **Title** (you provide during upload)
2. **Document Type** (manual, troubleshooting, etc.)
3. **Brand & Category** (for better organization)
4. **Product IDs** (to link to specific products)
5. **File Content** (the actual text inside the PDF)

---

## 🎯 **WORKFLOW: Download → Upload (That's It!)**

### **Example Scenario:**

#### **Step 1: Download from Bosch Website**
You download: `bosch_waj2846iin_user_manual_v2_final.pdf`

#### **Step 2: Upload to Knowledge Base**
- **File**: Keep the original name (no need to rename!)
- **Title**: "Bosch WAJ2846IIN Series 6 Washing Machine User Manual"
- **Document Type**: "manual"
- **Brand**: "Bosch"
- **Category**: "Washing Machine"
- **Product IDs**: "WAJ2846IIN"

#### **What AI Agents See:**
They search by:
- Product model number (WAJ2846IIN)
- Brand (Bosch)
- Category (Washing Machine)
- Content inside the PDF (error codes, features, specs)

They **DON'T** care about the filename!

---

## 📥 **UPLOAD METHODS**

### **Method 1: Admin Panel (Easiest)**

1. Login to Admin Panel: `https://www.adityaretail.com/#/admin`
2. Go to "Knowledge Base"
3. Click "Upload Document"
4. Select your PDF (use original filename)
5. Fill in the form:
   ```
   Title: Bosch WAJ2846IIN User Manual
   Type: manual
   Brand: Bosch
   Category: Washing Machine
   Product IDs: WAJ2846IIN
   ```
6. Click "Upload"

**Done!** AI agents can now use this manual.

---

### **Method 2: API Upload (Bulk)**

If you have many files, use API:

```bash
curl -X POST "https://www.adityaretail.com/api/knowledge-base/upload" \
  -F "file=@bosch_waj2846iin_user_manual_v2_final.pdf" \
  -F "title=Bosch WAJ2846IIN User Manual" \
  -F "document_type=manual" \
  -F "brand=Bosch" \
  -F "category=Washing Machine" \
  -F "product_ids=WAJ2846IIN"
```

---

## 🎯 **WHAT TO PROVIDE (Metadata)**

### **Required:**
1. **Title** - Clear, descriptive name
   - ✅ Good: "Bosch WAJ2846IIN Series 6 User Manual"
   - ❌ Bad: "manual_v2_final.pdf"

2. **Document Type** - Choose from:
   - `manual` - User manuals, operation guides
   - `troubleshooting` - Error codes, common issues
   - `installation` - Installation instructions
   - `warranty` - Warranty information
   - `faq` - Frequently asked questions

### **Optional (But Highly Recommended):**
3. **Brand** - Bosch, Siemens, Hindware, etc.
4. **Category** - Washing Machine, Refrigerator, Chimney, etc.
5. **Product IDs** - Model numbers (comma-separated)
   - Example: "WAJ2846IIN,WAK2406IIN,WAT2846IIN"

---

## 📋 **EXAMPLES: Real Brand Website Downloads**

### **Example 1: Bosch Washing Machine**

**Downloaded from Bosch website:**
- Filename: `BSH_WashingMachine_2023_UserGuide_EN_v1.2.pdf`

**Upload as:**
```
File: BSH_WashingMachine_2023_UserGuide_EN_v1.2.pdf (don't rename!)
Title: Bosch Serie 6 Front Load Washing Machine User Guide
Type: manual
Brand: Bosch
Category: Washing Machine
Product IDs: WAJ2846IIN,WAK2406IIN,WAT2846IIN
```

---

### **Example 2: Siemens Error Codes**

**Downloaded:**
- Filename: `siemens_error_codes_troubleshooting.pdf`

**Upload as:**
```
File: siemens_error_codes_troubleshooting.pdf
Title: Siemens Washing Machine Error Codes & Troubleshooting
Type: troubleshooting
Brand: Siemens
Category: Washing Machine
Product IDs: (leave blank if applies to all Siemens washing machines)
```

---

### **Example 3: Installation Guide**

**Downloaded:**
- Filename: `INST_MANUAL_CHIMNEY_DWB98IJ60I_REV3.pdf`

**Upload as:**
```
File: INST_MANUAL_CHIMNEY_DWB98IJ60I_REV3.pdf
Title: Bosch DWB98IJ60I Chimney Installation Guide
Type: installation
Brand: Bosch
Category: Chimney
Product IDs: DWB98IJ60I
```

---

## 🤖 **HOW AI AGENTS FIND THE RIGHT MANUAL**

### **Customer Query:** "My Bosch washing machine WAJ2846IIN shows error E18"

### **What AI Agent Does:**
1. Extracts: Product model = "WAJ2846IIN", Error = "E18"
2. Searches knowledge base for:
   - Documents with product_id = "WAJ2846IIN"
   - OR brand = "Bosch" AND category = "Washing Machine"
   - AND content contains "E18"
3. Finds: "Bosch Washing Machine Error Codes Guide"
4. Reads: "Error E18 = Drainage problem. Steps: 1) Check filter..."
5. Provides accurate answer to customer!

**The filename was never used!**

---

## 📦 **BULK UPLOAD STRATEGY**

### **Step 1: Organize by Brand**
```
Downloads/
├── Bosch/
│   ├── washing_machine_manual_2023.pdf
│   ├── chimney_installation_guide.pdf
│   ├── error_codes_all_products.pdf
├── Siemens/
│   ├── refrigerator_manual.pdf
│   ├── oven_installation.pdf
```

### **Step 2: Upload Brand by Brand**
- Upload all Bosch manuals first
- Then Siemens
- Then other brands

### **Step 3: Test AI Agents**
- Ask product-specific questions
- Check if agents provide accurate answers
- Upload more manuals as needed

---

## ✅ **BEST PRACTICES**

### **DO:**
✅ Download PDFs directly from brand websites (most accurate)
✅ Keep original filenames (easier to track source)
✅ Provide clear, descriptive titles
✅ Link to specific product model numbers
✅ Upload troubleshooting guides separately from user manuals
✅ Test AI agents after uploading new manuals

### **DON'T:**
❌ Rename files (no benefit, waste of time)
❌ Skip metadata (brand, category, product IDs)
❌ Upload without testing
❌ Forget to link product IDs
❌ Upload duplicate content
❌ Use images-only PDFs (system needs text)

---

## 🎯 **PRIORITY: WHAT TO UPLOAD FIRST**

### **Phase 1: Error Codes (Highest Impact)**
Upload troubleshooting guides with error codes for:
1. Washing machines (E18, E17, E02, etc.)
2. Refrigerators (common errors)
3. Chimneys (motor issues)
4. Ovens (heating errors)
5. Dishwashers (drainage issues)

**Why first?** Customers contact support most for errors.

---

### **Phase 2: Popular Products (High Volume)**
Upload user manuals for:
1. Top 10 best-selling products
2. Latest models
3. Premium products (higher profit margin)

---

### **Phase 3: Installation Guides**
Upload for:
1. Products requiring professional installation
2. Built-in appliances (ovens, chimneys, hobs)

---

### **Phase 4: Complete Coverage**
Upload for:
1. All remaining products
2. Warranty guides
3. FAQs
4. Maintenance guides

---

## 🔍 **FINDING MANUALS ON BRAND WEBSITES**

### **Bosch:**
1. Go to: https://www.bosch-home.in/
2. Search product model
3. Click "Downloads" or "Support"
4. Download PDF

### **Siemens:**
1. Go to: https://www.siemens-home.bsh-group.com/in/
2. Enter model number
3. Click "Documents"
4. Download manual

### **If Manual Not Available:**
- Contact brand support
- Or use generic category manual
- Clearly mark as "generic" in title

---

## 📊 **TRACKING UPLOADS**

### **Check Current Knowledge Base:**
```bash
curl "https://www.adityaretail.com/api/knowledge-base/" | jq
```

### **Search for Specific Product:**
```bash
curl "https://www.adityaretail.com/api/knowledge-base/product/WAJ2846IIN/documents"
```

### **View Upload Statistics:**
In Admin Panel:
- Knowledge Base section
- Shows: Total documents, by brand, by category
- Click to view/delete

---

## 🎓 **EXAMPLES: COMPLETE WORKFLOWS**

### **Scenario 1: New Product Launch**

**Task:** Add Bosch Serie 8 Refrigerator (model: KGN864IFP)

**Steps:**
1. Go to Bosch website
2. Find model: KGN864IFP
3. Download:
   - User manual
   - Installation guide
   - Energy label (if PDF)
4. Upload all 3 files to Knowledge Base:
   ```
   File 1: user_manual_KGN864IFP_v1.pdf
   Title: Bosch KGN864IFP Serie 8 Refrigerator User Manual
   Type: manual
   Brand: Bosch
   Category: Refrigerator
   Product IDs: KGN864IFP

   File 2: installation_KGN864IFP.pdf
   Title: Bosch KGN864IFP Installation Guide
   Type: installation
   Brand: Bosch
   Category: Refrigerator
   Product IDs: KGN864IFP

   File 3: energy_specs_KGN864IFP.pdf
   Title: Bosch KGN864IFP Energy Specifications
   Type: manual
   Brand: Bosch
   Category: Refrigerator
   Product IDs: KGN864IFP
   ```
5. Test: Ask AI agent "What are the specs of Bosch KGN864IFP?"
6. Verify: Agent provides accurate info

**Done!** Product is fully documented.

---

### **Scenario 2: High Support Calls for Error E18**

**Task:** Reduce support calls about error E18 in washing machines

**Steps:**
1. Find all washing machine error code guides from:
   - Bosch website
   - Siemens website
2. Download PDF manuals
3. Upload as type "troubleshooting"
4. Test: Ask "What is error E18?" to service agent
5. Monitor: Support call reduction

---

## 💡 **PRO TIPS**

### **Tip 1: Version Control**
Include version in title if important:
- "Bosch WAJ2846IIN User Manual (2023)"
- "Bosch WAJ2846IIN User Manual (Updated 2024)"

### **Tip 2: Language**
If you have manuals in multiple languages:
- Upload all versions
- Add language to title: "...Manual (Hindi)"

### **Tip 3: Combine Related Files**
If you have separate PDFs for same product:
- Upload each separately
- Use same Product IDs
- AI will search all related documents

### **Tip 4: Update Old Manuals**
If brand releases updated manual:
- Upload new version
- Delete old version
- Or keep both with version numbers

---

## ⚠️ **COMMON ISSUES & SOLUTIONS**

### **Issue:** "AI agent not providing accurate info"

**Solution:**
1. Check if manual is uploaded for that product
2. Search knowledge base: `/api/knowledge-base/product/{product_id}/documents`
3. If missing, upload manual
4. Test again

---

### **Issue:** "Upload says 0 words extracted"

**Solution:**
1. PDF might be image-based (scanned)
2. Convert to text-based PDF first
3. Or use OCR tool
4. Re-upload

---

### **Issue:** "AI mentions wrong product model"

**Solution:**
1. Check Product IDs field during upload
2. Ensure correct model number
3. Re-upload with correct IDs

---

## 📞 **QUICK REFERENCE**

### **Upload Checklist:**
- [ ] Downloaded from official brand website
- [ ] File is text-based PDF (not image scan)
- [ ] Clear title provided
- [ ] Document type selected
- [ ] Brand name added
- [ ] Category specified
- [ ] Product ID(s) linked
- [ ] Uploaded successfully
- [ ] Tested with AI agent

### **File Naming: DON'T WASTE TIME!**
❌ Don't rename: `bosch_manual_123.pdf` → `WAJ2846IIN_manual.pdf`
✅ Just upload: `bosch_manual_123.pdf` with proper title in form

---

**Your AI agents are learning machines - the more you feed them (quality manuals), the smarter they get!** 🤖📚
