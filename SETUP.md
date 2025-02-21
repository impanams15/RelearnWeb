# Setup Guide

## Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

1. Clone the repository
```bash
git clone https://github.com/QuaddropicHQ/RelearnWeb.git
cd RelearnWeb
```

2. Create and activate virtual environment (optional but recommended)
Linux and macOS
```bash
python -m venv venv
source venv/bin/activate
```
On Windows
```bash
venv\Scripts\activate`
```

3. Install required packages
```bash
pip install -r requirements.txt
```

## Environment Variables

Enter the required ENV variables by clicking on AI Settings.

## Running the Application

1. Start the Streamlit app
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

## Development Settings

- Debug mode can be enabled by setting `DEBUG=True` in the `.env` file
- For local development, use `localhost` as host

## Troubleshooting

If you encounter any issues:
1. Verify all environment variables are set correctly
2. Ensure all dependencies are installed
3. Check the application logs for error messages