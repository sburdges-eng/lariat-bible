# LARIAT BANQUET SYSTEM - Q&A CUSTOMIZATION GUIDE
**Interactive System Configuration Tool**

---

## 🎯 **PURPOSE**

This guide helps you customize the Lariat Banquet System to fit your specific business needs. Answer these questions honestly to identify which features to implement, what to modify in templates, and how to optimize the workflow for your operation.

**Time to Complete:** 45-90 minutes
**Best Completed By:** Owner, Manager, and Key Staff together
**Result:** Clear roadmap for system customization

---

## 📋 **HOW TO USE THIS GUIDE**

1. **Answer Honestly** - Don't answer based on what you think you "should" do. Answer based on your actual business practices.

2. **Skip When Unsure** - If you're not sure about a question, skip it and come back later. You don't need all answers on day one.

3. **Document Your Answers** - Write your answers down. They'll guide your implementation.

4. **Prioritize** - Mark which customizations are:
   - ⭐ CRITICAL (must have before go-live)
   - ⭐⭐ IMPORTANT (implement in first month)
   - ⭐⭐⭐ NICE TO HAVE (add later as needed)

5. **Review Regularly** - Revisit this guide quarterly as your business evolves.

---

## 📊 **SECTION 1: PRICING & FINANCIAL STRUCTURE** (8 Questions)

### **Q1: What are your minimum spend requirements by event size?**

**Current minimum spends in the system:**
- <50 guests: $2,500 minimum
- 50-100 guests: $5,000 minimum
- 100-200 guests: $10,000 minimum
- 200+ guests: $15,000 minimum

**Your Answer:**
```
<50 guests: $__________ minimum
50-100 guests: $__________ minimum
100-200 guests: $__________ minimum
200+ guests: $__________ minimum
```

**Impact:** This value appears in invoice minimum spend check (cells E33-E34)
**Priority:** ⭐ CRITICAL
**Implementation:** Update Invoice Template values

---

### **Q2: What is your sales tax rate?**

**Current rate in system:** 8.15%

**Your Answer:** _________ %

**Impact:** Affects formula in cell D28 of Invoice Template
**Priority:** ⭐ CRITICAL
**Implementation:** Change formula `=D27*0.0815` to `=D27*[YOUR RATE]`

---

### **Q3: What is your service fee / gratuity percentage?**

**Current rate in system:** 20%

**Your Answer:** _________ %

**Is this mandatory or optional?**
- [ ] Mandatory (always charged)
- [ ] Optional (at client discretion)
- [ ] Varies by event type

**Impact:** Affects formula in cell D29 of Invoice Template
**Priority:** ⭐ CRITICAL
**Implementation:** Change formula `=D27*0.20` to `=D27*[YOUR RATE]`

---

### **Q4: Do you offer volume discounts?**

**Options:**
- [ ] No discounts offered
- [ ] Yes, discount structure:
  - Events over $______: _____% discount
  - Events over $______: _____% discount
  - Events over $______: _____% discount

**Impact:** May require additional row in invoice template
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add discount calculation row after subtotal

---

### **Q5: Do you charge delivery/travel fees?**

**Options:**
- [ ] No delivery fees
- [ ] Flat fee: $________ per event
- [ ] Distance-based:
  - 0-10 miles: $______
  - 11-20 miles: $______
  - 21-30 miles: $______
  - 30+ miles: Quote custom
- [ ] Time-based: $______ per hour travel time

**Impact:** Requires additional line item in invoice
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add "Delivery Fee" row to invoice template

---

### **Q6: What are your deposit and payment terms?**

**Current terms in system:**
- Booking: 25% deposit
- 14 days before: 50% payment
- Day of event: Final 25% + any additions

**Your Answer:**
```
Booking: _____% deposit due when: _______________
Second payment: _____% due when: _______________
Final payment: _____% due when: _______________
```

**Payment methods accepted:**
- [ ] Cash
- [ ] Check
- [ ] Credit Card (fees: _____%)
- [ ] ACH/Bank Transfer
- [ ] Venmo/PayPal/Zelle
- [ ] Other: __________

