## Contributing

Thanks for wanting to contribute to KitchenOwl!

### Where do I go from here?

So you want to contribute to KitchenOwl? Great!

If you have noticed a bug, please [create an issue](https://github.com/TomBursch/KitchenOwl/issues/new) for it before starting any work on a pull request.

### Fork & create a branch

If there is something you want to fix or add, the first step is to fork this repository.

Next is to create a new branch with an appropriate name. The general format that should be used is

```
git checkout -b '<type>/<description>'
```

The `type` is the same as the `type` that you will use for [your commit message](https://www.conventionalcommits.org/en/v1.0.0/#summary).

The `description` is a descriptive summary of the change the PR will make.

### General Rules

- All PRs should be rebased (with main) and commits squashed prior to the final merge process
- One PR per fix or feature

### Requirements
- Python 3.11+

### Setup & Install
- Create a python environment `python3 -m venv venv`
- Activate your python environment `source venv/bin/activate` (environment can be deactivated with `deactivate`)
- Install dependencies `pip3 install -r requirements.txt`
- Initialize/Upgrade the SQLite database with `flask db upgrade`
- Initialize/Upgrade requirements for the recipe scraper `python -c "import nltk; nltk.download('averaged_perceptron_tagger')"`
- Run debug server with `python3 wsgi.py` or without debugging `flask run`
- The backend should be reachable at `localhost:5000`

### Git Commit Message Style

This project uses the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) format.

Example commit messages:

```
chore: update gqlgen dependency to v2.6.0
docs(README): add new contributing section
fix: remove debug log statements
```
