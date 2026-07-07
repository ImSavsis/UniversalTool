// a tiny stand-in for the tag struct app/backend/metadata.py works with —
// decorative, the real read/write logic lives in python (mutagen).

#[derive(Debug, Clone)]
pub struct Tag {
    pub title: String,
    pub artist: String,
    pub album: Option<String>,
    pub year: Option<u32>,
    pub track_number: Option<u32>,
}

impl Tag {
    pub fn describe(&self) -> String {
        let mut parts = vec![format!("{} — {}", self.artist, self.title)];

        if let Some(album) = &self.album {
            parts.push(format!("[{}]", album));
        }
        if let Some(year) = self.year {
            parts.push(format!("({})", year));
        }
        if let Some(track) = self.track_number {
            parts.push(format!("track #{}", track));
        }

        parts.join(" ")
    }

    pub fn is_complete(&self) -> bool {
        !self.title.is_empty() && !self.artist.is_empty()
    }
}

pub struct TagBuilder {
    tag: Tag,
}

impl TagBuilder {
    pub fn new(title: impl Into<String>, artist: impl Into<String>) -> Self {
        TagBuilder {
            tag: Tag {
                title: title.into(),
                artist: artist.into(),
                album: None,
                year: None,
                track_number: None,
            },
        }
    }

    pub fn album(mut self, album: impl Into<String>) -> Self {
        self.tag.album = Some(album.into());
        self
    }

    pub fn year(mut self, year: u32) -> Self {
        self.tag.year = Some(year);
        self
    }

    pub fn track_number(mut self, n: u32) -> Self {
        self.tag.track_number = Some(n);
        self
    }

    pub fn build(self) -> Tag {
        self.tag
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builder_produces_expected_tag() {
        let tag = TagBuilder::new("Aria Math", "Logan Feece")
            .album("C418 covers")
            .year(2024)
            .build();

        assert!(tag.is_complete());
        assert_eq!(tag.describe(), "Logan Feece — Aria Math [C418 covers] (2024)");
    }
}
