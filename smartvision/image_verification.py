from dataclasses import dataclass
from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity


# Tune these values after testing with your own reference/candidate images.
HASH_MAX_DISTANCE = 12       # lower is more similar
SSIM_MIN_SCORE = 0.62        # higher is more similar
ORB_MIN_GOOD_MATCHES = 10    # more matched keypoints is better
ORB_RATIO_TEST = 0.75


@dataclass
class VerificationResult:
    accepted: bool
    hash_distance: int
    ssim_score: float
    orb_good_matches: int
    hash_passed: bool
    ssim_passed: bool
    orb_passed: bool
    message: str


def _open_rgb(path: str) -> Image.Image:
    image = Image.open(path)
    return image.convert("RGB")


def _prepare_gray(image: Image.Image, size=(320, 320)) -> np.ndarray:
    image = image.convert("L").resize(size, Image.Resampling.LANCZOS)
    return np.asarray(image, dtype=np.uint8)


def _orb_match_count(reference: np.ndarray, candidate: np.ndarray) -> int:
    detector = cv2.ORB_create(nfeatures=1200)
    keypoints1, descriptors1 = detector.detectAndCompute(reference, None)
    keypoints2, descriptors2 = detector.detectAndCompute(candidate, None)

    if descriptors1 is None or descriptors2 is None:
        return 0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    pairs = matcher.knnMatch(descriptors1, descriptors2, k=2)

    good = []
    for pair in pairs:
        if len(pair) == 2:
            first, second = pair
            if first.distance < ORB_RATIO_TEST * second.distance:
                good.append(first)

    return len(good)


def compare_images(reference_path: str, candidate_path: str) -> VerificationResult:
    """Compare two images and accept when at least two of three checks pass."""
    if not Path(reference_path).is_file():
        raise FileNotFoundError(f"Reference image not found: {reference_path}")
    if not Path(candidate_path).is_file():
        raise FileNotFoundError(f"Candidate image not found: {candidate_path}")

    reference_pil = _open_rgb(reference_path)
    candidate_pil = _open_rgb(candidate_path)

    hash_distance = int(imagehash.phash(reference_pil) - imagehash.phash(candidate_pil))

    reference_gray = _prepare_gray(reference_pil)
    candidate_gray = _prepare_gray(candidate_pil)
    ssim_score = float(structural_similarity(reference_gray, candidate_gray, data_range=255))

    orb_matches = _orb_match_count(reference_gray, candidate_gray)

    hash_passed = hash_distance <= HASH_MAX_DISTANCE
    ssim_passed = ssim_score >= SSIM_MIN_SCORE
    orb_passed = orb_matches >= ORB_MIN_GOOD_MATCHES

    passed_count = sum((hash_passed, ssim_passed, orb_passed))
    accepted = passed_count >= 2

    if accepted:
        message = f"Image accepted: {passed_count}/3 similarity checks passed."
    else:
        message = f"Image rejected: only {passed_count}/3 similarity checks passed."

    return VerificationResult(
        accepted=accepted,
        hash_distance=hash_distance,
        ssim_score=ssim_score,
        orb_good_matches=orb_matches,
        hash_passed=hash_passed,
        ssim_passed=ssim_passed,
        orb_passed=orb_passed,
        message=message,
    )
