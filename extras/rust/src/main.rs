// extras/rust — decorative toy crate, not wired into the actual nexdex.space
// build (that's the C++ installer + python app). kept here as a small rust
// playground alongside the app. build with: cargo run --manifest-path Cargo.toml

mod formats;
mod tags;
mod checksum;
mod progress;
mod playlist;

fn banner() -> &'static str {
    r#"
 _ __   _____  ____| | _____  __
| '_ \ / _ \ \/ / _` |/ _ \ \/ /
| | | |  __/>  < (_| |  __/>  <
|_| |_|\___/_/\_\__,_|\___/_/\_\
        .space
"#
}

fn main() {
    println!("{}", banner());

    let track = tags::Tag {
        title: "MATADORA (Extended)".to_string(),
        artist: "SUKA.".to_string(),
        album: None,
        year: Some(2026),
        track_number: None,
    };
    println!("{}", track.describe());

    for fmt in formats::AudioFormat::all() {
        println!(
            "{:<6} lossless={}",
            fmt.extension(),
            fmt.is_lossless()
        );
    }

    let data = b"nexdex.space made by savsis";
    println!("crc32({:?}) = {:08x}", String::from_utf8_lossy(data), checksum::crc32(data));

    progress::simulate_download("MATADORA (Extended)");

    let mut pl = playlist::Playlist::new();
    pl.add(playlist::Track {
        tag: track.clone(),
        path: "downloads/MATADORA (Extended).flac".to_string(),
        duration_secs: 222,
    });
    println!(
        "playlist: {} track(s), total {}",
        pl.len(),
        playlist::Playlist::format_duration(pl.total_duration_secs())
    );

    println!("made by savsis with <3");
}