**Impact:** Affects contract terms and client communication
**Priority:** ⭐ CRITICAL
**Implementation:** Update contract template, invoice notes

---

### **Q7: Do you charge setup/breakdown/rental fees?**

**Options:**
- [ ] Setup included in price
- [ ] Setup fee: $______ (flat) or $______ per hour
- [ ] Breakdown fee: $______ (flat) or $______ per hour
- [ ] Equipment rental fees:
  - Chafing dishes: $______ each
  - Tables: $______ each
  - Linens: $______ each
  - Other: _____________: $______

**Impact:** Requires additional line items in invoice
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add fee rows to invoice template

---

### **Q8: Do you require event insurance or certificates?**

**Options:**
- [ ] No insurance required
- [ ] Yes, certificate of insurance required
  - Minimum coverage: $_____________
  - Required days before event: _______
- [ ] We provide insurance for fee: $______

**Impact:** Affects booking process and contract
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Update contract, add to booking checklist

---

## 🍽️ **SECTION 2: MENU & OFFERINGS** (6 Questions)

### **Q9: Which menu items are seasonal or limited availability?**

**List items that are:**
- **Summer Only:** _______________________________
- **Fall Only:** _________________________________
- **Winter Only:** _______________________________
- **Spring Only:** _______________________________
- **Year-round:** ________________________________

**Impact:** Add notes to price lookup table indicating seasonality
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add "Season" column to price lookup (Column H)

---

### **Q10: Which items require special equipment or cannot be made at certain venues?**

**Equipment-dependent items:**
```
Item: _________________ Requires: _________________
Item: _________________ Requires: _________________
Item: _________________ Requires: _________________
```

**Items requiring on-site kitchen:**
- _________________________
- _________________________

**Impact:** Add equipment notes to kitchen sheet template
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add "Equipment Needed" column to kitchen sheet

---

### **Q11: What are minimum order quantities for specific items?**

**Examples:**
```
Whole pigs/large proteins: Minimum _____ guests
Specialty cakes: Minimum order $______
Custom items: Minimum _____ servings
```

**Impact:** Add minimum quantity checks to invoice
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Add validation or notes to invoice template

---

### **Q12: Which items CANNOT be made in advance?**

**Must be made day-of:**
- _________________________
- _________________________
- _________________________

**Maximum advance prep time by item:**
```
Item: _______________ Max advance: _____ days
Item: _______________ Max advance: _____ days
Item: _______________ Max advance: _____ days
```

**Impact:** Affects production schedule timing
**Priority:** ⭐ CRITICAL
**Implementation:** Document in workflow, add to production schedule

---

### **Q13: Do items pair well or poorly together? Any restrictions?**

**Items that pair well (suggest as bundles):**
- _________________ + _________________ + _________________
- _________________ + _________________ + _________________

**Items that DON'T pair well (avoid together):**
- _________________ + _________________ (Reason: _________)
- _________________ + _________________ (Reason: _________)

**Impact:** Add notes to sales process, suggested combinations
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Create pairing guide for sales team

---

### **Q14: What dietary accommodations do you offer?**

**Check all that apply:**
- [ ] Vegetarian options
- [ ] Vegan options
- [ ] Gluten-free options (certified or just gluten-free ingredients?)
- [ ] Dairy-free options
- [ ] Nut-free options (do you have nut-free facility?)
- [ ] Kosher options
- [ ] Halal options
- [ ] Low-carb/Keto options
- [ ] Other: _________________

**Surcharge for special dietary items?**
- [ ] No surcharge
- [ ] Yes: _____% upcharge
- [ ] Varies by item

**Impact:** Add dietary options to invoice notes, menu pricing
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Expand price lookup table with dietary variants

---

## 👨‍🍳 **SECTION 3: KITCHEN WORKFLOW & CAPACITY** (5 Questions)

### **Q15: How many staff typically work events by size?**

**Staffing levels:**
```
20-50 guests:
  Prep: _____ people
  Service: _____ people

50-100 guests:
  Prep: _____ people
  Service: _____ people

100-200 guests:
  Prep: _____ people
  Service: _____ people

200+ guests:
  Prep: _____ people
  Service: _____ people
```

