AI-Powered HR Leave Management SystemThis is a sophisticated, conversational AI agent designed to streamline the entire leave management process within an organization. It provides a user-friendly chat interface for Employees, Supervisors, and HR personnel to manage leave requests, approvals, and status checks efficiently.🌟 Key FeaturesConversational AI Agent: Built with LangChain and LangGraph, powered by OpenAI's gpt-4o, allowing users to interact using natural language.Role-Based Access Control: Secure authentication system using JWT for three distinct roles:Employee: Can request leave and check the status of their requests.Supervisor: Can view, approve, or reject leave requests from their direct reports.HR Manager: Can view all requests, provide final approval, and manage the overall process.Full Leave Lifecycle Management: The agent intelligently handles the complete workflow:Employee submits a request.Agent forwards it to the correct Supervisor.Supervisor approves/rejects the request.Agent forwards it to HR for final approval.All parties are notified of status changes.Persistent Data Storage: Uses MongoDB to store all user data, leave requests, and their statuses.Interactive Frontend: A clean and responsive chat interface built with Streamlit.🛠️ Tech StackBackend: FlaskFrontend: StreamlitDatabase: MongoDBAI/LLM Framework: LangChain, LangGraphLLM Provider: OpenAI (gpt-4o)Authentication: JWT (PyJWT)🚀 Getting StartedFollow these instructions to set up and run the project on your local machine.PrerequisitesBefore you begin, ensure you have the following installed and configured:Python 3.9+MongoDB Atlas Account: Create a free cluster on MongoDB Atlas and get your Connection String.OpenAI Account: Get your API Key from the OpenAI Platform.Git (for cloning the repository).⚙️ Installation & Setup1. Clone the Repository:git clone <your-repository-url>
cd <repository-folder-name>
2. Create and Activate a Virtual Environment:This keeps your project dependencies isolated.# Create the virtual environment
python -m venv venv

# Activate it (on Windows)
.\venv\Scripts\activate

# Activate it (on macOS/Linux)
source venv/bin/activate
3. Install Dependencies:Install all the required Python libraries from the requirements.txt file.pip install -r requirements.txt
4. Set Up Environment Variables:Create a file named .env in the root directory of the project.Copy the content from .env.example (if available) or add the following lines, replacing the placeholder values with your actual keys and credentials.# .env file
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
MONGO_URI="mongodb+srv://<username>:<password>@<your-cluster-url>/"
MONGO_DB_NAME="hr_system"
SECRET_KEY="your_strong_secret_key_for_jwt"
5. Set Up Initial Database Data:Run the setup script to create the initial test users (Employee, Supervisor, HR) in your MongoDB database.python setup_initial_data.py
▶️ Running the ApplicationYou need to run the backend and frontend simultaneously in two separate terminals.1. Start the Backend Server (Flask):Open your first terminal, activate the virtual environment, and run:python run.py
Keep this terminal running. It will handle all the application logic.2. Start the Frontend Application (Streamlit):Open a second terminal, activate the virtual environment, and run:streamlit run frontend/chat_ui.py
This will automatically open a new tab in your web browser with the application's login page.You can now use the application!🧪 Test UsersUse the following credentials to log in and test the different roles:Employee:Username: employee_kamalPassword: emp_passwordSupervisor:Username: supervisor_johnPassword: sup_passwordHuman Resources (HR):Username: hr_managerPassword: hr_password