# Fixing the Semester Sequence Issue

This document provides instructions for fixing the incorrect semester sequence in the LabClass database.

## The Problem

The semester sequence in the database is currently incorrect:
1. 1st Sem 2025-2026
2. 2nd Sem 2025-2026
3. Summer 2026
4. 1st Sem 2027-2028 (incorrect)
5. 2nd Sem 2027-2028 (incorrect)
6. Summer 2028 (incorrect)

The correct sequence should be:
1. 1st Sem 2025-2026
2. 2nd Sem 2025-2026
3. Summer 2026
4. 1st Sem 2026-2027
5. 2nd Sem 2026-2027
6. Summer 2027

The issue occurred in the `check_and_add_next_academic_year_semesters` function in the backend code, which was incorrectly incrementing years when creating the next set of semesters.

## The Solution

This issue has been fixed in two ways:

1. **Code Fix**: The `check_and_add_next_academic_year_semesters` function in `routes/schedules.py` has been updated to correctly increment the academic years when creating new semesters.

2. **Data Fix**: A script has been created to update the existing incorrect semester entries in the database.

## How to Fix

### Step 1: Update the Database

Run the provided script to update the existing incorrect semester entries:

```bash
cd backend
python fix_semester_sequence.py
```

This script will:
- Update "1st Sem 2027-2028" to "1st Sem 2026-2027" (ID: 55)
- Update "2nd Sem 2027-2028" to "2nd Sem 2026-2027" (ID: 56)
- Update "Summer 2028" to "Summer 2027" (ID: 57)

### Step 2: Verify the Fix

You can verify that the semester creation logic now works correctly by running the test script:

```bash
cd backend
python test_semester_increment.py
```

The test should show that when a Summer semester is approved, the next academic year's semesters are created with the correct year sequence.

### Step 3: Restart the Application

Restart the backend server to ensure the updated code is running:

```bash
cd backend
# If using a virtual environment, activate it first
# source venv/bin/activate  (Unix) or venv\Scripts\activate (Windows)
python main.py
```

## Future Prevention

The code fix ensures that future semester sequences will be generated correctly. The academic year progression will now follow this pattern:

- After "Summer 2026" comes "1st Sem 2026-2027"
- After "Summer 2027" comes "1st Sem 2027-2028"

And so on, maintaining the correct academic year progression.

## Technical Details

The issue was in the year calculation:

**Before (Incorrect):**
```python
current_year = int(semester_name.split()[-1])  # e.g., 2026 from "Summer 2026"
next_year = current_year + 1  # 2027
academic_year = f"{next_year}-{next_year+1}"  # "2027-2028"
```

**After (Correct):**
```python
current_year = int(semester_name.split()[-1])  # e.g., 2026 from "Summer 2026"
next_year_start = current_year  # 2026
next_year_end = current_year + 1  # 2027
academic_year = f"{next_year_start}-{next_year_end}"  # "2026-2027"
```

This ensures that after "Summer 2026", the next academic year is "1st Sem 2026-2027" rather than skipping to "1st Sem 2027-2028". 