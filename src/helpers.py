from packaging.version import InvalidVersion, parse
from rich import box
from rich.table import Table
from src.client import PyPiClient
from src.managers.package import Package


def calculate_update_type(current_version, latest_version):
    """
    Calculate if the latest version is a major, minor, or patch update compared to the current version.
    Returns one of: 'major', 'minor', 'patch', or None.
    """
    try:
        current = parse(current_version)
        latest = parse(latest_version)
    except InvalidVersion:
        return None
    if current == latest:
        return None
    if hasattr(current, "major") and hasattr(latest, "major"):
        if latest.major > current.major:
            return "major"
        elif latest.minor > current.minor:
            return "minor"
        elif latest.micro > current.micro:
            return "patch"
    return None


def package_table_row(frozen, package):
    name = package.name
    latest_version = package.latest_version
    frozen_version = frozen.dependencies.get(name.lower())

    # Calculate update_type based on frozen version vs latest version
    update_type = None
    if frozen_version and frozen_version != latest_version and "git+https://" not in frozen_version:
        update_type = calculate_update_type(frozen_version, latest_version)

    if frozen_version and frozen_version != latest_version:
        if "git+https://" in frozen_version:
            status = "Check"
            style = "red1"
        else:
            status = "Outdated"
            style = "yellow1"
    elif not frozen_version:
        status = "Check"
        style = "cyan1"
        frozen_version = "Unable to determine version"
    else:
        status = "OK"
        style = "green3"

    # Always reflect update_type if present
    if update_type:
        status = f"{status} ({update_type})"

    if "git+https://" in frozen_version:
        frozen_version = frozen_version.replace("git+https://", "")
        frozen_version = f"{frozen_version.split('@')[0]} TAG {frozen_version.split('@')[1]}"
    return name, latest_version, frozen_version, status, style


def get_packages(dependencies, messages):
    client = PyPiClient()
    packages = []

    for dependency in dependencies:
        c = client.get_package(dependency)
        if isinstance(c, int):
            # deals with cases such as package names with [extras] in them
            messages.append(f"{dependency}")
            continue
        package = Package(c.json())

        packages.append(package)
    return packages


def dependency_table_header(title):
    table = Table(title=title, box=box.MARKDOWN, show_lines=True)
    table.add_column("Package", style="bright_white")
    table.add_column("Installed Version", style="bright_white")
    table.add_column("Latest Version", style="bright_white")
    table.add_column("Status", style="bright_white")
    return table


def information_table(repository_manager, docker_image, poetry_version):
    table = Table(title="Branch Information", box=box.MARKDOWN, show_lines=True)
    table.add_column("", style="bright_white")
    table.add_column("Details", style="bright_white")
    table.add_row("Repository URL", repository_manager.repo_url)
    table.add_row("Branch Name", repository_manager.get_branch())
    table.add_row("Dockerfile Path", repository_manager.dockerfile_path)
    table.add_row("Poetry Version", poetry_version)
    table.add_row("Docker Image", docker_image)
    return table


def get_branch_data(branches):
    column_data = []
    for branch in branches.items():
        if branch[0] < 10:
            column_data.append(f" {branch[0]} {branch[1]}")
        else:
            column_data.append(f"{branch[0]} {branch[1]}")
    return column_data
