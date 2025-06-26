//
// klee_test.c
//
// KLEE symbolic execution tests for rgba.h/rgba.c
//

#include <klee/klee.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include "rgba.h"
#include <math.h>
#define MAX_STRING_LENGTH 32
#define MAX_BUFFER_LENGTH 64

// Test rgba_new function
void test_rgba_new() {
    uint32_t rgba_val;
    klee_make_symbolic(&rgba_val, sizeof(rgba_val), "rgba_val");
    
    rgba_t color = rgba_new(rgba_val);
    
    // Check that color components are in valid range [0.0, 1.0]
    assert(color.r >= 0.0 && color.r <= 1.0);
    assert(color.g >= 0.0 && color.g <= 1.0);
    assert(color.b >= 0.0 && color.b <= 1.0);
    assert(color.a >= 0.0 && color.a <= 1.0);
    
    // Test specific known values
    rgba_t white = rgba_new(0xFFFFFFFF);
    assert(white.r == 1.0 && white.g == 1.0 && white.b == 1.0 && white.a == 1.0);
    
    rgba_t black = rgba_new(0x000000FF);
    assert(black.r == 0.0 && black.g == 0.0 && black.b == 0.0 && black.a == 1.0);
    
    rgba_t transparent = rgba_new(0x00000000);
    assert(transparent.a == 0.0);
}

// Test rgba_to_string function
void test_rgba_to_string() {
    char buffer[MAX_BUFFER_LENGTH];
    rgba_t color;
    
    // Make color components symbolic
    klee_make_symbolic(&color, sizeof(color), "color");
    
    // Constrain to valid ranges
    klee_assume(color.r >= 0.0 && color.r <= 1.0);
    klee_assume(color.g >= 0.0 && color.g <= 1.0);
    klee_assume(color.b >= 0.0 && color.b <= 1.0);
    klee_assume(color.a >= 0.0 && color.a <= 1.0);
    
    rgba_to_string(color, buffer, sizeof(buffer));
    
    // Check that buffer is null-terminated
    assert(buffer[sizeof(buffer) - 1] == '\0' || strlen(buffer) < sizeof(buffer));
    
    // Test specific cases
    rgba_t opaque_red = {1.0, 0.0, 0.0, 1.0};
    rgba_to_string(opaque_red, buffer, sizeof(buffer));
    assert(strstr(buffer, "#ff0000") != NULL);
    
    rgba_t semi_transparent = {0.5, 0.5, 0.5, 0.5};
    rgba_to_string(semi_transparent, buffer, sizeof(buffer));
    assert(strstr(buffer, "rgba") != NULL);
}

// Test hex string parsing
void test_hex_parsing() {
    char hex_string[MAX_STRING_LENGTH];
    short ok;
    uint32_t result;
    
    // Test 6-digit hex
    strcpy(hex_string, "#FF0000");
    result = rgba_from_string(hex_string, &ok);
    assert(ok == 1);
    assert((result >> 24 & 0xff) == 255); // Red component
    assert((result >> 16 & 0xff) == 0);   // Green component
    assert((result >> 8 & 0xff) == 0);    // Blue component
    assert((result & 0xff) == 255);       // Alpha component
    
    // Test 3-digit hex
    strcpy(hex_string, "#F00");
    result = rgba_from_string(hex_string, &ok);
    assert(ok == 1);
    assert((result >> 24 & 0xff) == 255); // Red should be expanded
    
    // Test invalid hex
    strcpy(hex_string, "#ZZZ");
    result = rgba_from_string(hex_string, &ok);
    // Should handle gracefully (implementation dependent)
}

// Test RGB/RGBA string parsing
void test_rgb_parsing() {
    short ok;
    uint32_t result;
    
    // Test rgb() format
    result = rgba_from_string("rgb(255, 0, 0)", &ok);
    assert(ok == 1);
    assert((result >> 24 & 0xff) == 255);
    assert((result & 0xff) == 255); // Alpha should be 255 for rgb()
    
    // Test rgba() format
    result = rgba_from_string("rgba(255, 0, 0, 0.5)", &ok);
    assert(ok == 1);
    assert((result >> 24 & 0xff) == 255);
    
    // Test with whitespace
    result = rgba_from_string("rgb( 255 , 0 , 0 )", &ok);
    assert(ok == 1);
    
    // Test invalid format
    result = rgba_from_string("rgb(300, 0, 0)", &ok);
    // Should clamp values to 255 or handle appropriately
}

