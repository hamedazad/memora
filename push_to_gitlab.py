#!/usr/bin/env python3
"""
Simple script to push Memora to GitLab
"""

import subprocess
import sys

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Memora GitLab Push Script")
    print("=" * 50)
    
    print("Current Git status:")
    success, stdout, stderr = run_command("git status --short")
    if success:
        print(stdout)
    
    print("\nCurrent remotes:")
    success, stdout, stderr = run_command("git remote -v")
    if success:
        print(stdout)
    
    print("\n📋 Instructions to push to GitLab:")
    print("1. Create a new repository on GitLab.com")
    print("2. Copy the repository URL (HTTPS or SSH)")
    print("3. Run the following commands:")
    print()
    print("   # Add GitLab as a new remote")
    print("   git remote add gitlab YOUR_GITLAB_URL")
    print()
    print("   # Push all branches and tags")
    print("   git push gitlab --all")
    print("   git push gitlab --tags")
    print()
    print("Example GitLab URLs:")
    print("   HTTPS: https://gitlab.com/yourusername/memora.git")
    print("   SSH:   git@gitlab.com:yourusername/memora.git")
    print()
    
    # Ask if user wants to proceed
    response = input("Do you have your GitLab repository URL ready? (y/n): ").strip().lower()
    
    if response == 'y':
        gitlab_url = input("Enter your GitLab repository URL: ").strip()
        
        if not gitlab_url:
            print("❌ No URL provided. Exiting.")
            sys.exit(1)
        
        # Add GitLab remote
        print(f"\n➕ Adding GitLab as remote 'gitlab'...")
        success, stdout, stderr = run_command(f'git remote add gitlab "{gitlab_url}"')
        
        if not success:
            print(f"❌ Error adding remote: {stderr}")
            sys.exit(1)
        
        print("✅ GitLab remote added successfully")
        
        # Push to GitLab
        print("\n📤 Pushing to GitLab...")
        
        # Push all branches
        success, stdout, stderr = run_command("git push gitlab --all")
        if not success:
            print(f"❌ Error pushing branches: {stderr}")
            print("You may need to authenticate with GitLab first.")
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
        
    else:
        print("\n📝 Manual Setup Instructions:")
        print("1. Go to https://gitlab.com and create a new repository")
        print("2. Copy the repository URL")
        print("3. Run: git remote add gitlab YOUR_URL")
        print("4. Run: git push gitlab --all")
        print("5. Run: git push gitlab --tags")

if __name__ == "__main__":
    main()
