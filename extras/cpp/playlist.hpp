// extras/cpp — decorative. mirrors extras/rust/src/playlist.rs, just in
// C++: a tiny in-memory playlist model with no real I/O.
#pragma once

#include <vector>
#include <string>
#include <algorithm>
#include <optional>
#include <numeric>
#include "audio_meta.hpp"

namespace nexdex {

struct Track {
    AudioTag tag;
    std::string path;
    int durationSecs = 0;
};

class Playlist {
public:
    void add(Track track) {
        tracks_.push_back(std::move(track));
    }

    size_t size() const { return tracks_.size(); }
    bool empty() const { return tracks_.empty(); }

    int totalDurationSecs() const {
        return std::accumulate(
            tracks_.begin(), tracks_.end(), 0,
            [](int sum, const Track& t) { return sum + t.durationSecs; });
    }

    std::vector<const Track*> byArtist(const std::string& artist) const {
        std::vector<const Track*> result;
        for (const auto& t : tracks_) {
            if (equalsIgnoreCase(t.tag.artist, artist)) {
                result.push_back(&t);
            }
        }
        return result;
    }

    std::optional<const Track*> longest() const {
        if (tracks_.empty()) return std::nullopt;
        auto it = std::max_element(
            tracks_.begin(), tracks_.end(),
            [](const Track& a, const Track& b) { return a.durationSecs < b.durationSecs; });
        return &(*it);
    }

    static std::string formatDuration(int totalSecs) {
        int hours = totalSecs / 3600;
        int minutes = (totalSecs % 3600) / 60;
        int seconds = totalSecs % 60;

        char buf[32];
        if (hours > 0) {
            snprintf(buf, sizeof(buf), "%d:%02d:%02d", hours, minutes, seconds);
        } else {
            snprintf(buf, sizeof(buf), "%d:%02d", minutes, seconds);
        }
        return std::string(buf);
    }

private:
    static bool equalsIgnoreCase(const std::string& a, const std::string& b) {
        if (a.size() != b.size()) return false;
        return std::equal(a.begin(), a.end(), b.begin(), [](char x, char y) {
            return std::tolower(static_cast<unsigned char>(x)) ==
                   std::tolower(static_cast<unsigned char>(y));
        });
    }

    std::vector<Track> tracks_;
};

}  // namespace nexdex
