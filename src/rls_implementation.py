"""
Row Level Security (RLS) Implementation for InsightHub
Task #17: Implement and Test Row Level Security for Profiles and Interactions Tables

This script implements RLS policies to ensure users can only access and modify their own data.
"""

import sys
import os
from typing import Optional
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reddit_weekly_top.supabase_client import supabase_client

# Load environment variables
load_dotenv()

class RLSImplementer:
    """Implements Row Level Security policies for profiles and interactions tables."""
    
    def __init__(self):
        """Initialize the RLS implementer with Supabase client."""
        self.client = supabase_client.get_client()
        if not self.client:
            raise ValueError("Supabase client not available. Check SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
    
    def print_sql_for_manual_execution(self):
        """Print all SQL commands for manual execution in Supabase SQL Editor."""
        print("\n" + "="*80)
        print("🔧 SQL COMMANDS FOR MANUAL EXECUTION")
        print("="*80)
        print("Copy and paste these commands into your Supabase SQL Editor:")
        print("\n-- 1. Enable RLS on profiles table")
        print("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;")
        
        print("\n-- 2. Create profiles table policies")
        print("""
-- Policy for users to select only their own profile
CREATE POLICY profiles_select_policy ON profiles
FOR SELECT USING (auth.uid() = id);

-- Policy for users to update only their own profile  
CREATE POLICY profiles_update_policy ON profiles
FOR UPDATE USING (auth.uid() = id);

-- Policy for users to insert their own profile
CREATE POLICY profiles_insert_policy ON profiles
FOR INSERT WITH CHECK (auth.uid() = id);
""")
        
        print("\n-- 3. Enable RLS on interactions table")
        print("ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;")
        
        print("\n-- 4. Create interactions table policies")
        print("""
-- Policy for users to select only their own interactions
CREATE POLICY interactions_select_policy ON interactions
FOR SELECT USING (auth.uid() = user_id);

-- Policy for users to insert only their own interactions
CREATE POLICY interactions_insert_policy ON interactions
FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy for users to update only their own interactions
CREATE POLICY interactions_update_policy ON interactions
FOR UPDATE USING (auth.uid() = user_id);

-- Policy for users to delete only their own interactions
CREATE POLICY interactions_delete_policy ON interactions
FOR DELETE USING (auth.uid() = user_id);
""")
        
        print("\n-- 5. Verify RLS is enabled (optional)")
        print("""
-- Check RLS status
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('profiles', 'interactions');

-- Check created policies
SELECT schemaname, tablename, policyname, roles, cmd
FROM pg_policies 
WHERE tablename IN ('profiles', 'interactions');
""")
        
        print("\n" + "="*80)
        print("After executing these commands, run the test script to verify the implementation.")
    
    def test_connection(self) -> bool:
        """Test the Supabase connection."""
        try:
            print("🔗 Testing Supabase connection...")
            
            # Try to fetch some basic info
            result = self.client.table('profiles').select('id').limit(1).execute()
            
            if hasattr(result, 'data'):
                print("✅ Supabase connection successful!")
                return True
            else:
                print("❌ Connection test failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False
    
    def run_implementation(self):
        """Run the RLS implementation process."""
        print("🚀 Starting RLS Implementation for InsightHub")
        print("Task #17: Implement and Test Row Level Security")
        print("=" * 60)
        
        # Test connection
        if not self.test_connection():
            print("❌ Cannot proceed without valid Supabase connection")
            return False
        
        print("\n📝 RLS IMPLEMENTATION PLAN")
        print("-" * 30)
        print("1. Enable RLS on 'profiles' table")
        print("2. Create policies for profiles (SELECT, UPDATE, INSERT)")
        print("3. Enable RLS on 'interactions' table") 
        print("4. Create policies for interactions (SELECT, INSERT, UPDATE, DELETE)")
        print("5. Verify implementation")
        
        # Since we need elevated permissions for DDL operations,
        # we'll provide the SQL commands for manual execution
        self.print_sql_for_manual_execution()
        
        print("\n🎯 NEXT STEPS:")
        print("1. Execute the SQL commands above in Supabase SQL Editor")
        print("2. Run the test script: python src/test_rls_policies.py")
        print("3. Verify policies in Supabase Dashboard: Authentication → Policies")
        
        return True

def main():
    """Main function to run RLS implementation."""
    try:
        implementer = RLSImplementer()
        implementer.run_implementation()
        
        print("\n✅ RLS Implementation guide completed!")
        print("Please execute the SQL commands manually and then run tests.")
            
    except Exception as e:
        print(f"❌ Failed to initialize RLS implementation: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that SUPABASE_URL and SUPABASE_ANON_KEY are set in .env file")
        print("2. Verify Supabase project is accessible")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main() 