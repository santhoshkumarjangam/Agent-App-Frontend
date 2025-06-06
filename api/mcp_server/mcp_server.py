from mcp.server.fastmcp import FastMCP
# from fastmcp import FastMCP

mcp = FastMCP("mcp_server")

# TO-DO
def get_db_connection():
    import sqlite3
    connection = sqlite3.connect("todo.db")
    return connection

@mcp.tool()
def list_db_tables(dummy:str):

    """
    List all tables in the database

    Args:
        dummy:str - This parameter is not used by the function but helps ensure schema generation. A non-empty string is expected

    Returns:
        Dict: A dictionary with keys 'success' (bool), 'message' (str) and 'tables' (List[Str]) containing the table names if successful
    """
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        tables = [row[0] for row in cursor.fetchall()]
        connection.close()

        return {
            'success': True,
            'message': 'tables listed successfully',
            'tables' : tables
        }

    except Exception as e:
        return {
            'success': False,
            'message': 'failed to list tables',
            'tables' : None
        }

@mcp.tool()
def get_table_schema(table_name: str):
    """
    Get the schema of a specified table.

    Args:
        table_name (str): Name of the table to fetch schema for.

    Returns:
        Dict: A dictionary containing 'success' (bool), 'message' (str), and 'schema' (List[Dict]) if successful.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")

        schema = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
        connection.close()

        return {
            'success': True,
            'message': 'Schema fetched successfully',
            'schema': schema
        }

    except Exception as e:
        return {
            'success': False,
            'message': 'Failed to fetch schema',
            'schema': None
        }

@mcp.tool()
def query_db_table(table_name: str, columns: str, condition: str):
    """
    Query data from a specified table.

    Args:
        table_name (str): Name of the table to query.
        columns (str): Comma-separated column names to fetch.
        condition (str, optional): WHERE condition for the query.

    Returns:
        Dict: A dictionary containing 'success' (bool), 'message' (str), and 'data' (List[Tuple]) if successful.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"SELECT {columns} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        cursor.execute(query)

        data = cursor.fetchall()
        connection.close()

        return {
            'success': True,
            'message': 'Data fetched successfully',
            'data': data
        }

    except Exception as e:
        return {
            'success': False,
            'message': 'Failed to fetch data',
            'data': None
        }

@mcp.tool()
def insert_data(table_name: str, data: dict):
    """
    Insert data into a specified table.

    Args:
        table_name (str): Name of the table to insert data into.
        data (dict): Dictionary where keys are column names and values are corresponding values.

    Returns:
        Dict: A dictionary containing 'success' (bool) and 'message' (str).
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        values = tuple(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        connection.commit()
        connection.close()

        return {
            'success': True,
            'message': 'Data inserted successfully'
        }

    except Exception as e:
        return {
            'success': False,
            'message': 'Failed to insert data'
        }

@mcp.tool()
def delete_data(table_name: str, condition: str):
    """
    Delete data from a specified table.

    Args:
        table_name (str): Name of the table to delete data from.
        condition (str): WHERE condition for deletion.

    Returns:
        Dict: A dictionary containing 'success' (bool) and 'message' (str).
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = f"DELETE FROM {table_name} WHERE {condition}"
        cursor.execute(query)
        connection.commit()
        connection.close()

        return {
            'success': True,
            'message': 'Data deleted successfully'
        }

    except Exception as e:
        return {
            'success': False,
            'message': 'Failed to delete data'
        }


# NOTEPAD
@mcp.tool()
def add_note(note_content: str) -> dict:
    """
    Add a new note by appending it to the notepad file.

    Args:
        note_content (str): Content of the note to add.

    Returns:
        dict with key status and a value message.
    """
    try:
        with open("C:/Users/Santhosh/Desktop/AGENT APPLICATION/api/mcp_server/notepad.txt", "a") as f:
            f.write(note_content.strip() + "\n")
        return {"status": "successful", "message": "Note added successfully."}
    except Exception as e:
        return {"status": "unsuccessful", "message": "failed adding note."}

@mcp.tool()
def read_notes() -> dict:
    """
    Read and return all notes from the notepad file.

    Returns:
        dict: Status and data containing all notes or message if empty.
    """
    try:
        with open("C:/Users/Santhosh/Desktop/AGENT APPLICATION/api/mcp_server/notepad.txt", "r") as f:
            notes = f.read().strip() or "No notes found."
        return {"status": "successful", "data": notes}
    except Exception as e:
        return {"status": "unsuccessful", "data": ""}


# DIRECTORY TRAVERSER
@mcp.tool()
def get_largest_file(base_path: str) -> dict:
    """
    Find the largest file inside the given directory (including subdirectories).

    Args:
        base_path (str): The root directory path to search.

    Returns:
        dict: Status and data with largest file name, path, and size in bytes,
              or error message if path invalid or empty.
    """
    import os

    if not os.path.exists(base_path):
        return {"status": "failed", "message": f"Directory '{base_path}' does not exist."}
    if not os.path.isdir(base_path):
        return {"status": "failed", "message": f"'{base_path}' is not a directory."}

    max_size = -1
    max_sized_file = ""
    max_sized_path = ""

    for dir_path, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(dir_path, file)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > max_size:
                    max_size = file_size
                    max_sized_file = file
                    max_sized_path = file_path
            except OSError:
                continue

    if max_size == -1:
        return {"status": "failed", "message": "No files found in the directory."}

    return {
        "status": "successful",
        "data": {
            "file_name": max_sized_file,
            "file_path": max_sized_path,
            "size_bytes": max_size
        }
    }

