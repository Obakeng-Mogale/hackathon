def my_function(text: str):
    # Your code that uses the 'text' parameter
    print(text)

# The name of your text file
file_name = "test_transcript.txt"

# Open the file and read its contents
try:
    with open(file_name, 'r') as file:
        file_contents = file.read()
except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found.")
    file_contents = None

# Check if the file was read successfully and then call the function
if file_contents is not None:
    my_function(file_contents)