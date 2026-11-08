from app.verification.numerical_validator import (
    NumericalValidator,
)


def test_matching_numbers():

    result = NumericalValidator().validate(
        claim="The reduction was 15%.",
        evidence="The reported reduction was 15%.",
    )

    assert result["passed"] is True


def test_mismatched_numbers():

    result = NumericalValidator().validate(
        claim="The reduction was 25%.",
        evidence="The reported reduction was 15%.",
    )

    assert result["passed"] is False
    assert "25%" in result["missing_numbers"]