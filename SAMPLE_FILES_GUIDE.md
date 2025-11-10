# Sample Files Guide - PO and Invoice Test Sets

## 📁 Location
All sample files are in the `sample_files/` folder.

---

## 📊 Available Test Sets

### **Set 1: Price Mismatches**
**Files:**
- `sample_po_set1.xlsx`
- `sample_invoice_set1.xlsx`

**Issues:**
- ✅ **LAPTOP-001**: Price mismatch ($1200.00 → $1250.00)
- ✅ **KEYBOARD-003**: Price mismatch ($89.99 → $95.00)
- ✅ **WEBCAM-005**: Price mismatch ($45.00 → $50.00)

**Expected Results:**
- 3 mismatches detected
- 0 duplicates
- 0 anomalies

---

### **Set 2: Duplicates**
**Files:**
- `sample_po_set2.xlsx`
- `sample_invoice_set2.xlsx`

**Issues:**
- ✅ **MOUSE-002**: Appears **twice** in invoice
- ✅ **WEBCAM-005**: Appears **twice** in invoice

**Expected Results:**
- 0 mismatches
- 2 duplicates detected
- 0 anomalies

---

### **Set 3: Mismatches + Duplicates** ⭐ Recommended
**Files:**
- `sample_po_set3.xlsx`
- `sample_invoice_set3.xlsx`

**Issues:**
- ✅ **Price Mismatches:**
  - LAPTOP-001: $1200.00 → $1250.00
  - KEYBOARD-003: $89.99 → $95.00
  - WEBCAM-005: $45.00 → $50.00
- ✅ **Duplicates:**
  - MOUSE-002: Appears twice

**Expected Results:**
- 3 mismatches detected
- 1 duplicate detected
- 0 anomalies

---

### **Set 4: Quantity Mismatches**
**Files:**
- `sample_po_set4.xlsx`
- `sample_invoice_set4.xlsx`

**Issues:**
- ✅ **LAPTOP-001**: Quantity mismatch (5 → 6)
- ✅ **MONITOR-004**: Quantity mismatch (4 → 5)

**Expected Results:**
- 2 mismatches detected (quantity differences)
- 0 duplicates
- 0 anomalies

---

### **Set 5: Multiple Issues** ⭐ Most Comprehensive
**Files:**
- `sample_po_set5.xlsx`
- `sample_invoice_set5.xlsx`

**Issues:**
- ✅ **Price Mismatches:**
  - LAPTOP-001: $1200.00 → $1250.00
  - KEYBOARD-003: $89.99 → $95.00
  - WEBCAM-005: $45.00 → $50.00
- ✅ **Duplicates:**
  - MOUSE-002: Appears twice
- ✅ **Anomalies:**
  - SPEAKER-006: New item in invoice, not in PO

**Expected Results:**
- 3 mismatches detected
- 1 duplicate detected
- 1 anomaly detected (new item)

---

## 🧪 How to Use

### Testing in the Application:

1. **Upload Files:**
   - Go to the **Upload** tab
   - Upload the PO file (e.g., `sample_po_set3.xlsx`)
   - Upload the Invoice file (e.g., `sample_invoice_set3.xlsx`)
   - Enter a reference name (e.g., "Test Set 3")

2. **Analyze:**
   - Click "Analyze & Compare"
   - Wait for processing

3. **Review Results:**
   - Check the **Results** tab
   - Verify mismatches, duplicates, and anomalies match expected results

---

## 📋 Detailed Breakdown

### Set 1 - Price Mismatches Only
```
PO Items:
- LAPTOP-001: Qty 5, Price $1200.00
- MOUSE-002: Qty 10, Price $25.50
- KEYBOARD-003: Qty 8, Price $89.99
- MONITOR-004: Qty 4, Price $350.00
- WEBCAM-005: Qty 6, Price $45.00

Invoice Items (with mismatches):
- LAPTOP-001: Qty 5, Price $1250.00 ❌ (+$50)
- MOUSE-002: Qty 10, Price $25.50 ✅
- KEYBOARD-003: Qty 8, Price $95.00 ❌ (+$5.01)
- MONITOR-004: Qty 4, Price $350.00 ✅
- WEBCAM-005: Qty 6, Price $50.00 ❌ (+$5)
```

### Set 2 - Duplicates Only
```
PO Items: 5 unique items
Invoice Items: 7 items (2 duplicates)
- MOUSE-002 appears twice
- WEBCAM-005 appears twice
```

### Set 3 - Combined Issues
```
PO Items: 5 unique items
Invoice Items: 6 items
- 3 price mismatches
- 1 duplicate (MOUSE-002)
```

### Set 4 - Quantity Mismatches
```
PO Items:
- LAPTOP-001: Qty 5
- MONITOR-004: Qty 4

Invoice Items:
- LAPTOP-001: Qty 6 ❌ (+1)
- MONITOR-004: Qty 5 ❌ (+1)
```

### Set 5 - All Issues
```
PO Items: 5 items
Invoice Items: 7 items
- 3 price mismatches
- 1 duplicate
- 1 new item (SPEAKER-006) not in PO
```

---

## ✅ Verification Checklist

After running each set, verify:

- [ ] Correct number of mismatches detected
- [ ] Correct number of duplicates detected
- [ ] Correct number of anomalies detected
- [ ] Specific items flagged correctly
- [ ] Price differences shown accurately
- [ ] Duplicate items identified properly

---

## 🎯 Recommended Testing Order

1. **Start with Set 1** - Simple price mismatches
2. **Then Set 2** - Test duplicate detection
3. **Then Set 3** - Combined issues (most realistic)
4. **Then Set 4** - Quantity mismatches
5. **Finally Set 5** - All issues (comprehensive test)

---

## 📝 Notes

- All files use standard Excel format (.xlsx)
- Headers are: Item, Description, Quantity, Unit Price, Total
- Files are formatted with colored headers
- Column names are standardized for easy parsing

---

**All sample files are ready for testing! 🚀**

