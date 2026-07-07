// mirrors the format list from app/backend/converter.py, just as a rust toy.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AudioFormat {
    Mp3,
    Flac,
    Wav,
    M4a,
    Alac,
    Ogg,
    Opus,
}

impl AudioFormat {
    pub fn all() -> &'static [AudioFormat] {
        use AudioFormat::*;
        &[Mp3, Flac, Wav, M4a, Alac, Ogg, Opus]
    }

    pub fn extension(&self) -> &'static str {
        match self {
            AudioFormat::Mp3 => "mp3",
            AudioFormat::Flac => "flac",
            AudioFormat::Wav => "wav",
            AudioFormat::M4a => "m4a",
            AudioFormat::Alac => "alac",
            AudioFormat::Ogg => "ogg",
            AudioFormat::Opus => "opus",
        }
    }

    pub fn is_lossless(&self) -> bool {
        matches!(self, AudioFormat::Flac | AudioFormat::Wav | AudioFormat::Alac)
    }

    pub fn from_extension(ext: &str) -> Option<AudioFormat> {
        AudioFormat::all()
            .iter()
            .copied()
            .find(|f| f.extension().eq_ignore_ascii_case(ext))
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ImageFormat {
    Jpg,
    Png,
    Webp,
    Bmp,
    Gif,
    Tiff,
    Ico,
}

impl ImageFormat {
    pub fn all() -> &'static [ImageFormat] {
        use ImageFormat::*;
        &[Jpg, Png, Webp, Bmp, Gif, Tiff, Ico]
    }

    pub fn extension(&self) -> &'static str {
        match self {
            ImageFormat::Jpg => "jpg",
            ImageFormat::Png => "png",
            ImageFormat::Webp => "webp",
            ImageFormat::Bmp => "bmp",
            ImageFormat::Gif => "gif",
            ImageFormat::Tiff => "tiff",
            ImageFormat::Ico => "ico",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trips_extension() {
        for fmt in AudioFormat::all() {
            let ext = fmt.extension();
            assert_eq!(AudioFormat::from_extension(ext), Some(*fmt));
        }
    }

    #[test]
    fn flac_is_lossless() {
        assert!(AudioFormat::Flac.is_lossless());
        assert!(!AudioFormat::Mp3.is_lossless());
    }
}
