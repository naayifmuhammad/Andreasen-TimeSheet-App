

## Project Name

Andreasen‐ TimeSheet‐ App

### Download and Installation

1. **Clone the repository**

   You can download the project using Git. Open your terminal and run:

   ```bash
   git clone <repository_url>
   ```

   Alternatively, you can download the zip file and extract it to your desired location.

2. **Setup Virtual Environment**

   Navigate into the project directory and create a virtual environment:

   ```bash
   cd project_directory
   virtualenv env
   ```

   Activate the virtual environment:

   - On Windows:

     ```bash
     .\env\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source env/bin/activate
     ```

3. **Install Dependencies**

   Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Application**

   Run the Django development server:

   ```bash
   python manage.py runserver
   ```

   The application will be accessible at `http://127.0.0.1:8000/`.

### Project Overview

This project provides a management system where administrators can create and manage employees, projects, and track project-related information. Employees can log time against projects created by administrators.

### Default Credentials

Upon starting the application, you can sign up using the following default superuser credentials:

- **Username:** admin
- **Password:** Andreasen

If you can't seem to make it work, just do the following:

Open terminal. Use the following commands.

python manage.py createsuperuser

[Enter the information the interface asks you. You can use those credentials to log into the app then.]

### Features

- **Admin Dashboard:** Create and manage employees, projects, and view project details.
- **Employee Portal:** Log time against projects created by administrators.

---