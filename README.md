Streamlit app demo using EPA ECHO Air Emissions dataset

must use Python 3.9. use venv.
pip install -r requirements.txt
streamlit run app.py

To run on AWS using ECR+ECS:
Create an ECR repository. Build the Docker image and upload according to the push commands.
Create an ECS cluster. Use Amazon Linux 2023 (Python 3.9)
Create a Task Definition. Use the bridge option for networking and map port 8501

Git pre-hooks:
run install-git-hooks.sh to install git hooks
If you're having issues on a Mac with zsh operation not permitted errors:
    .git/hooks % ls -l@ pre-push
    xattr -d com.apple.quarantine pre-push