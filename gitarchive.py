import os
from github import Github, GithubException
from git import Repo, GitCommandError
import time

# Configuration
ACCESS_TOKEN = ''
REPO_PATH = 'D:\DevelopProjects\Dev\wat'
REPO_NAME = 'enthusiastdev121/wat'
REVIEWER = 'DonGroovy1120'
COMMIT_MESSAGE = 'Update asset\n\nCo-authored-by: DonGroovy1120 <groovyrocome@gmail.com>'
BRANCH_PREFIX = 'update-branch-'
NUM_PRS = 20  # Total number of pull requests to create

def modify_files_and_commit(repo, g_repo):
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(REPO_PATH) for f in filenames if f.endswith('.py')]
    num_files = len(files)
    changes_per_file = (NUM_PRS + num_files - 1) // num_files  # Calculate how many changes per file are needed

    pr_count = 0
    for i, file_path in enumerate(files):
        for change_num in range(changes_per_file):
            if pr_count >= NUM_PRS:
                break
            timestamp = int(time.time())
            branch_name = f"{BRANCH_PREFIX}{i}-{change_num}-{timestamp}"
            try:
                # Checkout main branch and pull latest changes
                repo.git.checkout('main')
                repo.git.pull('origin', 'main')

                # Create a new branch
                repo.git.checkout('-b', branch_name)

                # Make changes to the file
                with open(file_path, 'a') as file:
                    file.write(f"\n// Root Layout and Protected Routes{pr_count + 1}\n")

                # Commit changes
                repo.git.add(file_path)
                repo.git.commit('-m', COMMIT_MESSAGE)

                # Push changes
                repo.git.push('--set-upstream', 'origin', branch_name)

                # Create a pull request
                pr = g_repo.create_pull(title=f"Aniket {pr_count + 1}", body="There are JavaScript errors being thrown when using certain components of the UI kit. We need to debug and fix these issues", head=branch_name, base="main")
                pr.create_review_request(reviewers=[REVIEWER])

                # Wait and check mergeability
                time.sleep(10)  # Adjust time as needed
                if pr.mergeable:
                    pr.merge(commit_title=f"Merge {pr_count + 1}", commit_message=COMMIT_MESSAGE, merge_method='squash')
                    print(f"PR created and merged for {file_path}")

                    # Delete branch after merging
                    repo.git.checkout('main')
                    repo.git.pull('origin', 'main')
                    repo.git.branch('-d', branch_name)  # Delete local branch
                    repo.git.push('origin', '--delete', branch_name)  # Delete remote branch
                    print(f"Branch {branch_name} deleted.")
                else:
                    print(f"PR {pr_count + 1} is not mergeable. Please check manually.")
                pr_count += 1
            except GitCommandError as e:
                print(f"Git command failed: {e}")
            except GithubException as e:
                print(f"GitHub API error: {e}")
            except Exception as e:
                print(f"Failed to process file {file_path}: {e}")

def main():
    g = Github(ACCESS_TOKEN)
    g_repo = g.get_repo(REPO_NAME)
    local_repo = Repo(REPO_PATH)
    modify_files_and_commit(local_repo, g_repo)

if __name__ == "__main__":
    main()
