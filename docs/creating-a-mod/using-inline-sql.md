# Using Inline SQL

In the official Civ VII modding framework, you can modify the in-game databases either using SQL files or XML files. While this approach is still fine with **pyciv7**, there is a more *Pythonic* way of doing that without having to create extra files. There are plenty of Python libraries that handle SQL operations, such as Python's built-in `sqlite3`, and external libraries such as SQLAlchemy and ORMs like Django and SQLModel. **pyciv7** maximizes these features by allowing modders to write SQL code in their Python scripts, as opposed to creating new data files to modify the database. This is accomplished with SQLModel and SQLAlchemy.

This guide will walk you through how to use SQL in your Python scripts by replacing the `data/antiquity-traditions.xml` we created in the [**Basic Mod**](basic-mod.md) guide with inline SQL.

!!! abstract "What you'll do"
    1. Create a basic "Hello, world" Python script to add to our `.modinfo`.
    2. Add Python dependencies to our Python script.
    3. Learn how to use **pyciv7's** game bindings and how to handle unimplemented bindings.

## Using SQLModels

### Unimplemented Tables
