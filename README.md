Streamlit app demo using EPA ECHO Air Emissions dataset

pip install -r requirements.txt
streamlit run app.py

To run on AWS:
Create an ECR repository. Build the Docker image and upload according to the push commands.
Create an ECS cluster. Use Amazon Linux 2023 (Python 3.9)
Create a Task Definition. Use the bridge option for networking and map port 8501
