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
    is_empty: bool

    # README
    contains_readme: bool
    readme_purpose_and_outputs: Optional[bool]

    # Requirements
    contains_requirements: bool
    requirements_dependency_versions: Optional[bool]

    # License
    contains_license: bool

    # Documentation
    sufficient_code_documentation: bool

    # Modularity
    is_modular_and_structured: bool

    # Testing
    implements_tests: bool

    # Reproducibility
    fixes_seed_if_stochastic: Optional[bool]
    lists_hardware_requirements: bool

    # Citation and Linking
    contains_link_to_paper: bool
    contains_citation: bool

    # Data
    includes_data_or_sample: bool
