<h1 align="center">LeetCode Compensation</h1>

<p align="center">
  <a href="https://kuutsav.github.io/leetcode-compensation/">https://kuutsav.github.io/leetcode-compensation/</a>
</p>

A tool that helps you find **Software Engineer Salary in India** by:

- Fetching compensation data from Leetcode forums.
- Updating bi-weekly through GitHub action PRs.
- Using LLMs for parsing and sanitizing structured data from posts, followed by aggregation.

## Getting Started

Install uv from [Standalone Installers](https://docs.astral.sh/uv/getting-started/installation/) or from [PyPI](https://pypi.org/project/uv/):

```bash
uv sync  # Install all dependencies from pyproject.toml
```

## Updating Data

The project uses **LM Studio** by default with the `openai/gpt-oss-20b` model for:

- Parsing salaries, years of experience (YOE), and other compensation details from posts
- Normalizing fields like companies, roles, and locations into structured format

Make sure you have:

- [LM Studio](https://lmstudio.ai/) installed and running
- The `openai/gpt-oss-20b` model downloaded and loaded
- Server running on `http://localhost:1234`

Alternatively, you can use GitHub Models by setting `Provider.GITHUB_MODELS` and the `GITHUB_TOKEN` environment variable.

To sync and fetch new compensation data:

```bash
uv run leetcomp-sync
```
