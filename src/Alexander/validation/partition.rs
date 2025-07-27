use std::fs;

mod qsort;

fn extract_value(json: &str, key: &str) -> Option<String> {
    let key_pattern = format!("\"{}\"", key);
    
    let key_pos = if let Some(pos) = json.find(&key_pattern) {
        pos + key_pattern.len()
    } else if let Some(pos) = json.find(key) {
        pos + key.len()
    } else {
        return None;
    };
    
    let remaining = &json[key_pos..];
    
    // Skip whitespace and colon
    let mut chars = remaining.chars();
    let mut start_pos = 0;
    for ch in chars.by_ref() {
        if ch == ':' || ch.is_whitespace() {
            start_pos += ch.len_utf8();
        } else {
            break;
        }
    }
    
    let value_part = &remaining[start_pos..];
    
    // Expect opening quote
    if !value_part.starts_with('"') {
        return None;
    }
    
    let value_part = &value_part[1..]; // Skip opening quote
    
    if let Some(end_pos) = value_part.find('"') {
        Some(value_part[..end_pos].to_string())
    } else {
        None
    }
}

fn parse_bytes(s: &str) -> Option<Vec<u8>> {
    let mut ptr = s;
    
    // Handle format: "b'\\x00\\x01...'"
    if ptr.starts_with("b'") && ptr.ends_with('\'') {
        ptr = &ptr[2..ptr.len()-1]; // Remove "b'" and trailing "'"
    }
    
    let mut bytes = Vec::new();
    let mut chars = ptr.chars().peekable();
    
    while let Some(ch) = chars.next() {
        if ch == '\\' && chars.peek() == Some(&'x') {
            chars.next(); // consume 'x'
            
            // Get next two hex digits
            let hex1 = chars.next()?;
            let hex2 = chars.next()?;
            
            let hex_str = format!("{}{}", hex1, hex2);
            let byte_val = u8::from_str_radix(&hex_str, 16).ok()?;
            bytes.push(byte_val);
        }
    }
    
    Some(bytes)
}

fn bytes_to_i32_le(bytes: &[u8]) -> i32 {
    let mut result = 0i32;
    for (i, &byte) in bytes.iter().enumerate() {
        result |= (byte as i32) << (i * 8);
    }
    result
}

fn bytes_to_i32_array_le(bytes: &[u8]) -> Vec<i32> {
    bytes.chunks_exact(4)
        .map(|chunk| {
            i32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]])
        })
        .collect()
}

// Partition function from qsort.rs module
use qsort::partition;

fn main() -> std::io::Result<()> {
    let dir_path = "data_out_partition";
    let entries = fs::read_dir(dir_path)?;
    
    for entry in entries {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() {
            let content = fs::read_to_string(&path)?;
            
            let arr_str = extract_value(&content, "arr");
            let low_str = extract_value(&content, "low");
            let high_str = extract_value(&content, "high");
            
            if let (Some(arr_str), Some(low_str), Some(high_str)) = (arr_str, low_str, high_str) {
                let arr_bytes = parse_bytes(&arr_str);
                let low_bytes = parse_bytes(&low_str);
                let high_bytes = parse_bytes(&high_str);
                
                if let (Some(arr_bytes), Some(low_bytes), Some(high_bytes)) = (arr_bytes, low_bytes, high_bytes) {
                    let low = bytes_to_i32_le(&low_bytes);
                    let high = bytes_to_i32_le(&high_bytes);
                    let mut arr = bytes_to_i32_array_le(&arr_bytes);
                    
                    print!("Input array: [");
                    for (i, &val) in arr.iter().enumerate() {
                        if i > 0 { print!(", "); }
                        print!("{}", val);
                    }
                    println!("]");
                    
                    println!("Sorting range: low={}, high={}", low, high);
                    
                    let pivot_index = partition(Some(&mut arr), low, high);
                    
                    println!("Pivot index: {}", pivot_index);
                    println!();
                }
            }
        }
    }
    
    Ok(())
}
