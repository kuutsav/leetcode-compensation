A tool that helps you find **Software Engineer Salary in India** by:

- Fetching compensation data from Leetcode forums.
- Updating bi-weekly through GitHub action PRs.
- Using LLMs for parsing and sanitizing structured data from posts, followed by aggregation.

> [!WARNING]
> A 2-day data refresh delay allows the votes to accumulate, after that posts with negative votes are dropped.

## Getting Started

Install uv from [Standalone Installers](https://docs.astral.sh/uv/getting-started/installation/) or from [PyPI](https://pypi.org/project/uv/):

To create a virtual environment:

```bash
uv venv  # Create a virtual environment at .venv.
```

To activate the virtual environment:

```bash
# On macOS and Linux.
source .venv/bin/activate

# On Windows.
.venv\Scripts\activate
```

To install packages into the virtual environment:

```bash
uv pip install -r requirements.txt  # Install from a requirements.txt file.
```

Or simply use:

```bash
uv sync  # Install all dependencies from pyproject.toml
```

## Updating Data

> [!NOTE]
> You'll need LLM inference setup (config.toml: llms) using `local: ollama`, `vllm`, or `api: openrouter`

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

This will:
1. Fetch new posts from Leetcode forums
2. Parse them using the LLM to extract salary, YOE, bonus, stocks, etc.
3. Normalize company names, role titles, and locations
4. Aggregate the data into structured format

## Project Structure

- `src/leetcomp/` - Core modules (fetch, parse, normalize, sync)
- `data/` - Stored compensation data and mappings
- `index.html` - Frontend visualization
