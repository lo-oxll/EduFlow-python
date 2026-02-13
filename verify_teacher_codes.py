#!/usr/bin/env python3
"""
Test script to verify teacher code generation works correctly
"""

import time
import random
import string
import sys

def generate_teacher_code():
    """Generate a unique teacher code in format TCHR-XXXXX-XXXX"""
    # Use nanosecond timestamp for maximum uniqueness
    timestamp = str(int(time.time() * 1000000000))[-5:]
    # Generate 4-character random alphanumeric string with more entropy
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TCHR-{timestamp}-{random_str}"

def test_code_generation():
    print("Testing teacher code generation...")
    
    # Generate multiple codes to test uniqueness
    codes = []
    for i in range(10):
        code = generate_teacher_code()
        codes.append(code)
        print(f"Code {i+1}: {code}")
        
        # Verify format
        assert code.startswith('TCHR-'), f"Code should start with TCHR-, got {code}"
        assert len(code) == 14, f"Code should be 14 characters long, got {len(code)} characters"
        assert code[5] == '-', f"Code should have dash at position 5, got {code}"
        assert code[11] == '-', f"Code should have dash at position 11, got {code}"
    
    # Check uniqueness
    unique_codes = set(codes)
    assert len(unique_codes) == len(codes), f"Generated codes should be unique. Got {len(codes)} codes but only {len(unique_codes)} unique"
    
    print(f"✓ Generated {len(codes)} unique codes successfully!")
    print("✓ All codes follow TCHR-XXXXX-XXXX format")
    return True

def test_code_format_validation():
    print("\nTesting code format validation...")
    
    import re
    pattern = re.compile(r'^TCHR-\d{5}-[A-Z0-9]{4}$')
    
    # Test valid codes
    valid_codes = [
        "TCHR-12345-ABCD",
        "TCHR-98765-ZYXW",
        "TCHR-00001-1234",
        generate_teacher_code()  # Test a real generated code
    ]
    
    print("Valid codes:")
    for code in valid_codes:
        is_valid = bool(pattern.match(code))
        print(f"  {code}: {'✓' if is_valid else '✗'}")
        assert is_valid, f"Valid code {code} should match pattern"
    
    # Test invalid codes
    invalid_codes = [
        "TCHR-1234-ABCD",      # Too short
        "TCHR-123456-ABCD",    # Too long  
        "TEACHER-12345-ABCD",  # Wrong prefix
        "TCHR-12345-ABCDE",    # Wrong suffix length
        "TCHR-ABCDE-1234",     # Non-numeric middle part
        "tchr-12345-abcd",     # Lowercase
        "TCHR-12345-abcd"      # Lowercase suffix
    ]
    
    print("Invalid codes:")
    for code in invalid_codes:
        is_valid = bool(pattern.match(code))
        print(f"  {code}: {'✗' if not is_valid else '✓'}")
        assert not is_valid, f"Invalid code {code} should not match pattern"
    
    print("✓ Code format validation test passed!")
    return True

if __name__ == "__main__":
    print("=== Teacher Code Generation Verification ===\n")
    
    try:
        success = True
        success &= test_code_generation()
        success &= test_code_format_validation()
        
        print(f"\n=== Test Summary ===")
        if success:
            print("✓ All tests passed!")
            print("\nTeacher code generation is working correctly:")
            print("- Codes are generated in TCHR-XXXXX-XXXX format")
            print("- Each code is unique (tested with 10 generations)")
            print("- Format validation works properly")
            print("- Ready for integration with the school management system")
        else:
            print("✗ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
    
    sys.exit(0)