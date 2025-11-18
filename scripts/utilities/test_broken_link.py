import requests

# Test one of the broken links
broken_url = "https://doi.org/10.1287/mksc.2022.0357\\"
fixed_url = "https://doi.org/10.1287/mksc.2022.0357"

print("Testing broken URL with trailing backslash:")
print(f"URL: {broken_url}")
try:
    r = requests.head(broken_url, timeout=5, allow_redirects=True)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("\nTesting fixed URL without backslash:")
print(f"URL: {fixed_url}")
try:
    r = requests.head(fixed_url, timeout=5, allow_redirects=True)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