**Impact:** Affects production schedule, labor cost calculations
**Priority:** ⭐ CRITICAL
**Implementation:** Build into production schedule template

---

### **Q16: What is your kitchen's simultaneous prep capacity?**

**Equipment limitations:**
```
Ovens: _____ total, can run _____ items simultaneously
Stovetop burners: _____ total
Fryers: _____ total, _____ gallon capacity each
Refrigerator space: _____ cubic feet
Freezer space: _____ cubic feet
Dry storage: _____ square feet
```

**Maximum items you can prep in one day:** _____

**Impact:** Determines production schedule feasibility
**Priority:** ⭐ CRITICAL
**Implementation:** Add to production schedule planning

---

### **Q17: Do you prep on-site or off-site for events?**

**Options:**
- [ ] All prep in our kitchen, transport to venue
- [ ] Some items prepped on-site at venue
- [ ] Depends on venue kitchen availability
- [ ] Hybrid: Prep in our kitchen, final assembly on-site

**Impact:** Affects production schedule timing, travel logistics
**Priority:** ⭐ CRITICAL
**Implementation:** Adjust workflow steps 9-10 accordingly

---

### **Q18: What equipment do you own vs. rent for events?**

**Owned Equipment:**
- [ ] Chafing dishes (quantity: _____)
- [ ] Hot boxes/warmers (quantity: _____)
- [ ] Coolers (quantity: _____)
- [ ] Serving utensils
- [ ] Tables
- [ ] Linens
- [ ] Other: ______________

**Typically Rented:**
- [ ] Tents
- [ ] Tables/chairs
- [ ] China/silverware
- [ ] Glassware
- [ ] Other: ______________

**Impact:** Affects setup costs, rental budget line items
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add rental tracking to invoice template

---

### **Q19: What are your recipe batch size limitations?**

**Maximum batch sizes (equipment constrained):**
```
Braised items (oven capacity): _____ lbs at once
Fried items (fryer capacity): _____ lbs at once
Sauces/soups (pot size): _____ gallons at once
Baked goods (oven space): _____ pans at once
```

**Impact:** Critical for recipe scaling calculations
**Priority:** ⭐ CRITICAL
**Implementation:** Document in recipe book, scaling guide

---

## 🛒 **SECTION 4: VENDOR & ORDERING** (5 Questions)

### **Q20: Who are your preferred vendors by category?**

**Primary Vendors:**
```
Broadline distributor: _________________
Specialty proteins: ____________________
Produce: ______________________________
Dairy: ________________________________
Dry goods: ____________________________
Disposables: __________________________
Alcohol (if applicable): _______________
```

**Impact:** Populates vendor ordering lists
**Priority:** ⭐ CRITICAL
**Implementation:** Update order guide with your vendors

---

### **Q21: Do you have negotiated pricing or contracts?**

**For each vendor, note:**
```
Vendor: _____________
Contract? [ ] Yes [ ] No
Negotiated discount: _____%
Account #: ______________
Rep name: ______________
Rep phone: ______________
```

**Impact:** Affects pricing accuracy, ordering process
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Maintain vendor contact list in system

---

### **Q22: What are vendor minimum order amounts and delivery fees?**

**Vendor minimums:**
```
Vendor: _____________ Minimum: $_____ Delivery fee: $_____
Vendor: _____________ Minimum: $_____ Delivery fee: $_____
Vendor: _____________ Minimum: $_____ Delivery fee: $_____
```

**Free delivery thresholds?**
- Vendor: __________ Free over: $_______
- Vendor: __________ Free over: $_______

**Impact:** Affects ordering strategy, may need to combine orders
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Document in ordering procedures

---

### **Q23: What are typical delivery windows?**

**Vendor delivery schedules:**
```
Vendor: _____________ Delivers: ________ (days of week)
                      Cutoff time: _____ Order by: _____

Vendor: _____________ Delivers: ________ (days of week)
                      Cutoff time: _____ Order by: _____

Vendor: _____________ Delivers: ________ (days of week)
                      Cutoff time: _____ Order by: _____
```

