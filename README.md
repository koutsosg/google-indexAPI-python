# google-indexAPI-python

## Overview

`google-indexAPI-python` is a Python-based tool for automating the submission of URLs to Google's Indexing API. This project simplifies the process of notifying Google about updates to your website, ensuring that your content is indexed quickly and efficiently.

## Prerequisites

Steps needed to be performed

1. Python (duh)
2. Custom Search Engine ID
3. API key for Google Custom Search API
4. Service Account JSON Key for Google Indexing API

Refer to these resources for setup instructions:

- [Python](https://www.python.org/)
- [Programmable Search Engine](https://developers.google.com/custom-search/docs/overview)
- [Prerequisites for the Indexing API](https://developers.google.com/search/apis/indexing-api/v3/prereqs#oauth)

## Installation

To set up and run the project, follow these steps:

1. **Clone the Repository**

   Clone the repository to your local machine using Git:

   ```bash
   git clone https://github.com/koutsosg/google-indexAPI-python.git
   cd google-indexAPI-python
   ```

2. **Install Poetry**

   Ensure Poetry is installed on your system. You can install Poetry using the following command:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Alternatively, follow the Poetry [installation instructions](https://python-poetry.org/docs/#installation)

3. **Install Dependencies**
   Use Poetry to install the project dependencies:

   ```bash
   poetry install
   ```

   This command creates a virtual environment and installs all required dependencies.

4. Add Configuration Files

   You need to provide the following files in the root directory of the project:

- **`apidetails.json`**: The JSON key file for authenticating with the Google Indexing API.
- **`my_data.csv`**: The CSV file containing the URLs to be processed. Ensure it has a column named "URL".

## Usage

1. **Activate the Poetry Shell**

   Activate the virtual environment created by Poetry:

   ```bush
   poetry shell
   ```

2. **Run the Script**

   Execute the script to start processing URLs:

   ```bush
   poetry run start
   ```

## Contributing

Guidelines for contributing to the project.

## License

This project is licensed under the Custom License - see the [LICENSE](https://github.com/koutsosg/google-indexAPI-python?tab=License-1-ov-file#readme) file for details.

## Initial Release

This is the initial release of the `google-indexAPI-python` project, featuring the executable version without GUI.

**Included in this release:**

- `indexing.exe` (Windows) or `indexing` (macOS/Linux): The main executable for processing URLs.
- `README.md`: Instructions for using the executable.

**Instructions:**

1. Download the ZIP file from the [releases page](https://github.com/koutsosg/google-indexAPI-python/releases).
2. Extract the contents folder.
3. You need to provide the following files in the same folder:

- **`apidetails.json`**: The JSON key file for authenticating with the Google Indexing API.
- **`my_data.csv`**: The CSV file containing the URLs to be processed. Ensure it has a column named "URL".

4. Run the executable (`indexing.exe` or `indexing`).
5. Check the Logs Folder for results

- The executable generates log files in a directory named logs in the same location where the executable was run.
