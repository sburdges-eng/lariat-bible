# Active Events Directory

## Current Events in Progress

This directory contains all events currently being planned, prepped, or executed. Each event gets its own folder with all related documents.

## Folder Structure

```
ACTIVE_EVENTS/
└── ClientName_EventDate/
    ├── Invoice_ClientName_Date_v1.xlsx
    ├── Invoice_ClientName_Date_v2.xlsx (if revisions needed)
    ├── Production_Schedule.xlsx
    ├── Ingredient_Orders.xlsx
    ├── NOTES.txt
    └── Photos/ (event day photos)
```

## Naming Convention

**Folder Name Format**: `ClientLastName_MMDD`
- Examples:
  - `Johnson_0915` (Johnson wedding, September 15)
  - `CorporateXYZ_1103` (Corporate event, November 3)
  - `Smith_1225` (Smith holiday party, December 25)

**File Naming**:
- `Invoice_ClientName_Date_v1.xlsx` - Initial invoice
- `Invoice_ClientName_Date_v2.xlsx` - Revised invoice (if needed)
- `Production_Schedule.xlsx` - Thu/Fri/Sat prep schedule
- `Ingredient_Orders.xlsx` - Compiled ingredient needs
- `NOTES.txt` - Running log of changes and decisions

## Workflow

### Step 1: Create Event Folder
```bash
mkdir ClientLastName_MMDD
cd ClientLastName_MMDD
```

### Step 2: Copy Invoice Template
```bash
cp ../../TEMPLATES/Invoice_Template_MASTER.xlsx Invoice_ClientName_Date_v1.xlsx
```

### Step 3: Fill Out Invoice
- Enter client contact information
- Add menu item selections
- Verify pricing calculations
- Review minimum spend
- Save and send to client

### Step 4: Client Approval
- Track revisions (v2, v3, etc.)
- Document changes in NOTES.txt
- Keep all versions for reference

### Step 5: Generate Kitchen Documents
- Use Kitchen Prep Sheet (Sheet 2 of invoice)
- Create production schedule
- Calculate ingredient needs
- Generate vendor orders

### Step 6: Track Event Progress
- Update NOTES.txt daily
- Add photos from prep and event
- Document any issues or lessons learned

## Event Lifecycle

### Active Status (Keep in this folder while):
- Invoice is being finalized
- Production is being planned
- Prep is in progress
- Event is within 1 week

### Archive Ready (Move to ARCHIVE when):
- Event is completed
- Final invoice is paid
- Photos are organized
- Notes are complete

## Moving to Archive

After event completion:
```bash
mv ClientLastName_MMDD ../ARCHIVE/2025/MM_MonthName/
```

Example:
```bash
mv Johnson_0915 ../ARCHIVE/2025/09_September/
```

## NOTES.txt Template

```
EVENT: Client Name - Date
CONTACT: Phone/Email
GUEST COUNT: XX
EVENT TYPE: Wedding/Corporate/Private Party

TIMELINE:
- [Date]: Initial booking, deposit received
- [Date]: Menu finalized, final invoice sent
- [Date]: Full payment received
- [Date]: Prep begins
- [Date]: Event executed

CHANGES:
- [Date]: Changed appetizer from X to Y per client request
- [Date]: Increased guest count from 50 to 60
- [Date]: Added dessert option

LESSONS LEARNED:
- What went well
- What to improve
- Time estimates accuracy
- Any issues encountered

FINAL METRICS:
- Total Revenue: $XXX
- Food Cost: $XXX (XX%)
- Labor Hours: XX
- Profit Margin: XX%
```

## Best Practices

1. **Create folders immediately** upon booking
2. **Update NOTES.txt** after every change
3. **Save invoice versions** never overwrite
4. **Take photos** during prep and service
5. **Archive promptly** after completion (within 1 week)
6. **Review metrics** before archiving

## Current Active Events

_(List current events here or reference separately)_

- [ ] ClientName_Date - Status: [Booked/Planning/Prep/Service]
- [ ] ClientName_Date - Status: [Booked/Planning/Prep/Service]

---

For detailed workflow, see [DOCUMENTATION/WORKFLOW.md](../DOCUMENTATION/WORKFLOW.md)
