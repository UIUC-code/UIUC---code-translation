use std::env;
use std::process;

fn main() {
    // Collect command-line arguments
    let args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        eprintln!("Usage: {} <string1> <string2>", args[0]);
        process::exit(1);
    }

    let a = &args[1];
    let b = &args[2];

    // Mimic C strcmp: returns 0 if equal, <0 if a<b, >0 if a>b
    let result = strcmp_like(a, b);

    println!("{}", result);
}

// C-like strcmp behavior
fn strcmp_like(a: &str, b: &str) -> i32 {
    for (ac, bc) in a.bytes().zip(b.bytes()) {
        if ac != bc {
            return ac as i32 - bc as i32;
        }
    }
    a.len() as i32 - b.len() as i32
}
