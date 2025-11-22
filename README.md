# Auto-OSINT Google Dork Generator

Auto-OSINT is a command-line tool designed to support Open Source Intelligence (OSINT) investigations by generating well-structured and context-specific Google Dorks.  
It allows analysts, researchers, and cybersecurity professionals to automate part of the reconnaissance phase by producing relevant search queries for emails, usernames, domains, and subdomains.  
The tool is built with modularity in mind, making it suitable both for manual OSINT workflows and for integration into broader automated pipelines.

## Overview

Google Dorks are advanced search operators used to extract publicly available but often overlooked information from the web.  
By automating their generation, Auto-OSINT helps analysts avoid repetitive manual work and ensures more consistent, broad, and systematic search coverage.  

The tool provides:

- A structured approach to OSINT discovery.
- A reliable way to generate categorized intelligence queries.
- A foundation for later expansion into automated scraping, monitoring, or reporting frameworks.

Auto-OSINT is intended for professionals who require a fast and efficient method to generate reconnaissance queries while maintaining full control of the investigation.

## Features

- **Fully interactive interface:** Users can choose the category of target they want to investigate through a clean terminal menu.
- **Multiple target types supported:**  
  - Email addresses  
  - Usernames and aliases  
  - Domains  
  - Subdomains  
- **Automatic query categorization:** Dorks are grouped logically into areas such as documents, leaks, indexed files, exposed services, and social profiles.
- **Output export capability:** Users can export generated dorks into `.txt` files, useful for investigations, case documentation, or penetration testing reports.
- **Color-based interface:** The tool uses `colorama` to improve readability and navigation.
- **Expandability:** The internal structure is designed so that more modules—such as automated scanning, result parsing, or integration with OSINT APIs—can be added with ease.

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/auto-osint.git
cd auto-osint
````

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the program:

```bash
python3 auto-osint.py
```

## Usage Guide

Once executed, Auto-OSINT presents a clear menu allowing the user to select what type of information they want to generate dorks for:

1. Email addresses
2. Usernames / aliases
3. Domains
4. Subdomains

After entering the target, the tool automatically generates a structured list of Google Dorks adapted to the nature of the input.
Each category of dorks is printed to the console and can be exported to a sanitized `.txt` file for later use.

This makes the tool suitable for:

* OSINT investigations
* Digital footprint assessments
* Threat intelligence gathering
* Penetration testing reconnaissance
* Academic or training purposes

Auto-OSINT does not perform active scanning or interact with external systems; it only generates publicly searchable queries, making it compliant with ethical OSINT standards.

## Exported Files

The tool can export results in plain-text format.
Files follow the naming pattern:

```
dorks_<target>.txt
```

All file names are automatically sanitized to avoid special characters or filesystem issues.
These exported files can be integrated into OSINT documentation, case reports, or digital investigations.

## Project Structure

```
auto-osint/
│── auto-osint.py          # Main program
│── requirements.txt        # Python dependencies
│── README.md               # Documentation
│── LICENSE                 # MIT License
│── .gitignore              # Files and folders excluded from version control
```

This minimal structure ensures the repository stays clean and that only essential files are included.

## Dependencies

Auto-OSINT uses several Python libraries to support its functionality, including:

* aiohttp
* aiofiles
* beautifulsoup4
* colorama
* requests
* tqdm
* python-dateutil

These dependencies are maintained in `requirements.txt` to ensure reproducibility across systems.

## Legal Disclaimer

Auto-OSINT is designed exclusively for lawful OSINT work, research, training, and security analysis.
The author does not assume responsibility for any misuse, unauthorized investigation, or illegal activity conducted with this tool.
Users must confirm that they have authorization before performing any form of digital reconnaissance against a target.

By using Auto-OSINT, you agree to comply with applicable laws and ethical standards.

## Author

Developed by Alejandro Brea Gascón.
Contributions, improvements, and forks are welcome.

```