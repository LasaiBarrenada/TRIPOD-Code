REPO_ASSESSMENT_PROMPT = """
    You will be provided the tree of a repository and its code. Use it to assess the quality of the repository.
    You should return a boolean for each of these categories:
    - is_empty: is the repository empty? A repository is considered empty if it contains no files, only files that are empty, or only a README file.
    - contains_readme: does the repository contain instructions on how the code is structured and how to use it (such as a README.md, README.txt or README file)?
    - readme_purpose_and_outputs: (don't return anything for this field if contains_readme is false) do these instructions provide an overview of the purpose of the code repository, and its expected outputs?
    - contains_requirements: does the repository specify the software dependencies used to run the code in a separate file (for example as a requirements.txt, environment.yml, or pyproject.toml file) or in the README file?
    - requirements_dependency_versions: (don't return anything for this field if requirements_dependency_versions is false) does the requirements file specify dependency version requirements?
    - contains_license: does the repository include a license file specifying how others can use this code?
    - sufficient_code_documentation: does the code include sufficient inline documentation or comments explaining the purpose and functionality of key components of the code for a user to understand its logic?
    - is_modular_and_structured: is the code organized into modular, reusable components using functions and classes where appropriate, rather than consisting of a single or a few long scripts?
    - implements_tests: does the repository include unit tests or functional tests to verify that the code works as intended? This may include test scripts, test files, or embedded assertions that check whether inputs and outputs behave as expected.
    - fixes_seed_if_stochastic: (If applicable, don't return anything if the repository doesn't use stochastic processes) if using stochastic processes (e.g., random number generation, machine learning models), is the repository setting fixed random seeds to ensure reproducibility?
    - hardware_requirements: are hardware requirements listed?
    - contains_link_to_paper: does the repository contain a link to the paper it was used for?
    - contains_citation: does the repository include a citation to the paper, in the format of a latex citation key or in plain text?
    - includes_data_or_sample: does the repository include either the original dataset or a sample dataset for demonstration purposes?
    - comments_and_explanations: provide additional comments and explanations regarding the repository's quality, strengths, weaknesses, or any notable aspects that may not be fully captured by the boolean assessments above.
    - coding_languages: (if the repository contains code) list all programming languages used in the repository.
    """
