# Mini Project 3  
#### INF601 - Advanced Programming in Python  
#### Matt Hogan  
  
## Description
This is a basic to-do list application built with Flask.
## Running the App
1. Clone or download repository  
2. Create and activate a virtual environment  
```
python -m venv .venv  
.\.venv\Scripts\activate.bat
```  
3. Install necessary packages  
```
pip install -r requirements.txt
```
4. Initialize the databases  
```
flask --app todo_list init-db
```
5. Run the flask app  
```
flask --app todo_list run
```
6. Navigate to `http://127.0.0.1:5000/` in a browser
