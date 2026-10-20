# IEEE Tracker

A web-based checklist and event management system designed to help IEEE Student Branch societies organize events, manage tasks, and track progress through a centralized dashboard.

## Overview

IEEE Tracker provides a structured way for different IEEE societies to manage event-related activities. Each society can create events, follow predefined checklists, update task completion status, and add remarks. A dedicated Secretary dashboard helps monitor progress across societies.

## Features

- **Multi-Society Management:** Separate workspaces for IEEE societies.
- **Event Management:** Create and manage events with categorized event types.
- **Dynamic Checklists:** Generate structured checklists based on event configurations.
- **Task Tracking:** Update task completion status and monitor progress.
- **Remarks and Comments:** Record updates and communicate event-related information.
- **Secretary Dashboard:** View and track progress across participating societies.
- **Secure Authentication:** Password-based login with hashed password storage.
- **Responsive Interface:** Access the application through a web browser.

## Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Authentication:** Flask sessions and Werkzeug password hashing
- **Deployment:** PythonAnywhere

## Project Structure

```text
ieee-tracker/
├── app.py
├── checklists.py
├── requirements.txt
├── set_password.py
├── README.md
└── static/
    ├── index.html
    ├── style.css
    ├── app.js
    └── logo.png
```

The application may also create an `instance/` directory to store its SQLite database when running locally.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or later
- pip
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your GitHub username and repository name.

### 2. Create a Virtual Environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux or macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Set a unique secret key for Flask sessions before starting the application.

**Windows PowerShell:**

```powershell
$env:SECRET_KEY = "your-long-random-secret"
```

**Linux or macOS:**

```bash
export SECRET_KEY="your-long-random-secret"
```

For production, configure environment variables through your hosting provider instead of storing secrets in source code.

### 5. Run the Application

```bash
python app.py
```

If the application starts successfully, open the local URL displayed in the terminal, typically:

```text
http://127.0.0.1:5000
```

## Deployment

The application can be deployed on a compatible Python hosting platform, such as PythonAnywhere.

General deployment steps:

1. Upload or connect the GitHub repository.
2. Configure the Python environment and install dependencies.
3. Set the correct project path in the WSGI configuration.
4. Configure the Flask secret key using an environment variable.
5. Ensure the SQLite database path is writable and appropriate for the hosting environment.
6. Reload the web application and verify authentication and dashboard functionality.

**Database note:** SQLite data stored on temporary hosting storage may be lost after restarts or redeployments. For reliable long-term use, configure persistent storage or migrate to a managed database.

## Security Notes

- Never commit passwords, secret keys, credentials files, or database files containing sensitive information.
- Use environment variables for production secrets.
- Passwords should be stored as hashes, not as plaintext.
- Use HTTPS when accessing the deployed application.
- Give each society access only to its authorized workspace.
- Back up the database regularly when using persistent storage.

## Future Enhancements

Potential improvements include:

- Persistent cloud database integration
- Automated progress reports
- Event deadlines and reminders
- Exportable reports
- Role-based access control
- Improved analytics and progress visualizations

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch to your fork.
5. Open a pull request describing your changes.

## License

A license has not yet been specified. Add a license file if you intend to define how others may use, modify, and distribute this project.

---

**IEEE Tracker** — Simplifying event coordination and checklist management for IEEE societies.
