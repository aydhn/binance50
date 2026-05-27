from typing import Any


class SklearnVotingSkeletonAdapter:
    def availability_report(self) -> dict[str, Any]:
        return {"status": "skeleton_only"}

    def explain_soft_voting_contract(self) -> dict[str, Any]:
        return {"description": "Simulates soft voting by averaging probabilities"}

    def validate_probabilities_for_soft_voting(self, predictions: list[Any]) -> None:
        pass

    def build_soft_voting_metadata(
        self, predictions: list[Any], weights: dict[str, float]
    ) -> dict[str, Any]:
        return {"weights": weights}
