from pydantic import BaseModel, Field
from typing import Optional, Literal, List

CodeStatementLocation = Literal[
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "data_availability_section",
    "code_availability_section",
    "supplementary_material",
    "other",
]

CodingLanguage = Literal[
    "python",
    "r",
    "matlab",
    "sas",
    "cpp",
    "shell_bash",
    "sql",
    "other",
]


class PaperAssessment(BaseModel):
    """
    Structured assessment of whether a paper meets inclusion criteria
    for multivariable prediction model studies, with justification and
    associated code repository information if applicable.
    """

    is_match: bool = Field(
        ...,
        description="Whether the paper meets the inclusion criteria for a multivariable prediction model study.",
    )
    reason: str = Field(
        ...,
        description="Brief explanation justifying why the paper does or does not meet the criteria.",
    )
    country_first_author_institution: str = Field(
        ...,
        description=(
            "The country of origin based on the affiliation of the first author. Use the ISO 3166 standard name of the country in your response."
            "Return 'not reported' if the information is not found"
        ),
    )
    repo_url: Optional[str] = Field(
        ...,
        description=(
            "URL to the paper's code repository if the paper is a match. "
            "Use 'Appendix' if code is explicitly stated to be in supplementary materials"
        ),
    )
    code_statement_locations: Optional[List[CodeStatementLocation]] = Field(
        ...,
        description=(
            "All locations in the paper where a code availability statement appears if a repo_url is found. "
            "Use ['other'] if the code availability statement location does not fit the available categories"
        ),
    )
    code_statement_sentence: Optional[str] = Field(
        ...,
        description="If repo_url is found, the sentence introducing the repository url (without the url itself), eg. 'The code can be found here:'",
    )


class RepoAssessment(BaseModel):
    # Relevance
    is_empty: bool = Field(
        ...,
        description=(
            "Whether the repository is empty. Consider it empty if it contains no files, "
            "only empty files, or only a README file."
        ),
    )

    # README
    contains_readme: bool = Field(
        ...,
        description=(
            "Whether the repository contains usage/structure instructions (e.g., README.md/README.txt/README)."
        ),
    )
    readme_purpose_and_outputs: Optional[bool] = Field(
        ...,
        description=(
            "If contains_readme is True, whether the README provides an overview of the repository purpose "
            "and expected outputs. Do not return anything if contains_readme is False."
        ),
    )

    # Requirements
    contains_requirements: bool = Field(
        ...,
        description=(
            "Whether the repository specifies software dependencies either in a dedicated file "
            "(e.g., requirements.txt, environment.yml, pyproject.toml) or in the README."
        ),
    )
    requirements_dependency_versions: Optional[bool] = Field(
        ...,
        description=(
            "If contains_requirements is True, whether dependencies include version constraints "
            "(e.g., package==1.2.3, >=, ~=). Do not return anything if contains_requirements is False."
        ),
    )

    # License
    contains_license: bool = Field(
        ...,
        description="Whether the repository includes a license file describing usage permissions.",
    )

    # Documentation
    sufficient_code_documentation: bool = Field(
        ...,
        description=(
            "Whether the code contains sufficient inline comments/docstrings explaining key components "
            "so a user can understand the logic."
        ),
    )

    # Modularity
    is_modular_and_structured: bool = Field(
        ...,
        description=(
            "Whether code is organized into modular, reusable components (functions/classes/modules) "
            "rather than a few long scripts."
        ),
    )

    # Testing
    implements_tests: bool = Field(
        ...,
        description=(
            "Whether the repository includes tests (unit/functional), test files/scripts, or meaningful "
            "assertions verifying expected behavior."
        ),
    )

    # Reproducibility
    fixes_seed_if_stochastic: Optional[bool] = Field(
        ...,
        description=(
            "If the repository uses stochastic processes (e.g., random sampling, ML training), whether it "
            "sets fixed random seeds for reproducibility. Do not return anything if stochasticity is not applicable."
        ),
    )
    lists_hardware_requirements: bool = Field(
        ...,
        description="Whether hardware requirements (e.g., GPU/CPU/RAM) are stated anywhere in the repository.",
    )

    # Citation and Linking
    contains_link_to_paper: bool = Field(
        ...,
        description="Whether the repository includes a link (URL/DOI/arXiv/PubMed) to the associated paper.",
    )
    contains_citation: bool = Field(
        ...,
        description=(
            "Whether the repository provides a citation for the paper (e.g., plain text citation, BibTeX entry, "
            "CITATION.cff, or a LaTeX citation key)."
        ),
    )

    # Data
    includes_data_or_sample: bool = Field(
        ...,
        description=(
            "Whether the repository includes the original dataset or a sample/demo dataset sufficient to run "
            "or demonstrate the code."
        ),
    )

    # Free-text notes
    comments_and_explanations: Optional[str] = Field(
        ...,
        description=(
            "Additional comments about repository quality, strengths/weaknesses, and notable aspects not fully "
            "captured by the boolean fields."
        ),
    )

    # Languages
    coding_languages: Optional[List[CodingLanguage]] = Field(
        ...,
        description=(
            "If the repository contains code, return all programming languages used. "
            "Choose all that apply from: python, r, matlab, sas, cpp, shell_bash, sql, other. "
            "Use 'other' for languages that do not fit these categories. "
            "Do not return anything if there is no code in the repository."
        ),
    )
