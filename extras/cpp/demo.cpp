// extras/cpp/demo.cpp — decorative, not part of the build. compile with:
//   cl.exe /std:c++17 /EHsc demo.cpp /Fe:demo.exe
// or: g++ -std=c++17 demo.cpp -o demo

#include <iostream>
#include "audio_meta.hpp"
#include "progress_bar.hpp"
#include "playlist.hpp"

int main() {
    using nexdex::AudioTagBuilder;
    using nexdex::ProgressBar;
    using nexdex::Playlist;
    using nexdex::Track;

    auto tag = AudioTagBuilder("MATADORA (Extended)", "SUKA.")
                   .year(2026)
                   .build();

    std::cout << tag.describe() << "\n\n";

    ProgressBar bar("MATADORA (Extended)", 30);
    for (int pct = 0; pct <= 100; pct += 20) {
        std::cout << bar.render(pct) << "\n";
    }

    Playlist playlist;
    playlist.add(Track{tag, "downloads/MATADORA (Extended).flac", 222});
    std::cout << "\nplaylist: " << playlist.size() << " track(s), total "
              << Playlist::formatDuration(playlist.totalDurationSecs()) << "\n";

    std::cout << "\nmade by savsis with <3\n";
    return 0;
}
