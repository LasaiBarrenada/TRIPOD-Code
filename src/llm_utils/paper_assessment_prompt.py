PAPER_ASSESSMENT_PROMPT = """
    We include a paper in our analysis if it is a project in which a multivariable prediction model is developed, updated or validated using any statistical or machine learning technique.
    It has to be in the study itself, not as a reference to another paper. For instance, a protocol that details how a prediction model will be run in a future study does not qualify.
    If the study itself uses any statistical model, such as a COX regression model, a multivariable logistic regression, for example, it should be included and will count as meeting the criteria. Any modality of prediction model is included, also include time series models, image-based models, and text-based models.
    Given a paper, decide if the paper would fit this criteria. You need to provide a a boolean match and a reason for whether the paper meets the criteria.
    Additionally, return a URL to the paper's code repository if it is provided and the paper is a match.
    The repository should be reported to contain the code used to conduct the study, do not report a repository for a library or tool that was developed external to the paper but was used in the study.
    Report only code repositories, not model or data repositories. If a user account link to a repository platform is reported instead of a repository, you can report it.
    Otherwise, always report the root of the repository, ignoring releases or subfolders that could be included in the link.
    If in the supplementary material or appendix section the code is reported, return 'Appendix' as the URL (but it has to explicitly mention that this supplemental contains the code). If a DOI is provided, format it in a resolvable URL form.
"""
