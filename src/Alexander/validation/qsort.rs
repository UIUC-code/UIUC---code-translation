use crate::*;

pub fn swap(a: Option<&mut i32>, b: Option<&mut i32>) {
    // Check if both `a` and `b` are Some (i.e., not None)
    if let (Some(a), Some(b)) = (a, b) {
        let t = *a;  // Dereference `a` to get the value
        *a = *b;    // Assign the value of `b` to `a`
        *b = t;     // Assign the value of `t` to `b`
    }
    // If either `a` or `b` is None, do nothing (equivalent to C's NULL pointer check)
}
pub fn partition(arr: Option<&mut [i32]>, low: i32, high: i32) -> i32 {
    // Check if `arr` is None (equivalent to checking for NULL in C)
    if arr.is_none() {
        return -1;  // Return -1 to indicate an error (invalid input)
    }

    // Unwrap safely: If `arr` is `Some`, it will be a valid mutable slice reference
    let arr = arr.unwrap();

    let pivot = arr[high as usize];
    let mut i = low - 1;

    for j in low..high {
        if arr[j as usize] <= pivot {
            i += 1;
            // Swap arr[i] and arr[j] using a temporary variable
            let temp = arr[i as usize];
            arr[i as usize] = arr[j as usize];
            arr[j as usize] = temp;
        }
    }

    // Swap arr[i + 1] and arr[high] using a temporary variable
    let temp = arr[(i + 1) as usize];
    arr[(i + 1) as usize] = arr[high as usize];
    arr[high as usize] = temp;

    i + 1
}
pub fn quickSort(arr: Option<&mut [i32]>, low: i32, high: i32) {
    // Check if `arr` is None (equivalent to checking for NULL in C)
    if arr.is_none() {
        return;
    }

    // Unwrap safely: If `arr` is `Some`, it will be a valid mutable slice reference
    let arr = arr.unwrap();

    if low < high {
        let i = partition(Some(arr), low, high);
        quickSort(Some(arr), low, i - 1);
        quickSort(Some(arr), i + 1, high);
    }
}