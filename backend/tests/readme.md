Unit tests use pytest as the basic framework

conftest.py defines fixtures necessary for testing this flask app

Dependencies for testing: 

```
pip install pytest
pip install pytest-cov
pip install pytest-asyncio
```

To run all tests:

In command line under `/tests` directory type:

```
pytest
```

To show test coverage in command line:

```
pytest --cov=app
```

To generate detailed coverage report in html format:

```
pytest --cov=app --cov-report=html
```