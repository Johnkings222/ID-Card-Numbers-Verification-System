#!/usr/bin/env python3
"""
Test script for Chinese ID Card verification logic
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from id_card_verifier import ChineseIDVerifier


def test_id_verification():
    """Test various ID numbers"""

    test_cases = [
        # (ID Number, Expected Valid, Description)
        ("11010519491231002X", True, "Valid Beijing ID"),
        ("440524198001010013", True, "Valid Guangdong ID (1980)"),
        ("510102198901010017", True, "Valid Sichuan ID (1989)"),
        ("12345678901234567", False, "Too short (17 digits)"),
        ("1234567890123456789", False, "Too long (19 digits)"),
        ("11010519491231002Y", False, "Invalid checksum (Y instead of X)"),
        ("110105194913310020", False, "Invalid date (month 13)"),
        ("11010519491232002X", False, "Invalid date (day 32)"),
        ("ABCDEF19491231002X", False, "Non-numeric address code"),
        ("11010519491231ABCX", False, "Non-numeric sequence code"),
    ]

    print("=" * 70)
    print("Chinese ID Card Verification Test")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for id_number, expected_valid, description in test_cases:
        is_valid, message = ChineseIDVerifier.verify_id(id_number)

        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        result = "Valid" if is_valid else f"Invalid: {message}"

        if is_valid == expected_valid:
            passed += 1
        else:
            failed += 1

        print(f"{status} | {description}")
        print(f"       ID: {id_number}")
        print(f"       Expected: {'Valid' if expected_valid else 'Invalid'}")
        print(f"       Got: {result}")
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 70)

    return failed == 0


def test_checksum_calculation():
    """Test checksum calculation specifically"""

    print("\n" + "=" * 70)
    print("Checksum Calculation Test")
    print("=" * 70)
    print()

    # Test with known ID
    id_number = "11010519491231002X"
    first_17 = id_number[:17]

    # Calculate checksum manually
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    checksum_map = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    weighted_sum = sum(int(first_17[i]) * weights[i] for i in range(17))
    checksum_index = weighted_sum % 11
    expected_checksum = checksum_map[checksum_index]
    actual_checksum = id_number[17]

    print(f"ID Number: {id_number}")
    print(f"First 17 digits: {first_17}")
    print(f"Weighted sum: {weighted_sum}")
    print(f"Checksum index (sum % 11): {checksum_index}")
    print(f"Expected checksum: {expected_checksum}")
    print(f"Actual checksum: {actual_checksum}")
    print(f"Match: {'✅ YES' if expected_checksum == actual_checksum else '❌ NO'}")
    print()

    return expected_checksum == actual_checksum


def test_extraction():
    """Test ID number extraction from text"""

    print("=" * 70)
    print("ID Extraction Test")
    print("=" * 70)
    print()

    test_texts = [
        ("姓名：张三 身份证号：11010519491231002X", "11010519491231002X"),
        ("ID: 440524188001010014", "440524188001010014"),
        ("身份证 51010219890101001X 有效期", "51010219890101001X"),
        ("No ID number here", None),
        ("Short number: 12345678901234567", None),  # Only 17 digits
    ]

    for text, expected_id in test_texts:
        extracted_id = ChineseIDVerifier.extract_id_number(text)
        match = extracted_id == expected_id
        status = "✅ PASS" if match else "❌ FAIL"

        print(f"{status}")
        print(f"  Text: {text}")
        print(f"  Expected: {expected_id}")
        print(f"  Extracted: {extracted_id}")
        print()


def main():
    """Run all tests"""
    print("\n🧪 Running Chinese ID Card Verification Tests\n")

    # Run tests
    test_extraction()
    test_passed = test_id_verification()
    checksum_passed = test_checksum_calculation()

    print("\n" + "=" * 70)
    if test_passed and checksum_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
