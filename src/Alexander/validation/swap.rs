use std::fs;

mod qsort;

// Swap function from qsort.rs module
use qsort::swap;

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

fn bytes_to_i32_array_le(bytes: &[u8]) -> Vec<i32> {
    bytes.chunks_exact(4)
        .map(|chunk| {
            i32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]])
        })
        .collect()
}

fn main() -> std::io::Result<()> {
    let dir_path = "data_out_swap";
    let entries = fs::read_dir(dir_path)?;
    
    for entry in entries {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() {
            let content = fs::read_to_string(&path)?;
            
            let a_str = extract_value(&content, "a");
            let b_str = extract_value(&content, "b");
            
            if let (Some(a_str), Some(b_str)) = (a_str, b_str) {
                let a_bytes = parse_bytes(&a_str);
                let b_bytes = parse_bytes(&b_str);
                
                if let (Some(a_bytes), Some(b_bytes)) = (a_bytes, b_bytes) {
                    let mut a_arr = bytes_to_i32_array_le(&a_bytes);
                    let mut b_arr = bytes_to_i32_array_le(&b_bytes);
                    
                    print!("Input a: [");
                    for (i, &val) in a_arr.iter().enumerate() {
                        if i > 0 { print!(", "); }
                        print!("{}", val);
                    }
                    println!("]");
                    
                    print!("Input b: [");
                    for (i, &val) in b_arr.iter().enumerate() {
                        if i > 0 { print!(", "); }
                        print!("{}", val);
                    }
                    println!("]");
                    
                    // Call swap on each corresponding pair of elements
                    let min_len = a_arr.len().min(b_arr.len());
                    for i in 0..min_len {
                        swap(Some(&mut a_arr[i]), Some(&mut b_arr[i]));
                    }
                    
                    print!("Output a: [");
                    for (i, &val) in a_arr.iter().enumerate() {
                        if i > 0 { print!(", "); }
                        print!("{}", val);
                    }
                    println!("]");
                    
                    print!("Output b: [");
                    for (i, &val) in b_arr.iter().enumerate() {
                        if i > 0 { print!(", "); }
                        print!("{}", val);
                    }
                    println!("]");
                }
            }
        }
    }
    
    Ok(())
}