**Impact:** Determines when to place orders in workflow
**Priority:** ⭐ CRITICAL
**Implementation:** Adjust Step 7 timing in workflow

---

### **Q24: Who are backup vendors if primary is unavailable?**

**Backup plan:**
```
Primary: ______________ Backup: ______________
Primary: ______________ Backup: ______________
Primary: ______________ Backup: ______________
```

**Emergency sources (last resort):**
- Restaurant Depot: [ ] Yes [ ] No
- Costco: [ ] Yes [ ] No
- Sam's Club: [ ] Yes [ ] No
- Local grocery: _______________

**Impact:** Ensures you can always source ingredients
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Document in ordering procedures

---

## 🎉 **SECTION 5: EVENT EXECUTION & SERVICE** (5 Questions)

### **Q25: Do you offer staffing (servers, bartenders) as part of catering?**

**Options:**
- [ ] No, client provides staff
- [ ] Yes, we provide servers
  - Cost: $_____ per server per hour
  - Minimum hours: _____
- [ ] Yes, we provide bartenders
  - Cost: $_____ per bartender per hour
  - Minimum hours: _____
- [ ] Can arrange through staffing agency
  - Markup: _____%

**Impact:** Adds service to offerings, pricing structure
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Add staffing line items to invoice

---

### **Q26: Do you provide rentals (tables, linens, etc.)?**

**Rental offerings:**
- [ ] No rentals provided
- [ ] Yes, we have rentals:
  - Tables: $_____ each
  - Chairs: $_____ each
  - Linens: $_____ each
  - China: $_____ per setting
  - Glassware: $_____ per piece
  - Other: ________: $_____
- [ ] Partner with rental company (markup: ____%)

**Impact:** Expands revenue, requires inventory tracking
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Add rental section to invoice

---

### **Q27: What is your service area / delivery radius?**

**Service area:**
- Primary area (no travel fee): _____ miles radius
- Extended area (travel fee applies): _____ miles
- Will NOT travel beyond: _____ miles
- Travel time limits: Max _____ hours each way

**Impact:** Affects booking criteria, delivery fees
**Priority:** ⭐ CRITICAL
**Implementation:** Document in booking process

---

### **Q28: Do you offer setup and breakdown as standard or add-on?**

**Setup:**
- [ ] Included in all pricing
- [ ] Included for events >$_____ only
- [ ] Always an add-on fee: $_____
- [ ] Depends on venue/event type

**Breakdown:**
- [ ] Included in all pricing
- [ ] Included for events >$_____ only
- [ ] Always an add-on fee: $_____
- [ ] Depends on venue/event type

**Impact:** Affects pricing, labor scheduling
**Priority:** ⭐ CRITICAL
**Implementation:** Clarify in invoice and contracts

---

### **Q29: Do you handle decorations, florals, or ambiance elements?**

**Options:**
- [ ] No, strictly food service only
- [ ] Yes, basic décor included (what: _____________)
- [ ] Yes, as add-on service:
  - Centerpieces: $_____
  - Table settings: $_____
  - Ambiance lighting: $_____
- [ ] Partner with decorator (referral or markup: ____%)

**Impact:** Potential revenue stream, requires coordination
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Add to service offerings

---

## 🖥️ **SECTION 6: SYSTEM PREFERENCES & AUTOMATION** (6 Questions)

### **Q30: How do you currently manage event bookings?**

**Current system:**
- [ ] Email and phone only
- [ ] Spreadsheet tracking
- [ ] Calendar app (which one: _________)
- [ ] CRM software (which one: _________)
- [ ] Catering-specific software (which one: _________)
- [ ] Paper-based system

**Do you want to integrate with current system?**
- [ ] Yes, maintain current system alongside this one
- [ ] No, replace current system entirely
- [ ] Partially - use both for different purposes

**Impact:** Determines if data import/export needed
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** May need export templates

---

### **Q31: Do you want automated email notifications?**

**Automated emails:**
- [ ] Invoice sent to client automatically
- [ ] Payment reminders sent automatically
- [ ] Event reminders sent to client
- [ ] Headcount confirmation reminders
- [ ] Post-event thank you / review request
- [ ] None - prefer manual control

