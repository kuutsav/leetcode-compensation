## Pre-commit Checks

Before submitting your contributions, make sure all pre-commit checks pass. This is especially important for data refreshes and parsing-related changes, which often involve Python code. Here's how you can do it:

- **Install Pre-commit Hooks**: If not already set up, install pre-commit hooks in your local repository. This usually involves running the command `pre-commit install` after cloning the repository and setting up the venv.
- **Run Pre-commit Locally**: This should happen automatically before a commit, if not, run `pre-commit run --all-files` to check all your changes. Fix any issues that arise.

## UI Design and Aesthetics

Our project follows a specific design language and aesthetic to ensure a cohesive user experience. When contributing:

- **Adhere to Existing Styles**: Make sure your contributions match the general design, color schemes, and component styles of the project.
- **Pre-validation**: Before implementing significant design changes or adding new components, validate your idea.
- **Screenshots**: Provide screenshots or mock-ups that showcase how the change or new component will look and function within the application. This helps others visualize your proposal and provide constructive feedback.

## JavaScript Dependencies

We aim to keep the ui as lightweight and dependency free as possible.

If you believe a new dependency is absolutely necessary, please start a discussion by opening an issue or pull request. Include your rationale for the addition and any potential alternatives you've considered.
