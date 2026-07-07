// a small dependency-free crc32 (used nowhere, just a rust toy sitting
// next to the real python download/convert pipeline).

const POLY: u32 = 0xEDB88320;

fn table() -> [u32; 256] {
    let mut table = [0u32; 256];
    let mut i = 0u32;
    while i < 256 {
        let mut c = i;
        let mut k = 0;
        while k < 8 {
            c = if c & 1 != 0 { POLY ^ (c >> 1) } else { c >> 1 };
            k += 1;
        }
        table[i as usize] = c;
        i += 1;
    }
    table
}

pub fn crc32(data: &[u8]) -> u32 {
    let table = table();
    let mut crc: u32 = 0xFFFFFFFF;
    for &byte in data {
        let idx = ((crc ^ byte as u32) & 0xFF) as usize;
        crc = table[idx] ^ (crc >> 8);
    }
    crc ^ 0xFFFFFFFF
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_vector() {
        // crc32("123456789") == 0xCBF43926, the standard check value.
        assert_eq!(crc32(b"123456789"), 0xCBF43926);
    }

    #[test]
    fn empty_input() {
        assert_eq!(crc32(b""), 0);
    }
}
