import requests
from pathlib import Path
from abc import ABC, abstractmethod
from urllib.parse import urlparse
import os
import re
import git
import shutil
import subprocess
from typing import List, Optional
import zipfile
import tarfile
from enum import Enum
from pydantic import BaseModel


class RepoStatus(str, Enum):
    OK = "ok"
    EMPTY = "empty"
    INACCESSIBLE = "inaccessible"
    NOT_SUPPORTED = "not_supported"


class RepoExtractionResult(BaseModel):
    repo_url: str
    status: RepoStatus
    repo_path: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None


class RepoNotSupportedError(Exception):
    pass


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def extract_file_tree(repo_path: Path) -> List[str]:
    """Return a sorted list of relative file paths."""
    files = []
    for p in repo_path.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(repo_path)))
    return sorted(files)


class RepoCloner(ABC):
    @abstractmethod
    def clone(self, repo_url: str, base_path: Path) -> Path:
        pass


class DefaultGitCloner(RepoCloner):
    def clone(self, repo_url: str, base_path: Path) -> Path:
        parsed = urlparse(repo_url)
        parts = [p for p in parsed.path.split("/") if p]
        repo_name = os.path.splitext(parts[-1])[0] if parts else "unknown_repo"

        repo_path = base_path / repo_name

        if repo_path.exists() and any(repo_path.iterdir()):
            return repo_path

        base_path.mkdir(parents=True, exist_ok=True)
        git.Repo.clone_from(repo_url, repo_path, depth=1)
        return repo_path


class ZenodoCloner(RepoCloner):
    API_BASE = "https://zenodo.org/api/records/"

    def _extract_zip_normalized(self, zip_path: Path, repo_path: Path):
        with zipfile.ZipFile(zip_path) as zf:
            members = zf.namelist()
            top_levels = {
                m.split("/")[0]
                for m in members
                if "/" in m and not m.startswith("__MACOSX")
            }
            zf.extractall(repo_path)

        if len(top_levels) == 1:
            root = repo_path / next(iter(top_levels))
            if root.exists() and root.is_dir():
                for item in root.iterdir():
                    shutil.move(str(item), repo_path)
                shutil.rmtree(root)

    def clone(self, repo_url: str, base_path: Path) -> Path:
        record_id = repo_url.rstrip("/").split("/")[-1]
        resp = requests.get(f"{self.API_BASE}{record_id}")
        resp.raise_for_status()
        data = resp.json()

        title = data["metadata"].get("title", f"zenodo_{record_id}")
        safe_title = re.sub(r"[^a-zA-Z0-9._-]+", "_", title).strip("_")
        repo_path = base_path / safe_title
        repo_path.mkdir(parents=True, exist_ok=True)

        for f in data.get("files", []):
            download_url = f["links"]["self"]
            file_name = f["key"]
            local_path = repo_path / file_name

            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, "wb") as out:
                    for chunk in r.iter_content(8192):
                        out.write(chunk)

            if zipfile.is_zipfile(local_path):
                self._extract_zip_normalized(local_path, repo_path)
                local_path.unlink()

            elif tarfile.is_tarfile(local_path):
                with tarfile.open(local_path) as tf:
                    tf.extractall(repo_path)
                local_path.unlink()

        return repo_path


class FigshareCloner(RepoCloner):
    API_BASE = "https://api.figshare.com/v2/articles/"

    def clone(self, repo_url: str, base_path: Path) -> Path:
        article_id = repo_url.rstrip("/").split("/")[-1]
        meta = requests.get(f"{self.API_BASE}{article_id}").json()
        title = meta.get("title", f"figshare_{article_id}")

        safe_title = re.sub(r"[^a-zA-Z0-9._-]+", "_", title).strip("_")
        repo_path = base_path / safe_title
        repo_path.mkdir(parents=True, exist_ok=True)

        files = requests.get(f"{self.API_BASE}{article_id}/files").json()
        for f in files:
            path = repo_path / f["name"]
            with requests.get(f["download_url"], stream=True) as r:
                r.raise_for_status()
                with open(path, "wb") as out:
                    for chunk in r.iter_content(8192):
                        out.write(chunk)

        return repo_path


class OSFCloner(RepoCloner):
    def clone(self, repo_url: str, base_path: Path) -> Path:
        project_id = repo_url.rstrip("/").split("/")[-1]
        tmp_root = base_path / project_id

        if not (tmp_root.exists() and any(tmp_root.iterdir())):
            subprocess.run(
                ["osf", "-p", project_id, "clone"],
                cwd=base_path,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        repo_path = base_path / project_id
        repo_path.mkdir(parents=True, exist_ok=True)

        osf_storage = tmp_root / "osfstorage"
        if not osf_storage.exists():
            return repo_path  # EMPTY but accessible

        for item in osf_storage.iterdir():
            shutil.move(str(item), repo_path)

        shutil.rmtree(osf_storage, ignore_errors=True)
        return repo_path


class DOICloner(RepoCloner):
    """Resolves a DOI link to its final URL and delegates to the correct cloner."""

    def clone(self, repo_url: str, repo_path: Path):
        repo_path.mkdir(parents=True, exist_ok=True)
        # print(f"Resolving DOI: {repo_url}")

        try:
            resp = requests.head(repo_url, allow_redirects=True, timeout=10)
            resp.raise_for_status()
            final_url = resp.url
            # print(f"DOI resolved to: {final_url}")
            cloner = get_repo_cloner(final_url)
            cloner.clone(final_url, repo_path)

        except Exception as e:
            print(f"Failed to resolve DOI or delegate: {e}")
            raise


CLONER_MAP = {
    "github.com": DefaultGitCloner,
    "gitlab.com": DefaultGitCloner,
    "gitee.com": DefaultGitCloner,
    "zenodo.org": ZenodoCloner,
    "figshare.com": FigshareCloner,
    "osf.io": OSFCloner,
}


def get_repo_cloner(repo_url: str) -> RepoCloner:
    """Determines the appropriate RepoCloner subclass for a given URL."""
    parsed_url = urlparse(repo_url)
    domain = parsed_url.netloc
    domain = re.sub(r"^www\.", "", domain).lower()

    if "doi.org" in domain or "dx.doi.org" in domain:
        return DOICloner()

    if domain in CLONER_MAP:
        return CLONER_MAP[domain]()

    if any(s in domain for s in ["git.", ".github.io", ".gitlab.", "gitlab", ".gite."]):
        return DefaultGitCloner()

    raise ValueError(f"No specific cloner found for URL domain or format: {domain}")
