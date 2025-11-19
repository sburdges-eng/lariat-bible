# PROJECT RULES

## BEO Bible System Specifications and Standards

**Version**: 1.0
**Last Updated**: 2025-11-19
**Purpose**: Define all rules, formulas, and standards for the BEO Bible system

---

## Table of Contents

1. [System Purpose & Structure](#system-purpose--structure)
2. [10-Step Core Workflow](#10-step-core-workflow)
3. [Invoice Template Specifications](#invoice-template-specifications)
4. [Formula Details & Examples](#formula-details--examples)
5. [Kitchen Sheet Specifications](#kitchen-sheet-specifications)
6. [Recipe Scaling Rules](#recipe-scaling-rules)
7. [Ordering & Inventory Rules](#ordering--inventory-rules)
8. [Pricing & Financial Rules](#pricing--financial-rules)
9. [Production Schedule Template](#production-schedule-template)
10. [Quality Control Checklists](#quality-control-checklists)
11. [Version Control System](#version-control-system)
12. [Metrics & KPIs](#metrics--kpis)
13. [Common Issues & Solutions](#common-issues--solutions)
14. [Training Requirements](#training-requirements)
15. [Maintenance Schedule](#maintenance-schedule)
16. [Quick Reference Guides](#quick-reference-guides)

---

## System Purpose & Structure

### Purpose
The BEO Bible is a comprehensive banquet event order management system designed to:
- Streamline event booking through execution
- Automate pricing and cost calculations
- Generate kitchen prep sheets automatically
- Ensure consistent quality and profitability
- Track metrics and improve operations

### Core Components
1. **Invoice Template** (Excel): Client-facing pricing and kitchen prep
2. **Recipe Database** (Word): All recipes with yields and scaling
3. **Ingredient Master List** (Excel): Complete ingredient database
4. **Order Guides** (Excel): Vendor products and pricing
5. **Documentation** (Markdown): System rules and workflows

### File Organization
```
Templates/ → Master files (never edit)
Reference/ → Recipe book, order guides (read-only)
Active_Events/ → Current events in progress
Archive/ → Completed events by month/year
Analytics/ → Reports and metrics tracking
Documentation/ → This file and other guides
```

---

## 10-Step Core Workflow

### Step 1: Event Booking (30-60 min)
- Collect client contact information
- Determine event date, time, location
- Discuss guest count and event type
- Review menu options and preferences
- Confirm budget and minimum spend
- Collect deposit (typically 50%)

### Step 2: Create Invoice (15-30 min)
- Copy Invoice Template to event folder
- Enter client information
- Add menu item selections
- Verify VLOOKUP formulas populate prices
- Check calculations (subtotal, tax, fee)
- Validate minimum spend requirement
- Save as v1

### Step 3: Client Approval (1-3 days)
- Send invoice to client for review
- Track any revision requests
- Create v2, v3, etc. for changes
- Document all changes in NOTES.txt
- Obtain final approval
- Collect remaining payment

### Step 4: Generate Kitchen Sheet (30-45 min)
- Review Sheet 2 (auto-populated from Sheet 1)
- Assign prep days (Thu/Fri/Sat)
- Add task details for each item
- Specify plating requirements
- Note service timing
- Print for kitchen team

### Step 5: Calculate Ingredients (1-2 hours)
- List all menu items from invoice
- Look up recipes in Recipe Book
- Scale each recipe to quantity needed
- Compile all ingredients into master list
- Combine duplicate ingredients
- Add 10% buffer for waste/safety
- Check existing inventory

### Step 6: Create Production Schedule (30-60 min)
- Assign tasks to specific days:
  - Thursday: Long braises, stocks, sauces
  - Friday: Main prep, butchering, marinades
  - Saturday: Final prep, assembly, service
- Estimate time for each task
- Assign staff members
- Build in buffer time
- Print and post in kitchen

### Step 7: Order Ingredients (1-2 hours)
- Reference Order Guides for products
- Create orders by vendor:
  - Shamrock Foods (dry goods, proteins)
  - Sysco (specialty items)
  - Local suppliers (fresh produce)
- Submit orders for Thursday delivery
- Confirm delivery times
- Plan Friday fresh pickup if needed

### Step 8: Receive & Inventory (1-2 hours)
- Check deliveries against orders
- Verify quantities and quality
- Note any substitutions or shortages
- Update inventory system
- Proper storage immediately
- Document any issues

### Step 9: Prep & Production (3 days)
**Thursday**:
- Receive deliveries
- Start long-cooking items
- Make stocks, sauces, brines
- Butcher large proteins
- Check quality and timing

**Friday**:
- Continue prep work
- Marinate proteins
- Prepare vegetables
- Make cold items
- Set up mise en place
- Final quality check

**Saturday**:
- Early morning final prep
- Transport to venue if off-site
- Final cooking and assembly
- Plating and presentation
- Service execution
- Breakdown and cleanup

### Step 10: Event Execution (4-8 hours)
- Arrive at venue 2-4 hours before service
- Setup and final prep
- Cook-to-order items
- Plate and serve according to timeline
- Maintain quality throughout service
- Client satisfaction check
- Breakdown and cleanup
- Post-event debrief

---

## Invoice Template Specifications

### Sheet 1: Client Invoice

#### Structure
```
Column A: Item Name (Text)
Column B: Price Per Person (Formula: =VLOOKUP(A3,$F$3:$G$55,2,FALSE))
Column C: Quantity (Number - guest count or item count)
Column D: Total Price (Formula: =B3*C3)

Rows 1-2: Header with business info
Rows 3-20: Line items (menu selections)
Row 21: Subtotal (Formula: =SUM(D3:D20))
Row 22: Sales Tax 8.15% (Formula: =D21*0.0815)
Row 23: Service Fee 20% (Formula: =D21*0.20)
Row 24: GRAND TOTAL (Formula: =D21+D22+D23)
Row 26: Minimum Spend Validator

Columns F-G (hidden or right side): Price Lookup Table
  F3:F55 = Item Names (must match Column A exactly)
  G3:G55 = Prices (numbers)
```

#### Business Information Section
```
Row 1: [Business Name]
        [Address]
        [Phone] | [Email]

Row 2: BANQUET EVENT ORDER INVOICE

Client Information (above line items):
Name: __________________
Event Date: __________________
Guest Count: __________________
Event Type: __________________
Contact: __________________
```

#### Price Lookup Table (Columns F:G)
Must contain exactly 53 menu items:
- Appetizers (10 items)
- Salads (5 items)
- Entrees (20 items)
- Sides (10 items)
- Desserts (8 items)

**Critical**: Item names in Column F must match Column A exactly (case-sensitive) for VLOOKUP to work.

#### Calculation Formulas

**Price Lookup** (Column B):
```excel
=VLOOKUP(A3,$F$3:$G$55,2,FALSE)
```
Finds item name in A3, looks up price in F:G table, returns price from column 2

**Line Total** (Column D):
```excel
=B3*C3
```
Multiplies price per person by quantity

**Subtotal** (D21):
```excel
=SUM(D3:D20)
```
Sums all line item totals

**Sales Tax** (D22):
```excel
=D21*0.0815
```
Applies 8.15% tax to subtotal

**Service Fee** (D23):
```excel
=D21*0.20
```
Applies 20% service fee to subtotal

**Grand Total** (D24):
```excel
=D21+D22+D23
```
Adds subtotal, tax, and service fee

**Minimum Spend Validator** (D26):
```excel
=IF(D24<500,"BELOW MINIMUM - Increase items or quantities",PASS - $"&TEXT(D24-500,"0.00")&" above minimum")
```
Checks if total meets $500 minimum

---

## Formula Details & Examples

### VLOOKUP Price Formula

**Purpose**: Automatically populate item prices based on name

**Formula**:
```excel
=VLOOKUP(A3,$F$3:$G$55,2,FALSE)
```

**Parameters**:
- `A3`: Item name to look up
- `$F$3:$G$55`: Price table range (absolute reference)
- `2`: Return value from column 2 of table
- `FALSE`: Exact match required

**Example**:
```
A3: "Grilled Chicken Breast"
F10: "Grilled Chicken Breast"
G10: 18.50

Result in B3: 18.50
```

**Common Errors**:
- `#N/A`: Item name doesn't match exactly
- `#REF!`: Price table range is incorrect
- `#VALUE!`: Lookup value contains errors

**Troubleshooting**:
1. Check spelling and spacing of item name
2. Verify price table range includes all items
3. Ensure no hidden characters or extra spaces
4. Confirm item exists in price table

### Percentage Calculations

**Tax Calculation** (8.15%):
```excel
=D21*0.0815
```

**Service Fee** (20%):
```excel
=D21*0.20
```

**Total Markup** (28.15%):
```excel
=D21*1.2815
```
(Combines tax 8.15% + service fee 20%)

### Conditional Formatting

**Minimum Spend Check**:
```excel
=IF(D24<500,"BELOW MINIMUM","MEETS MINIMUM")
```

**Food Cost Warning** (if implementing):
```excel
=IF((Actual_Cost/D21)>0.35,"HIGH FOOD COST - Review","OK")
```

---

## Kitchen Sheet Specifications

### Sheet 2: Kitchen Prep Sheet

#### Purpose
Auto-generate kitchen prep instructions from client invoice

#### Structure
```
Column A: Item Name (Formula: =Invoice!A3)
Column B: Quantity (Formula: =Invoice!C3)
Column C: Prep Day (Manual: Thu/Fri/Sat)
Column D: Tasks (Manual: Specific prep instructions)
Column E: Plating (Manual: How to plate/present)
Column F: Time Served (Manual: When to serve)
Column G: Notes (Manual: Special instructions)
```

#### Linking Formulas

**Item Name** (Column A):
```excel
=Invoice!A3
```
Links directly to Sheet 1, Column A

**Quantity** (Column B):
```excel
=Invoice!C3
```
Links directly to Sheet 1, Column C

**Auto-Update**: When invoice is updated, kitchen sheet updates automatically

#### Manual Entry Fields

**Prep Day** (Column C):
- Options: Thursday, Friday, Saturday
- Guidelines:
  - Thursday: Long braises, stocks, anything 24+ hours
  - Friday: Main prep, most items
  - Saturday: Final prep, fresh items only

**Tasks** (Column D):
- Specific action items
- Example: "Trim and season brisket, sear, braise in oven 275°F for 6 hours"
- Reference recipe book for details

**Plating** (Column E):
- Presentation instructions
- Example: "Slice against grain, 4oz portion, top with jus, garnish with crispy onions"

**Time Served** (Column F):
- Service timing
- Example: "6:30 PM - Hot, passed immediately"

**Notes** (Column G):
- Special considerations
- Allergen info
- Client preferences
- Holding instructions

---

## Recipe Scaling Rules

### Standard Scaling Process

1. **Identify Base Yield**
   - Most recipes written for 10 servings
   - Note yield in recipe header
   - Verify portion sizes

2. **Calculate Scale Factor**
   ```
   Scale Factor = Needed Servings ÷ Recipe Yield
   Example: 60 servings ÷ 10 servings = 6x
   ```

3. **Scale Ingredients**
   ```
   New Amount = Original Amount × Scale Factor
   Example: 2 lbs chicken × 6 = 12 lbs chicken
   ```

4. **Add Safety Buffer**
   ```
   Final Amount = New Amount × 1.10
   Example: 12 lbs × 1.10 = 13.2 lbs
   ```

5. **Round to Purchasing Units**
   ```
   Example: 13.2 lbs rounds to 14 lbs (typical pack size)
   ```

### Scaling Considerations

**Items that Scale Linearly**:
- Proteins (meats, chicken, fish)
- Vegetables (most)
- Starches (rice, pasta, potatoes)
- Most garnishes

**Items that DON'T Scale Linearly**:
- Seasonings (scale by 75% for large batches)
- Salt (taste and adjust, don't just multiply)
- Acids (vinegar, lemon - scale by 80%)
- Thickeners (reduce percentage for large batches)
- Cooking times (don't simply multiply)

### Batch Cooking Rules

**Proteins**:
- Maximum batch size: 30-40 lbs for even cooking
- Multiple batches better than one huge batch
- Maintain temperature between batches

**Sauces & Braises**:
- Can scale up to 3-4x easily
- Beyond 4x, make multiple batches
- Taste and adjust seasoning at end

**Baked Items**:
- Don't change oven temperature
- Adjust baking time carefully
- Rotate pans for even cooking

---

## Ordering & Inventory Rules

### Ordering Timeline

**7 Days Before Event**:
- Finalize ingredient list
- Check inventory for existing stock
- Create preliminary orders

**5 Days Before Event** (Monday for Saturday event):
- Confirm final guest count
- Adjust ingredient quantities
- Submit orders to vendors

**3 Days Before Event** (Thursday):
- Receive Shamrock delivery (dry goods, proteins)
- Receive Sysco delivery (specialty items)
- Verify quantities and quality

**1 Day Before Event** (Friday):
- Pick up fresh produce from local suppliers
- Purchase any forgotten items
- Final inventory check

### Vendor Guidelines

**Shamrock Foods**:
- Order by: Monday 5 PM for Thursday delivery
- Minimum order: $150
- Typical delivery window: 6 AM - 2 PM
- Use for: Proteins, dry goods, dairy, frozen
- Payment terms: Net 30

**Sysco**:
- Order by: Tuesday noon for Thursday delivery
- Minimum order: $200
- Typical delivery window: 8 AM - 12 PM
- Use for: Specialty items, seafood, gourmet products
- Payment terms: Net 30

**Local Suppliers**:
- Order: 2 days in advance
- Pick up: Friday morning
- Use for: Fresh produce, artisan products, bakery
- Payment: At time of pickup

### Inventory Management

**Pre-Event Inventory**:
1. Check existing stock for common items:
   - Oils, vinegars, seasonings
   - Flour, sugar, dry goods
   - Frozen stocks and sauces
2. Deduct from order quantities
3. Note items running low for next order

**Post-Event Inventory**:
1. Account for leftover ingredients
2. Store properly or repurpose
3. Update inventory records
4. Calculate actual usage vs. ordered

**Stock Rotation**:
- First in, first out (FIFO)
- Label all items with receive date
- Check expiration dates weekly
- Use older stock first

---

## Pricing & Financial Rules

### Pricing Structure

**Base Pricing Formula**:
```
Menu Item Price = (Ingredient Cost ÷ Target Food Cost %) ÷ Guest Count
Target Food Cost = 30-35%
```

**Example**:
```
Ingredient cost for 50 servings = $500
Target food cost = 33%
Base price = $500 ÷ 0.33 = $1,515
Price per person = $1,515 ÷ 50 = $30.30
```

### Invoice Calculations

**Subtotal**:
```
Sum of all menu items × quantities
```

**Sales Tax** (8.15%):
```
Subtotal × 0.0815
```

**Service Fee** (20%):
```
Subtotal × 0.20
Covers: Labor, delivery, setup, service, cleanup
```

**Grand Total**:
```
Subtotal + Tax + Service Fee
= Subtotal × 1.2815
```

### Minimum Requirements

**Minimum Event Total**: $500
- Below $500 not profitable
- Minimum covers labor and overhead
- Encourage clients to add items or guests

**Minimum Deposit**: 50% of total
- Due at booking to hold date
- Non-refundable
- Applied to final invoice

**Final Payment**: Remaining 50%
- Due 72 hours before event
- Required before prep begins
- No prep without payment

### Profitability Targets

**Food Cost**: 30-35% of subtotal
```
Target: $100 subtotal = $30-35 ingredient cost
```

**Labor Cost**: 15-20% of subtotal
```
Included in 20% service fee
```

**Total Costs**: 45-55% of subtotal
```
Leaves 45-55% for overhead and profit
```

**Event Profit Margin**: 40-50%
```
After all costs, target 40-50% net profit
```

### Pricing Adjustments

**Peak Season** (May-October):
- Consider 10-15% premium
- Higher demand justifies pricing
- Communicate value to clients

**Off-Season** (November-April):
- May offer 5-10% discount
- Fills slow periods
- Builds client base

**Large Events** (100+ guests):
- May reduce per-person slightly
- Economies of scale
- Still maintain margin targets

**Complex Menus**:
- Higher labor = higher service fee
- Can charge 25% service fee vs. 20%
- Premium plating adds value

---

## Production Schedule Template

### Thursday Schedule

**Morning (8 AM - 12 PM)**:
- [ ] Receive Shamrock delivery
- [ ] Receive Sysco delivery
- [ ] Check all items against order
- [ ] Proper storage of perishables
- [ ] Begin long-cooking items:
  - Start braises (6-8 hour cook time)
  - Make stocks if needed
  - Prepare marinades

**Afternoon (12 PM - 5 PM)**:
- [ ] Continue braised items
- [ ] Make sauces and reductions
- [ ] Butcher large proteins
- [ ] Prepare items that improve overnight:
  - Brines
  - Rubs
  - Marinades
- [ ] Quality check braised items
- [ ] Cooling and storage

**End of Day**:
- [ ] All braises complete and properly stored
- [ ] Tomorrow's prep list finalized
- [ ] Kitchen cleaned and organized
- [ ] Temperature logs recorded

### Friday Schedule

**Morning (8 AM - 12 PM)**:
- [ ] Pick up fresh produce
- [ ] Organize mise en place
- [ ] Prep vegetables:
  - Wash, peel, cut
  - Par-cook if needed
  - Proper storage
- [ ] Continue protein prep:
  - Trim and portion
  - Season as needed
  - Marinate if required

**Afternoon (12 PM - 6 PM)**:
- [ ] Prepare cold items:
  - Salads
  - Dressings
  - Garnishes
- [ ] Cook items that hold well:
  - Starches
  - Par-cooked vegetables
  - Warm sauces
- [ ] Set up service equipment
- [ ] Pack for transport if off-site
- [ ] Final ingredient check

**End of Day**:
- [ ] All prep complete except final cooking
- [ ] Everything properly stored
- [ ] Saturday timeline confirmed
- [ ] Staff assignments finalized

### Saturday Schedule (Service Day)

**Early Morning** (Varies by event time):
- [ ] Arrive 4 hours before service
- [ ] Transport to venue if needed
- [ ] Setup kitchen/serving area
- [ ] Equipment check
- [ ] Start final prep items

**Pre-Service** (2 hours before):
- [ ] Cook to-order items
- [ ] Reheat braised items properly
- [ ] Finish sauces
- [ ] Plate samples for approval
- [ ] Final quality check
- [ ] Service area setup

**Service** (Event time):
- [ ] Maintain food temperature
- [ ] Consistent plating and portions
- [ ] Monitor timing of courses
- [ ] Adjust as needed
- [ ] Client check-in

**Post-Service**:
- [ ] Breakdown and cleanup
- [ ] Pack equipment
- [ ] Inventory leftovers
- [ ] Transport back to kitchen
- [ ] Final cleanup

**Debrief**:
- [ ] Team discussion
- [ ] Note successes
- [ ] Document improvements
- [ ] Update NOTES.txt

---

## Quality Control Checklists

### Pre-Event Quality Check

**Invoice Review**:
- [ ] All menu items spelled correctly
- [ ] Prices populated correctly via VLOOKUP
- [ ] Quantities match guest count
- [ ] Calculations accurate
- [ ] Client information complete
- [ ] Payment received

**Kitchen Sheet Review**:
- [ ] Items match invoice exactly
- [ ] Quantities match invoice
- [ ] Prep days assigned appropriately
- [ ] Tasks clear and specific
- [ ] Plating instructions detailed
- [ ] Timing noted

**Ingredient Orders**:
- [ ] All ingredients calculated
- [ ] 10% buffer added
- [ ] Inventory checked and deducted
- [ ] Orders submitted on time
- [ ] Delivery times confirmed
- [ ] Special items noted

### During Prep Quality Check

**Thursday**:
- [ ] Deliveries complete and verified
- [ ] Braises seasoned properly
- [ ] Cooking temperatures correct
- [ ] Timing on track
- [ ] Proper storage
- [ ] Equipment functioning

**Friday**:
- [ ] Fresh items picked up
- [ ] Vegetables prepped correctly
- [ ] Proteins portioned accurately
- [ ] Cold items fresh and safe
- [ ] Everything properly labeled
- [ ] Ready for transport

**Saturday**:
- [ ] All items accounted for
- [ ] Equipment working properly
- [ ] Setup complete and clean
- [ ] Food temperatures safe
- [ ] Plating consistent
- [ ] Service timing accurate

### Post-Event Quality Review

**Food Quality**:
- [ ] Temperature maintained
- [ ] Presentation consistent
- [ ] Portion sizes accurate
- [ ] Client satisfaction
- [ ] Minimal waste

**Operational Efficiency**:
- [ ] Timeline followed
- [ ] Staff performed well
- [ ] Equipment adequate
- [ ] No major issues
- [ ] Improvements identified

**Financial Performance**:
- [ ] Food cost within target
- [ ] Labor hours as estimated
- [ ] Waste minimal
- [ ] Profit margin achieved

---

## Version Control System

### File Versioning

**Template Files**:
- Master templates: Version 1.0
- Update only when system changes
- Document updates in this file
- Backup before any changes

**Event Invoices**:
- Start with v1: `Invoice_Client_Date_v1.xlsx`
- Each revision: v2, v3, v4, etc.
- Never overwrite previous versions
- Note changes in NOTES.txt

**Documentation**:
- Date all updates in header
- Note what changed
- Keep change log at bottom
- Archive old versions

### Change Documentation

**In NOTES.txt** for each event:
```
CHANGE LOG:
[Date] v1: Initial invoice created
[Date] v2: Changed appetizer from X to Y per client request
[Date] v3: Increased guest count from 50 to 60
[Date] FINAL: Approved and paid
```

**In System Documentation**:
```
CHANGE LOG:
2025-11-19: Initial system creation v1.0
[Future dates]: Document any rule changes
```

---

## Metrics & KPIs

### Financial Metrics

**Event Revenue**:
- Track per event
- Compare to estimates
- Note payment timing

**Food Cost Percentage**:
```
(Actual Ingredient Cost ÷ Subtotal) × 100
Target: 30-35%
```

**Profit Margin**:
```
((Total - All Costs) ÷ Total) × 100
Target: 40-50%
```

**Average Event Size**:
- Revenue per event
- Guests per event
- Items per event

### Operational Metrics

**Prep Time Accuracy**:
- Estimated vs. actual
- Track by item type
- Improve estimates

**Ingredient Accuracy**:
- Ordered vs. used
- Waste percentage
- Inventory efficiency

**On-Time Performance**:
- Service start times
- Prep completion
- Delivery reliability

### Client Metrics

**Satisfaction Scores**:
- Post-event survey
- 1-5 scale rating
- Comments and feedback

**Repeat Rate**:
```
(Repeat Clients ÷ Total Clients) × 100
Target: >40%
```

**Referral Rate**:
```
(Referred Clients ÷ Total Clients) × 100
Target: >30%
```

---

## Common Issues & Solutions

### Invoice Issues

**Problem**: VLOOKUP returns #N/A
**Solution**: Check exact spelling in Column A vs. Column F

**Problem**: Tax calculation wrong
**Solution**: Verify formula is `=D21*0.0815`

**Problem**: Total seems low
**Solution**: Check quantities in Column C

### Kitchen Sheet Issues

**Problem**: Items not populating
**Solution**: Check link formulas `=Invoice!A3`

**Problem**: Wrong quantities
**Solution**: Verify link to correct invoice version

### Prep Issues

**Problem**: Running out of ingredients
**Solution**: Verify 10% buffer was added

**Problem**: Running behind schedule
**Solution**: Prioritize critical items, adjust timeline

**Problem**: Food quality concerns
**Solution**: Reference recipes, check temperatures

---

## Training Requirements

### New Staff Training

**Week 1: System Overview**
- Review all documentation
- Understand file structure
- Shadow experienced staff

**Week 2: Invoice Creation**
- Practice creating invoices
- Learn VLOOKUP troubleshooting
- Client communication

**Week 3: Kitchen Operations**
- Kitchen sheet interpretation
- Production scheduling
- Recipe scaling

**Week 4: Full Event**
- Complete event from start to finish
- With supervision
- Debrief and feedback

### Ongoing Training

**Monthly**: Review metrics and improvements
**Quarterly**: System updates and refinements
**Annually**: Comprehensive review and certification

---

## Maintenance Schedule

### Daily
- Update active event folders
- Check ingredient deliveries
- Quality checks during prep

### Weekly
- Review upcoming events
- Update pricing if needed
- Inventory audit

### Monthly
- Archive completed events
- Update analytics
- Review metrics

### Quarterly
- System review
- Documentation updates
- Process improvements

### Annually
- Comprehensive system audit
- Price list overhaul
- Recipe book review

---

## Quick Reference Guides

### Excel Formulas Quick Reference

```excel
VLOOKUP: =VLOOKUP(lookup_value, table_array, col_index, FALSE)
SUM: =SUM(range)
IF: =IF(condition, value_if_true, value_if_false)
PERCENTAGE: =amount * 0.XX
```

### Common Calculations

**Food Cost %**: `(Cost ÷ Subtotal) × 100`
**Profit Margin**: `((Revenue - Cost) ÷ Revenue) × 100`
**Scale Factor**: `Needed ÷ Recipe Yield`
**With Buffer**: `Amount × 1.10`

### Important Numbers

- Sales Tax: 8.15%
- Service Fee: 20%
- Min Event: $500
- Target Food Cost: 30-35%
- Target Margin: 40-50%
- Safety Buffer: 10%

---

## Change Log

```
2025-11-19: Initial PROJECT_RULES.md v1.0 created
            - Complete system specifications
            - All formulas and rules documented
            - Ready for implementation
```

---

**End of PROJECT_RULES.md**
