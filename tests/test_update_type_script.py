from src.managers.package import Package


# Helper to create a fake PyPI JSON response
def make_json(name, current_version, releases):
    return {"info": {"name": name, "version": current_version}, "releases": releases}


# Test cases: (current_version, latest_version, expected_update_type)
test_cases = [
    ("1.2.3", "2.0.0", "major"),
    ("1.2.3", "1.3.0", "minor"),
    ("1.2.3", "1.2.4", "patch"),
    ("1.2.3", "1.2.3", None),
    ("1.2.3", "1.2.3.post1", None),  # postrelease should be ignored
    ("1.2.3", "1.2.3rc1", None),  # prerelease should be ignored
]

for current, latest, expected in test_cases:
    releases = {
        current: [{}],
        latest: [{}],
    }
    pkg = Package(make_json("example", current, releases))
    print(f"Current: {current}, Latest: {pkg.latest_version}, Update type: {pkg.update_type}, Expected: {expected}")