@mcp.tool()
def get_total_size(base_path: str) -> dict:
    """
    Calculate the total size of all files in the directory (including subdirectories).

    Args:
        base_path (str): The root directory path to calculate size for.

    Returns:
        dict: Status and data with total size in bytes,
              or error message if path invalid or empty.
    """
    import os

    if not os.path.exists(base_path):
        return {"status": "failed", "message": f"Directory '{base_path}' does not exist."}
    if not os.path.isdir(base_path):
        return {"status": "failed", "message": f"'{base_path}' is not a directory."}

    total_size = 0
    file_found = False

    for dir_path, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(dir_path, file)
            try:
                total_size += os.path.getsize(file_path)
                file_found = True
            except OSError:
                continue

    if not file_found:
        return {"status": "failed", "message": "No files found in the directory."}

    return {
        "status": "successful",
        "data": {
            "total_size_bytes": total_size
        }
    }


# PDF PAGE EXTRACTION
@mcp.tool()
def extract_page_text(pdf_path: str, page_number: int) -> dict:
    """
    Extract text from a specific page in a PDF using pdfplumber.

    Args:
        pdf_path (str): Path to the PDF file.
        page_number (int): 1-based page number to extract.

    Returns:
        dict: Status and extracted text or error message.
    """
    import os
    import pdfplumber

    if not os.path.exists(pdf_path):
        return {"status": "failed", "message": "PDF file not found."}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number < 1 or page_number > len(pdf.pages):
                return {"status": "failed", "message": "Invalid page number."}
            text = pdf.pages[page_number - 1].extract_text() or ""
        return {"status": "successful", "data": text.strip()}
    except Exception as e:
        return {"status": "failed", "message": str(e)}

@mcp.tool()
def extract_page_range_text(pdf_path: str, start_page: int, end_page: int) -> dict:
    """
    Extract text from a range of pages in a PDF using pdfplumber.

    Args:
        pdf_path (str): Path to the PDF file.
        start_page (int): 1-based start page.
        end_page (int): 1-based end page (inclusive).

    Returns:
        dict: Status and combined extracted text or error message.
    """
    import os
    import pdfplumber

    if not os.path.exists(pdf_path):
        return {"status": "failed", "message": "PDF file not found."}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            if start_page < 1 or end_page > num_pages or start_page > end_page:
                return {"status": "failed", "message": "Invalid page range."}

            extracted = []
            for i in range(start_page - 1, end_page):
                text = pdf.pages[i].extract_text() or ""
                extracted.append(text.strip())

        return {"status": "successful", "data": "\n\n".join(extracted)}
    except Exception as e:
        return {"status": "failed", "message": str(e)}


# FILES RENAMER
@mcp.tool()
def rename_file(old_path: str, new_path: str) -> dict:
    """
    Rename a single file.

    Args:
        old_path (str): Original file path.
        new_path (str): New desired file path.

    Returns:
        dict: Status and confirmation message.
    """
    import os

    if not os.path.exists(old_path):
        return {"status": "failed", "message": "Original file not found."}

    try:
        os.rename(old_path, new_path)
        return {"status": "successful", "message": f"Renamed to {new_path}"}
    except Exception as e:
        return {"status": "failed", "message": str(e)}

@mcp.tool()
def rename_files_with_prefix_to_name(dir_path: str, target_prefix: str, new_base_name: str) -> dict:
    """
    Rename all files in a directory that start with a specific prefix to a new base name.

    Args:
        dir_path (str): Directory containing the files.
        target_prefix (str): The prefix of files to match.
        new_base_name (str): The new base name to rename matched files to.

    Returns:
        dict: Status and list of renamed files.
    """
    import os

    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        return {"status": "failed", "message": "Directory not found."}

    try:
        renamed_files = []
        counter = 1

        for filename in sorted(os.listdir(dir_path)):
            if filename.startswith(target_prefix):
                old_file = os.path.join(dir_path, filename)
                if os.path.isfile(old_file):
                    extension = os.path.splitext(filename)[1]
                    new_filename = f"{new_base_name}_{counter}{extension}"
                    new_file = os.path.join(dir_path, new_filename)
                    os.rename(old_file, new_file)
                    renamed_files.append(f"{filename} -> {new_filename}")
                    counter += 1

        if not renamed_files:
            return {"status": "failed", "message": "No files matched the prefix."}

        return {"status": "successful", "data": renamed_files}
    except Exception as e:
        return {"status": "failed", "message": str(e)}


if __name__ == "__main__":
    mcp.run(transport="sse")