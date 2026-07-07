// extras/cpp — decorative. a tiny console progress bar, echoing the shape
// of the /api/job/<id> polling response from backend/jobs.py.
#pragma once

#include <string>
#include <algorithm>

namespace nexdex {

class ProgressBar {
public:
    ProgressBar(std::string label, int width) : label_(std::move(label)), width_(width) {}

    std::string render(int percent) const {
        percent = std::clamp(percent, 0, 100);
        int filled = width_ * percent / 100;
        int empty = width_ - filled;

        std::string bar;
        bar.append(filled, '#');
        bar.append(empty, '-');

        return label_ + " [" + bar + "] " + std::to_string(percent) + "%";
    }

private:
    std::string label_;
    int width_;
};

}  // namespace nexdex
