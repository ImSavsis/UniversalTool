// extras/cpp — decorative, separate from installer/installer.cpp (the real,
// functional C++ source). a tiny header-only audio-tag toy, mirroring
// app/backend/metadata.py in spirit.
#pragma once

#include <string>
#include <optional>
#include <sstream>
#include <vector>

namespace nexdex {

struct AudioTag {
    std::string title;
    std::string artist;
    std::optional<std::string> album;
    std::optional<int> year;
    std::optional<int> trackNumber;

    bool isComplete() const {
        return !title.empty() && !artist.empty();
    }

    std::string describe() const {
        std::ostringstream out;
        out << artist << " -- " << title;
        if (album) out << " [" << *album << "]";
        if (year) out << " (" << *year << ")";
        if (trackNumber) out << " track #" << *trackNumber;
        return out.str();
    }
};

class AudioTagBuilder {
public:
    AudioTagBuilder(std::string title, std::string artist) {
        tag_.title = std::move(title);
        tag_.artist = std::move(artist);
    }

    AudioTagBuilder& album(std::string album) {
        tag_.album = std::move(album);
        return *this;
    }

    AudioTagBuilder& year(int year) {
        tag_.year = year;
        return *this;
    }

    AudioTagBuilder& trackNumber(int n) {
        tag_.trackNumber = n;
        return *this;
    }

    AudioTag build() const {
        return tag_;
    }

private:
    AudioTag tag_;
};

inline std::vector<std::string> knownExtensions() {
    return {"mp3", "flac", "wav", "m4a", "alac", "ogg", "opus"};
}

}  // namespace nexdex
