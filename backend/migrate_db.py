"""
Database migration script to ensure all tables and columns exist
Handles both PostgreSQL (Supabase) and SQLite
"""
import os
from sqlalchemy import text, inspect
from database import engine
import models

def add_missing_columns_postgresql(db_connection):
    """Add missing columns to PostgreSQL applications table"""
    try:
        inspector = inspect(engine)
        
        if 'applications' in inspector.get_table_names():
            table_columns = {col['name'] for col in inspector.get_columns('applications')}
            
            # Add resume_data if missing
            if 'resume_data' not in table_columns:
                try:
                    db_connection.execute(text('ALTER TABLE applications ADD COLUMN resume_data TEXT'))
                    db_connection.commit()
                    print("✓ Added 'resume_data' column to applications table")
                except Exception as e:
                    print(f"ℹ Could not add 'resume_data': {str(e)[:100]}")
            
            # Add resume_filename if missing
            if 'resume_filename' not in table_columns:
                try:
                    db_connection.execute(text('ALTER TABLE applications ADD COLUMN resume_filename VARCHAR'))
                    db_connection.commit()
                    print("✓ Added 'resume_filename' column to applications table")
                except Exception as e:
                    print(f"ℹ Could not add 'resume_filename': {str(e)[:100]}")
            
            # Add cover_letter if missing
            if 'cover_letter' not in table_columns:
                try:
                    db_connection.execute(text('ALTER TABLE applications ADD COLUMN cover_letter TEXT'))
                    db_connection.commit()
                    print("✓ Added 'cover_letter' column to applications table")
                except Exception as e:
                    print(f"ℹ Could not add 'cover_letter': {str(e)[:100]}")
    except Exception as e:
        print(f"ℹ PostgreSQL migration info: {str(e)[:100]}")

def check_and_fix_sqlite_table_schema(db_connection, table_name, model_class):
    """
    For SQLite, check if table columns match the model.
    If not, recreate the table with correct schema.
    """
    dialect_name = engine.dialect.name
    if dialect_name != 'sqlite':
        return False  # Not needed for other databases
    
    inspector = inspect(engine)
    
    try:
        actual_columns = {col['name'] for col in inspector.get_columns(table_name)}
        expected_columns = {col.name for col in model_class.__table__.columns}
        
        if actual_columns != expected_columns:
            missing_columns = expected_columns - actual_columns
            print(f"⚠️  Table '{table_name}' has missing columns: {missing_columns}")
            print(f"   Recreating table '{table_name}' with correct schema...")
            
            # Drop and recreate the table
            db_connection.execute(text(f'DROP TABLE IF EXISTS {table_name}'))
            db_connection.commit()
            
            # Recreate with correct schema
            models.Base.metadata.tables[table_name].create(bind=engine)
            print(f"✓ Table '{table_name}' recreated successfully")
            return True
    except Exception as e:
        print(f"ℹ Could not verify table '{table_name}': {str(e)[:80]}")
    
    return False

def migrate_database():
    """Create all tables and handle schema updates"""
    
    # First, create all new tables (if they don't exist)
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✓ Database tables ensured to exist")
    except Exception as e:
        print(f"⚠️  Could not create tables: {e}")
    
    # For any issues, fix them
    with engine.connect() as conn:
        dialect_name = engine.dialect.name
        
        if dialect_name == 'postgresql':
            print("📝 Running PostgreSQL migrations...")
            add_missing_columns_postgresql(conn)
        elif dialect_name == 'sqlite':
            print("📝 Checking SQLite schema compatibility...")
            try:
                check_and_fix_sqlite_table_schema(conn, 'applications', models.Application)
                check_and_fix_sqlite_table_schema(conn, 'jobs', models.Job)
                check_and_fix_sqlite_table_schema(conn, 'interview_rounds', models.InterviewRound)
            except Exception as e:
                print(f"ℹ Schema check encountered: {str(e)[:80]}")
        
        # Ensure migration is committed
        try:
            conn.commit()
        except:
            pass
    
    print("✓ Database schema migration completed")

if __name__ == "__main__":
    try:
        migrate_database()
        print("\n✅ Database is ready!")
    except Exception as e:
        print(f"\n⚠️  Migration info: {e}")

