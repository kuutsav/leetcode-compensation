# leetcode compensation

[![automatic-data-update](https://github.com/kuutsav/leetcode-compensation/actions/workflows/data-refresh.yaml/badge.svg)](https://github.com/kuutsav/leetcode-compensation/actions/workflows/data-refresh.yaml)
[![pages-build-deployment](https://github.com/kuutsav/leetcode-compensation/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/kuutsav/leetcode-compensation/actions/workflows/pages/pages-build-deployment)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

https://kuutsav.github.io/leetcode-compensation/

Analysing compensations mentioned on the Leetcode forums (only supports posts from `India` at the moment).

The `leetcomp` directory contains scripts to fetch new posts from [https://leetcode.com/discuss/compensation](https://leetcode.com/discuss/compensation).<br>We use LLMs to parse structured information from the scraped posts, which is then sanitised and aggregated.

---

![image info](./assets/leetcomp.png)

## Getting Started

Install uv with our standalone installers, or from [PyPI](https://pypi.org/project/uv/):

```shell
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# For a specific version.
curl -LsSf https://astral.sh/uv/0.2.9/install.sh | sh
powershell -c "irm https://astral.sh/uv/0.2.9/install.ps1 | iex"

# With pip.
pip install uv

# With pipx.
pipx install uv

# With Homebrew.
brew install uv
```

To create a virtual environment:

```shell
uv venv  # Create a virtual environment at .venv.
```

To activate the virtual environment:

```shell
# On macOS and Linux.
source .venv/bin/activate

# On Windows.
.venv\Scripts\activate
```

To install a package into the virtual environment:

```shell
uv pip install -r requirements.txt  # Install from a requirements.txt file.
```

## Updating data

> Make sure you have completed the steps above and are in a venv

```bash
$ export PYTHONPATH=.
$ python leetcomp/refresh.py
$ python leetcomp/parse.py
```

## Roadmap

- [x] ~~Sort by Compensation and Yoe~~
- [ ] ~~Search for Companies~~ and Roles
- [ ] Filters for Yoe, Date, Compensation, Location
- [ ] Add pagination

## Contributions

PRs are welcome but please go through [CONTRIBUTING.md](CONTRIBUTING.md) before raising a PR.
