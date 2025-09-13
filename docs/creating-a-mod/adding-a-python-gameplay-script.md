# Adding a Python Gameplay Script

In the previous [**Basic Mod**](basic-mod.md) guide, we created a repo in the Civ VII `Mods` directory, and created a simple Python runner to build a simple `.modinfo` file followed by running the game. However, at this point, this is just a redundant way of writing a `.modinfo` XML file, nothing has really changed from standard modding other than writing less lines of XML. The whole purpose of this package is to be able to run Python scripts in Civ VII mods, and in this guide we will do just that. Running Python scripts in Civ VII is a difficult process. Civ VII's (and previous Civ games') modding framework is written in JavaScript in kind of an isolated sandbox web browser mode. Therefore, we have to find a way to convert our Python code to JavaScript. **pyciv7** has one way<!-- two ways --> of doing this:

- **Transpiling Python code using [Transcrypt](https://www.transcrypt.org/)**: Transcrypt is a Python framework that "transpiles" Python code to JavaScript code (or in other words, converts Python files to JavaScript files). Transcrypt is light-weight and is what **pyciv7's** API uses to create bindings of Civ VII's modding API.

<!-- !!! info "When to use Transcrypt vs Pyodide"
    |                | **Lightweight** | **Requires dependencies** |
    |:--------------:|:---------------:|:-------------------------:|
    | **Transcrypt** |        ✔️        |             ❌          |
    |    **Pyodide** |        ❌        |             ✔️          | -->

This guide will walk you through creating and running a simple Civ VII mod using Python scripts by modifying the repository we created in the previous [**Basic Mod**](basic-mod.md) guide.

!!! abstract "What you'll do"
    1. Create a basic "Hello, world" Python script to add to our `.modinfo`.
    2. Add Python dependencies to our Python script.
    3. Learn how to use **pyciv7's** game bindings and how to handle unimplemented bindings.

## Running Python in Civ 7 via Transcrypt

<!-- ## Running Python in Civ 7 via Pyodide -->

## Using the pyciv7 Game Bindings

### Unimplemented Bindings
