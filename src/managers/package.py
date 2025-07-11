from dataclasses import dataclass

from packaging.version import InvalidVersion, parse


@dataclass
class Package:
    json: dict

    def __post_init__(self):
        self.name = self.json["info"]["name"]
        self.version = self.json["info"]["version"]
        self.releases = self.json["releases"]

    @property
    def current_version(self):
        return self.version

    @property
    def latest_version(self):
        version_str = self.parse_versions_for_latest().__str__()
        return version_str

    @property
    def update_type(self):
        """
        Determine if the latest version is a major, minor, or patch update compared to the current version.
        Returns one of: 'major', 'minor', 'patch', or None if not applicable.
        """
        try:
            current = parse(self.current_version)
            latest = parse(self.latest_version)
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

    @property
    def repository_url(self):
        """
        Returns the repository URL from project_urls.Source if present, otherwise None.
        """
        project_urls = self.json["info"].get("project_urls", {})
        if isinstance(project_urls, dict):
            return project_urls.get("Source")
        return None

    def parse_versions_for_latest(self):
        """
        Parse the versions and return the latest version
        using the packaging library now, previously parsed upload dates
        but found that it was not reliable because if an earlier version
        gets a new patch it's upload date could be the latest.
        It only happened for the Django package but it's better to be safe
        """
        latest_version = tuple()
        for version, releases in self.releases.items():
            for release in releases:
                try:
                    parsed_version = parse(version)
                except InvalidVersion:
                    # except InvalidVersion:
                    #     # e.g. paramiko has a release with a version of '0.1-bulbasaur'
                    #     # which isn't a version we are interested in and is likely a pre-release
                    #     # without it bee declared as such
                    #     pass
                    continue
                # # This doesn't seen to be required but keep it here for now
                # # until it's been tested a little more.
                if parsed_version.is_prerelease or parsed_version.is_postrelease:
                    continue
                if not len(latest_version):
                    latest_version = (parsed_version, release)
                else:
                    if parsed_version > latest_version[0]:
                        latest_version = (parsed_version, release)

        return latest_version[0] if len(latest_version) else None
