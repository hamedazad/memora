#!/usr/bin/env python3
"""
Script to set up GitLab remote for Memora project
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Memora GitLab Setup Script")
    print("=" * 50)
    
    # Check if we're in a git repository
    success, stdout, stderr = run_command("git status")
    if not success:
        print("❌ Error: Not in a git repository")
        sys.exit(1)
    
    print("✅ Git repository found")
    
    # Show current remotes
    print("\n📡 Current remotes:")
    success, stdout, stderr = run_command("git remote -v")
    if success:
        print(stdout)
    
    # Get GitLab repository URL
    print("\n🔗 GitLab Setup")
    print("Please provide your GitLab repository URL.")
    print("Example: https://gitlab.com/yourusername/memora.git")
    print("Or: git@gitlab.com:yourusername/memora.git")
    
    gitlab_url = input("\nEnter your GitLab repository URL: ").strip()
    
    if not gitlab_url:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)
    
    # Add GitLab as a new remote
    print(f"\n➕ Adding GitLab as remote 'gitlab'...")
    success, stdout, stderr = run_command(f'git remote add gitlab "{gitlab_url}"')
    
    if not success:
        print(f"❌ Error adding remote: {stderr}")
        sys.exit(1)
    
    print("✅ GitLab remote added successfully")
    
    # Push to GitLab
    print("\n📤 Pushing to GitLab...")
    print("This will push all branches and tags to GitLab")
    
    # Push all branches
    success, stdout, stderr = run_command("git push gitlab --all")
    if not success:
        print(f"❌ Error pushing branches: {stderr}")
        sys.exit(1)
    
    # Push all tags
    success, stdout, stderr = run_command("git push gitlab --tags")
    if not success:
        print(f"❌ Error pushing tags: {stderr}")
        sys.exit(1)
    
    print("✅ Successfully pushed to GitLab!")
    
    # Show updated remotes
    print("\n📡 Updated remotes:")
    success, stdout, stderr = run_command("git remote -v")
    if success:
        print(stdout)
    
    print("\n🎉 Setup complete!")
    print("Your Memora project is now available on GitLab.")
    print("You can continue using 'git push gitlab' to push future changes.")

if __name__ == "__main__":
    main()
