# Contribution

Contributions are highly welcomed and appreciated.

## Contents

- [Feature requests](#feature-requests)
- [Bug reports](#bug-reports)
- [Bug fixes](#bug-fixes)
- [Implement features](#implement-features)
- [Preparing Pull Requests](#preparing-pull-requests)

## Feature requests

We'd also like to hear about your thoughts and suggestions. Feel free to [submit them as issues](https://github.com/reportportal/agent-Python-RobotFramework/issues) and:

* Explain in detail how they should work.
* Keep the scope as narrow as possible. It will make it easier to implement.

## Bug reports

Report bugs for the agent in the [issue tracker](https://github.com/reportportal/agent-Python-RobotFramework/issues).

If you are reporting a new bug, please include:

* Your operating system name and version.
* Python interpreter version, installed libraries, reportportal-client, and agent-Python-RobotFramework version.
* Detailed steps to reproduce the bug.

## Bug fixes

Look through the [GitHub issues for bugs](https://github.com/reportportal/agent-Python-RobotFramework/labels/bug).

If you are going to fix any of existing bugs, assign that bug to yourself and specify preliminary milestones. Talk to [contributors](https://github.com/reportportal/agent-Python-RobotFramework/graphs/contributors) in case you need a consultancy regarding implementation.

## Implement features

Look through the [GitHub issues for enhancements](https://github.com/reportportal/agent-Python-RobotFramework/labels/enhancement).

Talk to [contributors](https://github.com/reportportal/agent-Python-RobotFramework/graphs/contributors) in case you need a consultancy regarding implementation.

## Preparing Pull Requests

What is a "pull request"? It informs the project's core developers about the changes you want to review and merge. Pull requests are stored on [GitHub servers](https://github.com/reportportal/agent-Python-RobotFramework/pulls). Once you send a pull request, we can discuss its potential modifications and even add more commits to it later on. There's an excellent tutorial on how Pull Requests work in the [GitHub Help Center](https://help.github.com/articles/using-pull-requests/).

Here is a simple overview below:

1. Fork the [agent-Python-RobotFramework GitHub repository](https://github.com/reportportal/agent-Python-RobotFramework).

2. Clone your fork locally using [git](https://git-scm.com/) and create a branch:

    ```sh
    $ git clone git@github.com:YOUR_GITHUB_USERNAME/agent-Python-RobotFramework.git
    $ cd agent-Python-RobotFramework
    # now, create your own branch off the "master":
    $ git checkout -b your-bugfix-branch-name
    ```

    If you need some help with Git, follow this quick start guide: https://git.wiki.kernel.org/index.php/QuickStart

3. Install [pre-commit](https://pre-commit.com) and its hook on the agent-Python-RobotFramework repo:

    **Note: pre-commit must be installed as admin, as it will not function otherwise**:

    ```sh
    $ pip install --user pre-commit
    $ pre-commit install
    ```

    Afterward `pre-commit` will run whenever you commit.

    [https://pre-commit.com](https://pre-commit.com) is a framework for managing and maintaining multi-language pre-commit hooks to ensure code-style and code formatting is consistent.

4. Install tox

    Tox is used to run all the tests and will automatically set up virtualenvs to run the tests in. (will implicitly use http://www.virtualenv.org/en/latest/):

    ```sh
    $ pip install tox
    ```

5. Run all the tests

    You need to have Python 3.10 available in your system. Now running tests is as simple as issuing this command:

    ```sh
    $ tox -e pep,py310
    ```

    This command will run tests via the "tox" tool against Python 3.10 and also perform code style checks.

6. You can now edit your local working copy and run the tests again as necessary. Please follow PEP-8 recommendations.

    You can pass different options to `tox`. For example, to run tests on Python 3.10 and pass options to pytest (e.g. enter pdb on failure) to pytest you can do:

    ```sh
    $ tox -e py310 -- --pdb
    ```

    Or to only run tests in a particular test module on Python 3.10:

    ```sh
    $ tox -e py310 -- tests/test_service.py
    ```

    When committing, `pre-commit` will re-format the files if necessary.

7. If instead of using `tox` you prefer to run the tests directly, then we suggest to create a virtual environment and use an editable installation with the `testing` extra:

    ```sh
    $ python3 -m venv .venv
    $ source .venv/bin/activate  # Linux
    $ .venv/Scripts/activate.bat  # Windows
    $ pip install -e ".[testing]"
    ```

    Afterwards, you can edit the files and run pytest normally:

    ```sh
    $ pytest tests/test_service.py
    ```

8. Commit and push once your tests pass and you are happy with your change(s):

    ```sh
    $ git commit -m "<commit message>"
    $ git push -u
    ```

9. Finally, submit a pull request through the GitHub website using this data:

    head-fork: YOUR_GITHUB_USERNAME/agent-Python-RobotFramework
    compare: your-branch-name

    base-fork: reportportal/agent-Python-RobotFramework
    base: master
