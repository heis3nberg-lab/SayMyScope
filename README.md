# SayMyScope

`saymyscope.py` is a Python script designed to filter subdomains or URLs based on out-of-scope definitions. It supports exact matches and wildcard patterns (e.g., `*.example.com`), making it a handy tool for security researchers, penetration testers, and anyone managing lists of domains or URLs. The script can operate in two modes: subdomain mode (default) or URL mode (with the `--urls` flag).

The tool reads an input file containing subdomains or URLs, compares them against a list of out-of-scope patterns, and outputs the in-scope items to a specified file. It also provides detailed feedback on what was removed and why.

## Features
- Filters subdomains or URLs based on exact matches or wildcard patterns.
- Supports two modes:
  - **Subdomain mode**: Filters subdomains (e.g., `sub.example.com`).
  - **URL mode**: Filters full URLs (e.g., `https://sub.example.com/path`).
- Handles encoding issues gracefully with fallback to Latin-1 if UTF-8 fails.
- Provides detailed removal reasons (e.g., "exact match" or "wildcard match").
- Outputs results to a file and prints a summary of processed items.

## Installation

### Prerequisites
- Python 3.x (tested with Python 3.9+)
- No external dependencies beyond the Python standard library.

### Steps
Clone the repository:
```bash
git clone https://github.com/heis3nberg-lab/SayMyScope.git
cd SayMyScope
```

Ensure you have Python 3 installed:
```bash
python3 --version
```

Run the script directly (no installation required):
```bash
python3 saymyscope.py --help
```

## Usage
```bash
python3 saymyscope.py -i INPUT_FILE -os OUT_OF_SCOPE_FILE -o OUTPUT_FILE [--urls]
```

### Arguments
- `-i, --input`: Input file containing subdomains or URLs (required).
- `-os, --outscope`: File containing out-of-scope domains or URLs (required).
- `-o, --output`: Output file for in-scope subdomains or URLs (required).
- `--urls`: Optional flag to process URLs instead of subdomains.

### File Formats
- **Input File**: One subdomain or URL per line.
- **Out-of-Scope File**: One pattern per line. Supports:
  - Exact matches (e.g., `example.com`, `https://example.com/path`).
  - Wildcard patterns (e.g., `*.example.com`, `http://example.com/*`).

## Examples

### Example 1: Subdomain Mode
Filter a list of subdomains, removing those that match out-of-scope patterns.

#### Files
**subs.txt:**
```
sub1.example.com
sub2.example.com
test.example.org
admin.test.com
```

**out.txt:**
```
*.example.com
test.com
```

#### Command
```bash
python3 saymyscope.py -i subs.txt -os out.txt -o inscope.txt
```

#### Output
```
Removed Subdomains:
--------------------------------------------------------------------------------
Subdomain                                Reason          Matched Pattern         
--------------------------------------------------------------------------------
sub1.example.com                        wildcard match  *.example.com           
sub2.example.com                        wildcard match  *.example.com           
admin.test.com                          exact match     test.com                
--------------------------------------------------------------------------------

Results saved to inscope.txt

Summary:
Total items: 4
Out of scope removed: 3
In scope items: 1
```

**inscope.txt:**
```
test.example.org
```

### Example 2: URL Mode
Filter a list of URLs, removing those that match out-of-scope domains or URL patterns.

#### Files
**urls.txt:**
```
https://sub1.example.com/path1
http://sub2.example.com/path2
https://example.org/login
http://admin.test.com/dashboard
https://example.com/private/api
```

**out.txt:**
```
*.example.com
https://example.com/private/*
test.com
```

#### Command
```bash
python3 saymyscope.py -i urls.txt -os out.txt -o inscope_url.txt --urls
```

#### Output
```
Domains with Removed URLs:
--------------------------------------------------------------------------------
Domain                          URLs Removed    Reason               Matched Pattern        
--------------------------------------------------------------------------------
sub1.example.com                1               wildcard domain match *.example.com           
sub2.example.com                1               wildcard domain match *.example.com           
admin.test.com                  1               exact domain match   test.com                
example.com                     1               wildcard URL match   https://example.com/private/*
--------------------------------------------------------------------------------

Results saved to inscope_url.txt

Summary:
Total items: 5
Out of scope removed: 4
In scope items: 1
```

**inscope_url.txt:**
```
https://example.org/login
```

## Notes on Wildcards
- Wildcards (`*`) match any sequence of characters in the same position.
- In **subdomain mode**, `*.example.com` matches `sub1.example.com` but not `example.com`.
- In **URL mode**, `https://example.com/*` matches `https://example.com/path` but not `https://sub.example.com/path`.

## Error Handling
- If an input or out-of-scope file is not found, the script exits with an error message.
- If a file cannot be decoded as UTF-8, it falls back to Latin-1 with ignored errors and prints a warning.
- Output file writing errors are caught and reported.

## Contributing
Feel free to submit issues or pull requests on GitHub! Suggestions for improvements (e.g., regex support, additional output formats) are welcome.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
Built with Python's standard library, leveraging `fnmatch` for wildcard matching and `urlparse` for URL handling.
