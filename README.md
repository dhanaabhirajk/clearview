# Clearview Project

The Clearview project is a chatGLM that resolve any doubts or questions you have about any Flipkart product.. This README provides instructions on how to run the project in both production and development environments using a Google Colab notebook.

## Getting Started

1. Clone the Git Repository
   - Open the provided Google Colab notebook: [Clearview Colab Notebook](https://colab.research.google.com/drive/10g_w8x9amh4pIkJricsJz0aoqNHtZ0Yt#scrollTo=X9o8qmZduBzj).
   - Clone the Git repository inside the notebook to access the necessary project files.

2. Uploading Secrets
   - After cloning the Git repository, you need to upload the `secrets.json` file to the `clearview` folder in the project directory.
   - **Note:** Make sure to include the correct configurations in the `secrets.json` file.

3. Create a collection `chats` to store the chat_history

## Running in Production Environment

If you want to run the Clearview project in the production environment, follow these steps:

1. Upload Secrets
- After cloning the repository, create a `secrets.json` file in the root directory with the following content:
     ```json
     {
         "MONGODB_URI": "your_mongodb_uri_here",
         "DB_NAME": "you_db_name",
         "NGROK_AUTH_TOKEN": "your_ngrok_auth_token_here",
         "SECRET_KEY": "your_secret_key_here",
         "STATUS_ENV": "PRODUCTION",
         "MAX_LENGTH": 32000,
         "TOP_P": 0.7,
         "TEMPERATURE": 0.95,
         "PORT": 5000
     }
     ```
Configure `secrets.json`
   - Set `"STATUS_ENV": "PRODUCTION"` in the `secrets.json` file to indicate the production environment.

2. Install Dependencies
   - For Python versions 3.10.11 and lower, install the `v-requirements.txt` file:
     ```
     !pip install -r v-requirements.txt
     ```

   - For Python versions above 3.10.11, install the `requirements.txt` file:
     ```
     !pip install -r requirements.txt
     ```

   - Additionally, install the large dependencies for deployment using the `l-requirements.txt` file:
     ```
     !pip install -r l-requirements.txt
     ```


3. Execute the Project
   - Run the necessary cells in the Colab notebook to execute the Clearview project in production mode.
   - The ngrok is used to generate public url for public access and is available in the output

Uploading the secrets.json is enough to run the colab notebook and others are available as code.

## Running in Development Environment

If you want to test the Clearview project in a local development environment, follow these steps:


1. Upload Secrets
- After cloning the repository, create a `secrets.json` file in the root directory with the following content:
     ```json
     {
         "MONGODB_URI": "your_mongodb_uri_here",
         "DB_NAME": "you_db_name",
         "NGROK_AUTH_TOKEN": "your_ngrok_auth_token_here",
         "SECRET_KEY": "your_secret_key_here",
         "STATUS_ENV": "DEV",
         "MAX_LENGTH": 32000,
         "TOP_P": 0.7,
         "TEMPERATURE": 0.95,
         "PORT": 5000
     }
     ```
     Configure `secrets.json`
   - Set `"STATUS_ENV": "DEV"` in the `secrets.json` file to indicate the development environment.

2. Install Dependencies
   - Install only the `requirements.txt` file:
     ```
     !pip install -r requirements.txt
     ```

3. Execute the Project
   - Change directory to clearview
   ```
   cd clearview
   ```
   - Run the web application
   ```
   python main.py
   ```

## Note

- Ensure that you have uploaded the correct `secrets.json` file with appropriate configurations for either production or development environments.
- Make sure you have the required Python version installed before running the installation commands.
- In local development mode `DEV`, the chatGLM and its dependencies are not installed


Happy coding!
