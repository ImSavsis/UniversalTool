// extras/rust — decorative toy: a tiny in-memory playlist model, echoing
// the shape of data/history.json (backend/history.py) but with no I/O.

use crate::tags::Tag;

#[derive(Debug, Clone)]
pub struct Track {
    pub tag: Tag,
    pub path: String,
    pub duration_secs: u32,
}

#[derive(Debug, Default)]
pub struct Playlist {
    tracks: Vec<Track>,
}

impl Playlist {
    pub fn new() -> Self {
        Playlist { tracks: Vec::new() }
    }

    pub fn add(&mut self, track: Track) {
        self.tracks.push(track);
    }

    pub fn len(&self) -> usize {
        self.tracks.len()
    }

    pub fn is_empty(&self) -> bool {
        self.tracks.is_empty()
    }

    pub fn total_duration_secs(&self) -> u32 {
        self.tracks.iter().map(|t| t.duration_secs).sum()
    }

    pub fn by_artist(&self, artist: &str) -> Vec<&Track> {
        self.tracks
            .iter()
            .filter(|t| t.tag.artist.eq_ignore_ascii_case(artist))
            .collect()
    }

    pub fn sorted_by_title(&self) -> Vec<&Track> {
        let mut sorted: Vec<&Track> = self.tracks.iter().collect();
        sorted.sort_by(|a, b| a.tag.title.cmp(&b.tag.title));
        sorted
    }

    pub fn longest(&self) -> Option<&Track> {
        self.tracks.iter().max_by_key(|t| t.duration_secs)
    }

    pub fn format_duration(total_secs: u32) -> String {
        let hours = total_secs / 3600;
        let minutes = (total_secs % 3600) / 60;
        let seconds = total_secs % 60;
        if hours > 0 {
            format!("{}:{:02}:{:02}", hours, minutes, seconds)
        } else {
            format!("{}:{:02}", minutes, seconds)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tags::TagBuilder;

    fn sample_track(title: &str, artist: &str, secs: u32) -> Track {
        Track {
            tag: TagBuilder::new(title, artist).build(),
            path: format!("downloads/{}.flac", title),
            duration_secs: secs,
        }
    }

    #[test]
    fn total_duration_sums_all_tracks() {
        let mut pl = Playlist::new();
        pl.add(sample_track("A", "X", 100));
        pl.add(sample_track("B", "Y", 200));
        assert_eq!(pl.total_duration_secs(), 300);
    }

    #[test]
    fn filters_by_artist_case_insensitively() {
        let mut pl = Playlist::new();
        pl.add(sample_track("A", "SUKA.", 100));
        pl.add(sample_track("B", "suka.", 50));
        pl.add(sample_track("C", "Someone Else", 10));
        assert_eq!(pl.by_artist("suka.").len(), 2);
    }

    #[test]
    fn finds_longest_track() {
        let mut pl = Playlist::new();
        pl.add(sample_track("Short", "X", 60));
        pl.add(sample_track("Long", "X", 600));
        assert_eq!(pl.longest().unwrap().tag.title, "Long");
    }

    #[test]
    fn formats_duration_with_and_without_hours() {
        assert_eq!(Playlist::format_duration(65), "1:05");
        assert_eq!(Playlist::format_duration(3665), "1:01:05");
    }
}
