import argparse
import fnmatch
from urllib.parse import urlparse

def load_file(filename):
    """Load items from a file into a set, handling encoding issues."""
    items = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    items.add(stripped)
    except UnicodeDecodeError:
        print(f"Warning: UTF-8 decoding failed for '{filename}'. Falling back to latin-1 with error ignoring.")
        with open(filename, 'r', encoding='latin-1', errors='ignore') as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    items.add(stripped)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        exit(1)
    return items

def matches_wildcard(item, wildcard_patterns):
    """Check if an item matches any wildcard pattern and return matching pattern."""
    for pattern in wildcard_patterns:
        if fnmatch.fnmatch(item, pattern):
            return pattern
    return None

def filter_subdomains(subdomains, out_of_scope):
    """Filter out of scope subdomains and track removal reasons."""
    exact_matches = set(domain for domain in out_of_scope if '*' not in domain)
    wildcard_patterns = set(domain for domain in out_of_scope if '*' in domain)
    
    in_scope = set()
    removed_domains = []
    
    for subdomain in subdomains:
        if subdomain in exact_matches:
            removed_domains.append([subdomain, "exact match", subdomain])
            continue
        matched_pattern = matches_wildcard(subdomain, wildcard_patterns)
        if matched_pattern:
            removed_domains.append([subdomain, "wildcard match", matched_pattern])
            continue
        in_scope.add(subdomain)
    
    return in_scope, removed_domains

def filter_urls(urls, out_of_scope):
    """Filter URLs based on out-of-scope domains or URL patterns with reasons."""
    # Separate domain-only patterns and URL patterns
    domain_exact = set()
    domain_wildcards = set()
    url_exact = set()
    url_wildcards = set()
    
    for pattern in out_of_scope:
        if pattern.startswith(('http://', 'https://')):
            if '*' in pattern:
                url_wildcards.add(pattern)
            else:
                url_exact.add(pattern)
        else:
            if '*' in pattern:
                domain_wildcards.add(pattern)
            else:
                domain_exact.add(pattern)
    
    in_scope = set()
    removed_domain_info = {}  # {domain: [count, reason, matched_pattern]}
    
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.hostname
        if not domain:
            continue
        
        # Check full URL against URL patterns first
        full_url = url.lower()  # Case-insensitive matching
        if full_url in url_exact:
            if domain not in removed_domain_info:
                removed_domain_info[domain] = [0, "exact URL match", full_url]
            removed_domain_info[domain][0] += 1
            continue
        matched_url_pattern = matches_wildcard(full_url, url_wildcards)
        if matched_url_pattern:
            if domain not in removed_domain_info:
                removed_domain_info[domain] = [0, "wildcard URL match", matched_url_pattern]
            removed_domain_info[domain][0] += 1
            continue
        
        # Fall back to domain-only checks
        if domain in domain_exact:
            if domain not in removed_domain_info:
                removed_domain_info[domain] = [0, "exact domain match", domain]
            removed_domain_info[domain][0] += 1
            continue
        matched_domain_pattern = matches_wildcard(domain, domain_wildcards)
        if matched_domain_pattern:
            if domain not in removed_domain_info:
                removed_domain_info[domain] = [0, "wildcard domain match", matched_domain_pattern]
            removed_domain_info[domain][0] += 1
            continue
        
        in_scope.add(url)
    
    return in_scope, removed_domain_info

def save_to_file(items, filename):
    """Save items to output file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for item in sorted(items):
                f.write(f"{item}\n")
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        exit(1)

def print_subdomain_removal_info(removed_domains):
    """Print detailed information about removed subdomains."""
    if removed_domains:
        print("\nRemoved Subdomains:")
        print("-" * 80)
        print(f"{'Subdomain':<40} {'Reason':<15} {'Matched Pattern':<25}")
        print("-" * 80)
        for domain, reason, pattern in removed_domains:
            print(f"{domain:<40} {reason:<15} {pattern:<25}")
        print("-" * 80)
    else:
        print("\nNo subdomains were removed.")

def print_url_removal_info(removed_domain_info):
    """Print detailed summary of domains whose URLs were removed."""
    if removed_domain_info:
        print("\nDomains with Removed URLs:")
        print("-" * 80)
        print(f"{'Domain':<30} {'URLs Removed':<15} {'Reason':<20} {'Matched Pattern':<20}")
        print("-" * 80)
        for domain, (count, reason, pattern) in removed_domain_info.items():
            print(f"{domain:<30} {count:<15} {reason:<20} {pattern:<20}")
        print("-" * 80)
    else:
        print("\nNo URLs were removed.")

def main():
    parser = argparse.ArgumentParser(
        description="""Filter out-of-scope subdomains or URLs from a list.

This script processes either a list of subdomains or URLs, removing items that match
out-of-scope domains (exact matches or wildcard patterns) or URL patterns (in URL mode).
Use without --urls for subdomain mode, or with --urls for URL mode.

Examples:
  Subdomain mode: python3 saymyscope.py -i subs.txt -os out.txt -o inscope.txt
  URL mode: python3 saymyscope.py -i urls.txt -os out.txt -o inscope_url.txt --urls
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True, 
                       help='Input file containing subdomains (e.g., subs.txt) or URLs (e.g., urls.txt)')
    parser.add_argument('-os', '--outscope', required=True, 
                       help='File containing out-of-scope domains or URLs (e.g., out.txt), supports wildcards like *.example.com or http://example.com/path/*')
    parser.add_argument('-o', '--output', required=True, 
                       help='Output file for in-scope subdomains or URLs (e.g., inscope.txt)')
    parser.add_argument('--urls', action='store_true',
                       help='Process URLs instead of subdomains; removes URLs matching out-of-scope domains or URL patterns')
    
    args = parser.parse_args()
    
    input_items = load_file(args.input)
    out_of_scope = load_file(args.outscope)
    
    if args.urls:
        in_scope_items, removed_info = filter_urls(input_items, out_of_scope)
        total_removed = sum(info[0] for info in removed_info.values())
        print_url_removal_info(removed_info)
    else:
        in_scope_items, removed_info = filter_subdomains(input_items, out_of_scope)
        total_removed = len(removed_info)
        print_subdomain_removal_info(removed_info)
    
    save_to_file(in_scope_items, args.output)
    
    print(f"\nSummary:")
    print(f"Total items: {len(input_items)}")
    print(f"Out of scope removed: {total_removed}")
    print(f"In scope items: {len(in_scope_items)}")

if __name__ == "__main__":
    main()
