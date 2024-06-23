

## Project Name

Andreasen‐ TimeSheet‐ App

### Download and Installation

### 1. Clone the Repository
To get a copy of the project, you need to clone the repository from GitHub.


git clone https://github.com/naayifmuhammad/Andreasen-TimeSheet-App.git
cd Andreasen-TimeSheet-App


   Alternatively, you can download the zip file and extract it to your desired location.

2. **Setup Virtual Environment**

   Navigate into the project directory and create a virtual environment:

   cd Andreasen-TimeSheet-App
   virtualenv env

   Activate the virtual environment:

   - On Windows:

     .\env\Scripts\activate

   - On macOS/Linux:


     source env/bin/activate

3. **Install Dependencies**

   Install the required Python packages:

   pip install -r requirements.txt


4. **Start the Application**

   Before starting the project, don't forget to execute the following commands:

   # python manage.py makemigrations
   # python manage.py migrate

   Run the Django development server:

   # python manage.py runserver
   

   The application will be accessible at `http://127.0.0.1:8000/`.

### Project Overview

This project provides a management system where administrators can create and manage employees, projects, and track project-related information. Employees can log time against projects created by administrators.

### Default Credentials

Upon starting the application, Open terminal. Use the following commands.

# python manage.py createsuperuser

[Enter the information the interface asks you. You can use those credentials to log into the app then.]

### Features

- **Admin Dashboard:** Create and manage employees, projects, and view project details.
- **Employee Portal:** Log time against projects created by administrators.

---

Updating the Project
1. Fetch and Merge Changes
To update your local copy with the latest changes from the repository, use the following commands:

# git fetch origin
# git merge origin/main

Alternatively, you can pull the latest changes directly:

# git pull origin main


# License
# This project is licensed under the MIT License. See the LICENSE file for details.
