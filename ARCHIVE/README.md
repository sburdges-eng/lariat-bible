# Archive Directory

## Completed Events Repository

This directory contains all completed events, organized by year and month. These archives serve as:
- Historical reference for repeat clients
- Data source for analytics and reporting
- Training materials for new staff
- Proof of successful executions

## Directory Structure

```
ARCHIVE/
└── 2025/
    ├── 01_January/
    ├── 02_February/
    ├── 03_March/
    ├── 04_April/
    ├── 05_May/
    ├── 06_June/
    ├── 07_July/
    ├── 08_August/
    ├── 09_September/
    ├── 10_October/
    ├── 11_November/
    └── 12_December/
```

## Archiving Process

### When to Archive
Move events to archive when:
- Event has been completed
- Final payment received
- All photos organized
- NOTES.txt finalized
- No pending follow-up

### How to Archive
```bash
# From ACTIVE_EVENTS directory
mv ClientLastName_MMDD ../ARCHIVE/2025/MM_MonthName/
```

Examples:
```bash
mv Johnson_0307 ../ARCHIVE/2025/03_March/
mv CorporateXYZ_1215 ../ARCHIVE/2025/12_December/
```

## Archive Contents

Each archived event folder should contain:
```
ClientName_EventDate/
├── Invoice_ClientName_Date_FINAL.xlsx  (final approved version)
├── Production_Schedule.xlsx
├── Ingredient_Orders.xlsx
├── NOTES.txt (complete with final metrics)
└── Photos/
    ├── prep_day1.jpg
    ├── prep_day2.jpg
    ├── setup.jpg
    ├── plated_dish1.jpg
    ├── event_service.jpg
    └── ...
```

## Archive Checklist

Before archiving, ensure:
- [ ] Final invoice is saved (rename to include "FINAL")
- [ ] All payments are recorded
- [ ] Production schedule is complete
- [ ] Ingredient orders are documented
- [ ] NOTES.txt includes:
  - [ ] Final guest count
  - [ ] Total revenue
  - [ ] Food cost and percentage
  - [ ] Labor hours
  - [ ] Profit margin
  - [ ] Lessons learned
  - [ ] Client feedback
- [ ] Photos are organized and named clearly
- [ ] Any special requests or customizations are noted

## Using Archived Events

### For Repeat Clients
1. Navigate to previous event folder
2. Review menu selections and pricing
3. Check NOTES.txt for preferences and feedback
4. Copy successful elements to new event

### For Similar Events
1. Search archives by event type (wedding, corporate, etc.)
2. Review production schedules for timing
3. Reference ingredient calculations for scaling
4. Learn from lessons learned notes

### For Training
1. Show new staff completed event examples
2. Review photos for plating standards
3. Use production schedules as templates
4. Demonstrate proper documentation

### For Analytics
1. Extract data from NOTES.txt files
2. Compile revenue and cost information
3. Analyze seasonal trends
4. Identify popular menu items
5. Calculate average profit margins

## Maintenance

### Monthly Review
At end of each month:
- Verify all completed events are archived
- Check that all folders are complete
- Update event count and revenue totals
- Note any trends or patterns

### Quarterly Audit
Every 3 months:
- Review folder organization
- Ensure photos are properly stored
- Verify data completeness
- Archive to external backup

### Annual Tasks
At year end:
- Compile annual statistics
- Create year-end summary report
- Backup entire year's archive
- Review storage needs

## Archive Statistics

### 2025 Events (To Date)
- **Total Events**: 0
- **Total Revenue**: $0
- **Average Event Size**: 0 guests
- **Most Popular Items**: TBD
- **Repeat Clients**: 0

_(Update these numbers monthly)_

### Monthly Breakdown 2025
| Month | Events | Revenue | Avg Guest Count |
|-------|--------|---------|-----------------|
| Jan   | 0      | $0      | 0               |
| Feb   | 0      | $0      | 0               |
| Mar   | 0      | $0      | 0               |
| Apr   | 0      | $0      | 0               |
| May   | 0      | $0      | 0               |
| Jun   | 0      | $0      | 0               |
| Jul   | 0      | $0      | 0               |
| Aug   | 0      | $0      | 0               |
| Sep   | 0      | $0      | 0               |
| Oct   | 0      | $0      | 0               |
| Nov   | 0      | $0      | 0               |
| Dec   | 0      | $0      | 0               |

## Backup Protocol

### Local Backups
- Weekly backup to external drive
- Cloud backup monthly
- Keep 2 years of archives readily accessible
- Archive older years to deep storage

### Disaster Recovery
- Critical documents backed up in multiple locations
- Invoice copies stored separately
- Photo backups maintained independently
- Client contact information duplicated in CRM

---

For analytics and reporting, see [ANALYTICS/README.md](../ANALYTICS/README.md)
