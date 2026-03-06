# Database Cleanup Utility - EduFlow

This utility helps maintain database integrity by removing orphaned records.

## 🎯 What It Does

The cleanup utility removes:
- **Orphaned Students**: Students whose school doesn't exist
- **Orphaned Teachers**: Teachers whose school doesn't exist  
- **Orphaned Subjects**: Subjects whose school doesn't exist
- **Orphaned Grade Levels**: Grade levels whose school doesn't exist

It also cleans up related records like:
- Student grades and attendance (for orphaned students)
- Teacher subject assignments and class assignments (for orphaned teachers)

## 📋 Usage

### Option 1: Command Line Script

Run the Python script directly:

```bash
# Full cleanup (all types)
python cleanup_database.py

# Or specify what to clean
python cleanup_database.py students      # Only orphaned students
python cleanup_database.py teachers      # Only orphaned teachers
python cleanup_database.py subjects      # Only orphaned subjects
python cleanup_database.py grade-levels  # Only orphaned grade levels
python cleanup_database.py all           # Same as running without arguments
```

**⚠️ Important:** The script will ask for confirmation before deleting anything.

### Option 2: API Endpoint

Use the admin API endpoint:

```bash
POST /api/admin/cleanup/orphaned-data
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN

{
  "type": "all"  // or "students", "teachers", "subjects", "grade-levels"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/api/admin/cleanup/orphaned-data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"type": "students"}'
```

## 🔍 Response Format

The API returns detailed information about what was deleted:

```json
{
  "success": true,
  "message": "تم تنظيف 15 سجل يتيم بنجاح",
  "message_en": "Successfully cleaned up 15 orphaned records",
  "results": {
    "students_deleted": 10,
    "teachers_deleted": 3,
    "subjects_deleted": 2,
    "grade_levels_deleted": 0,
    "details": [
      "Deleted 10 orphaned students",
      "Cleaned up 45 grade records and 23 attendance records",
      "Deleted 3 orphaned teachers",
      "Cleaned up 8 subject assignments and 5 class assignments",
      "Deleted 2 orphaned subjects"
    ]
  }
}
```

## 🛡️ Safety Features

- ✅ Requires admin authentication
- ✅ Shows what will be deleted before deletion (CLI version)
- ✅ Asks for confirmation (CLI version)
- ✅ Uses transactions (rollback on error)
- ✅ Logs all deletions to console
- ✅ Returns detailed report of what was deleted

## 📊 When to Use

Run this cleanup when:
- You see students/teachers appearing that don't belong to any school
- After manually deleting schools from the database
- After bulk imports/exports that might have failed
- As part of regular database maintenance (monthly recommended)

## ⚠️ Warnings

1. **Backup First**: Always backup your database before running cleanup
2. **Read Carefully**: Review what will be deleted before confirming
3. **Test Environment**: Test in a development environment first
4. **Foreign Keys**: The cleanup respects foreign key constraints

## 🔧 Troubleshooting

### "Failed to connect to database"
- Check your `.env` file has correct database credentials
- Ensure MySQL/MariaDB server is running
- Verify database exists

### "No orphaned data found"
- This is good! It means your database is clean
- No action needed

### Cleanup takes too long
- Large databases may take time
- The utility processes records in batches
- Consider running during off-peak hours

## 📝 Example Output

```
============================================================
🧹 EDUFLOW DATABASE CLEANUP UTILITY
============================================================

This utility will check for and remove orphaned records:
   • Students without schools
   • Teachers without schools
   • Subjects without schools
   • Grade levels without schools

============================================================

⚠️  WARNING: This will permanently delete data. Continue? (yes/no): yes

============================================================
Starting cleanup process...
============================================================

[1/4] Checking orphaned students...

📋 Found 5 orphaned students:
   - ID: 123, Name: أحمد محمد, Code: STU-001, School ID: 999
   - ID: 124, Name: سارة علي, Code: STU-002, School ID: 999
   ...

⚠️  Do you want to delete these orphaned students? (yes/no): yes

✅ Cleanup completed successfully!
   🗑️  Deleted students: 5
   🗑️  Deleted grade records: 25
   🗑️  Deleted attendance records: 15

[2/4] Checking orphaned teachers...
✅ No orphaned teachers found

...

============================================================
✅ CLEANUP COMPLETED
   Total records deleted: 5
============================================================
```

## 🆘 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify database connection
3. Review database logs
4. Contact system administrator

---

**Last Updated**: March 6, 2026  
**Version**: 1.0