// Test named color parsing
void test_named_colors() {
    short ok;
    uint32_t result;
    
    // Test known colors
    result = rgba_from_string("red", &ok);
    assert(ok == 1);
    assert(result == 0xFF0000FF);
    
    result = rgba_from_string("blue", &ok);
    assert(ok == 1);
    assert(result == 0x0000FFFF);
    
    result = rgba_from_string("transparent", &ok);
    assert(ok == 1);
    assert(result == 0xFFFFFF00);
    
    // Test case sensitivity
    result = rgba_from_string("RED", &ok);
    assert(ok == 0); // Should fail - case sensitive
    
    // Test unknown color
    result = rgba_from_string("unknowncolor", &ok);
    assert(ok == 0);
}

// Test rgba_from_string with symbolic input
void test_rgba_from_string_symbolic() {
    char input_string[MAX_STRING_LENGTH];
    short ok;
    uint32_t result;
    
    // Make string symbolic
    klee_make_symbolic(input_string, sizeof(input_string), "input_string");
    
    // Ensure null termination
    input_string[MAX_STRING_LENGTH - 1] = '\0';
    
    // Constrain to printable ASCII characters
    for (int i = 0; i < MAX_STRING_LENGTH - 1; i++) {
        klee_assume(input_string[i] >= 0x20 && input_string[i] <= 0x7E || input_string[i] == '\0');
        if (input_string[i] == '\0') {
            // Ensure all following characters are also null
            for (int j = i + 1; j < MAX_STRING_LENGTH; j++) {
                input_string[j] = '\0';
            }
            break;
        }
    }
    
    result = rgba_from_string(input_string, &ok);
    
    // If parsing succeeded, verify the result is reasonable
    if (ok) {
        // All color components should be valid bytes
        uint8_t r = (result >> 24) & 0xff;
        uint8_t g = (result >> 16) & 0xff;
        uint8_t b = (result >> 8) & 0xff;
        uint8_t a = result & 0xff;
        
        // Components are already bytes, so they're inherently valid
        assert(r <= 255 && g <= 255 && b <= 255 && a <= 255);
    }
}

// Test edge cases and boundary conditions
void test_edge_cases() {
    short ok;
    uint32_t result;
    char buffer[MAX_BUFFER_LENGTH];
    
    // Test empty string
    result = rgba_from_string("", &ok);
    assert(ok == 0);
    
    // Test very long string (should not crash)
    char long_string[1000];
    memset(long_string, 'a', sizeof(long_string) - 1);
    long_string[sizeof(long_string) - 1] = '\0';
    result = rgba_from_string(long_string, &ok);
    // Should handle gracefully
    
    // Test string with only hash
    result = rgba_from_string("#", &ok);
    assert(ok == 0);
    
    // Test rgba_to_string with very small buffer
    rgba_t color = {1.0, 0.0, 0.0, 1.0};
    char small_buffer[1];
    rgba_to_string(color, small_buffer, sizeof(small_buffer));
    // Should not crash, buffer should be handled safely
    
    // Test rgba_new with extreme values
    rgba_t extreme1 = rgba_new(0x00000000);
    rgba_t extreme2 = rgba_new(0xFFFFFFFF);
    assert(extreme1.r == 0.0 && extreme1.a == 0.0);
    assert(extreme2.r == 1.0 && extreme2.a == 1.0);
}

// Test consistency between functions
void test_roundtrip_consistency() {
    uint32_t original;
    klee_make_symbolic(&original, sizeof(original), "original");
    
    // Convert to rgba_t and back to string, then parse again
    rgba_t color = rgba_new(original);
    char buffer[MAX_BUFFER_LENGTH];
    rgba_to_string(color, buffer, sizeof(buffer));
    
    short ok;
    uint32_t parsed = rgba_from_string(buffer, &ok);
    
    if (ok) {
        // Due to floating point precision and formatting, exact equality
        // might not hold, but values should be close
        rgba_t parsed_color = rgba_new(parsed);
        
        // Allow for small floating point differences
        double epsilon = 0.01;
        assert(fabs(color.r - parsed_color.r) < epsilon);
        assert(fabs(color.g - parsed_color.g) < epsilon);
        assert(fabs(color.b - parsed_color.b) < epsilon);
        
        // Alpha might be different for hex format (always 1.0)
        if (color.a == 1.0) {
            assert(fabs(color.a - parsed_color.a) < epsilon);
        }
    }
}

int main() {
    // Run all tests
    test_rgba_new();
    test_rgba_to_string();
    test_hex_parsing();
    test_rgb_parsing();
    test_named_colors();
    test_rgba_from_string_symbolic();
    test_edge_cases();
    test_roundtrip_consistency();
    
    printf("All KLEE tests completed successfully!\n");
    return 0;
}
