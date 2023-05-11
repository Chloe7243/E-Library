# E-Library

How to run using Windows OS:

1. Make Sure you have Python 3.1 and above installed
   Command: ```$ python --version```
2. Open the command prompt, go to the project folder and create a Virtual Environment to run the application
   Command: ```$ python -m venv venv```
3. Activate the Virtual Environment
    Command: ```$ venv\Scripts\activate```
4. Install the required packages
    Command: ```$ pip install -r requirements.txt```
5. Create the `PASSKEY` environment variable (this will serve as the app's secret key and you'll also use it create admins on the application)
    Command: ```$ setx PASSKEY 'your-pass-key'```
    where `your-pass-key` is whatever string you want
6. Run the application
    Command: ```$ python main.py```