**Impact:** Requires email integration setup
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Future enhancement

---

### **Q32: How often do you want to review/update pricing?**

**Pricing review schedule:**
- [ ] Monthly
- [ ] Quarterly (recommended)
- [ ] Semi-annually
- [ ] Annually
- [ ] Only when vendor costs change significantly
- [ ] Ad-hoc / no schedule

**Who is responsible for pricing updates?**
- Name: _______________
- Backup: _______________

**Impact:** Determines maintenance schedule
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Set calendar reminders

---

### **Q33: Do you want to track actual vs. estimated costs per event?**

**Cost tracking:**
- [ ] Yes, track food cost actuals
- [ ] Yes, track labor cost actuals
- [ ] Yes, track total event profitability
- [ ] Yes, track all costs for analysis
- [ ] No, estimates are sufficient

**If yes, how will you track?**
- [ ] Save all vendor invoices and match to event
- [ ] Manual entry into tracking spreadsheet
- [ ] Integrated with accounting software

**Impact:** Adds post-event documentation step
**Priority:** ⭐⭐ IMPORTANT
**Implementation:** Create cost tracking template

---

### **Q34: How do you want to store/backup event files?**

**File storage:**
- [ ] Local computer only
- [ ] External hard drive backup
- [ ] Cloud storage (which: ________)
  - [ ] Google Drive
  - [ ] Dropbox
  - [ ] OneDrive
  - [ ] iCloud
  - [ ] Other: ________
- [ ] Multiple backups (local + cloud)

**Backup frequency:**
- [ ] Real-time (auto-sync)
- [ ] Daily
- [ ] Weekly
- [ ] After each event
- [ ] Manual only

**Impact:** Determines file organization structure
**Priority:** ⭐ CRITICAL
**Implementation:** Setup folder structure in chosen location

---

### **Q35: What reports/analytics are most valuable to you?**

**Most valuable metrics (rank 1-10, 1=most valuable):**
- ___ Total revenue by month
- ___ Revenue by event type
- ___ Food cost % trends
- ___ Labor cost trends
- ___ Most popular menu items
- ___ Most profitable menu items
- ___ Client acquisition sources
- ___ Repeat client rate
- ___ Average order value
- ___ Seasonal demand patterns

**How often do you want reports?**
- [ ] Weekly
- [ ] Monthly
- [ ] Quarterly
- [ ] Annually
- [ ] On-demand only

**Impact:** Determines which analytics to build
**Priority:** ⭐⭐⭐ NICE TO HAVE
**Implementation:** Create dashboard templates

---

## ✅ **CUSTOMIZATION SUMMARY WORKSHEET**

Use this to summarize your answers and prioritize implementation:

### **CRITICAL Changes (Must do before go-live):**

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
4. _________________________________________________
5. _________________________________________________

### **IMPORTANT Changes (Implement in first month):**

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
4. _________________________________________________
5. _________________________________________________

### **NICE TO HAVE Changes (Add as capacity allows):**

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
4. _________________________________________________
5. _________________________________________________

---

## 📋 **NEXT STEPS**

After completing this guide:

1. **Review your critical changes** - These must be done before using the system for a real event.

2. **Update templates** - Modify Invoice Template and other templates based on your critical answers.

3. **Test with sample event** - Create a fictional event using your customized templates.

4. **Train team** - Share relevant answers with staff (especially pricing, workflow, vendor info).

5. **Go live** - Start using for real events!

6. **Iterate** - Come back to this guide quarterly and update as your business evolves.

---

## 🎓 **REMEMBER:**

- **Perfect is the enemy of done** - You don't need to answer every question perfectly before starting. Get the critical items right, then iterate.

- **Business changes** - What's true today may not be true in 6 months. Update this guide as you grow.

- **Ask your team** - The people doing the work often have the best answers. Include them in this process.

- **Start simple** - Implement core features first, add complexity later.

---

**Document Version:** 1.0
**Last Updated:** November 19, 2025
**Next Review:** February 19, 2026
**Maintained By:** Lariat Banquet Team

---

**Now go customize your system and make it uniquely yours!** 🚀
