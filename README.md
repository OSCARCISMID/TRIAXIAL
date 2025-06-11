# TRIAXIAL

Real-time plotting tool for triaxial tests.

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set the `SECRET_KEY` environment variable for Flask security:
   ```bash
   export SECRET_KEY=your-secret-key
   ```
4. (Optional) Set the `LOG_LEVEL` environment variable or pass `--log-level`
   when running the application to adjust logging verbosity (e.g. `DEBUG`,
   `INFO`).
5. (Optional) Control debug mode using the `DEBUG` environment variable or the
   `--debug`/`--no-debug` command-line flags when starting the application.
6. Run the application:
   ```bash
   python app.py
   ```

## Usage

Place test data files in the `data/` directory. Open the
application in your browser at `http://localhost:5000` and select
a real-time file or load static files to visualize their results.
