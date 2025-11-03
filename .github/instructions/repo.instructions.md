---
applyTo: '**'
---
# Repository Instructions
- This repository is designed for data engineering workshops.
- Follow the provided guidelines for setting up your environment and running scripts.
- Look at README.md for more details on project structure and usage.

## Naming Conventions
- Use snake_case for function names 
- Use PascalCase for class names
- Use UPPER_CASE for constants
- Use camelCase for variable names

## Documentation
 - add docstrings to all functions using the following format:
   ```
   """
   Brief description of the function.

   Parameters:
   param1 (type): Description of param1.
   param2 (type): Description of param2.

   Returns:
   type: Description of the return value.
   """
   ```
- add type hints to all function signatures

## Error Handling 
- use try-except blocks to handle potential errors
- catch specific exceptions rather than using a general exception handler
- always log exceptions before re-raising or handling them
