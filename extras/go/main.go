// extras/go — decorative, not wired into the build. a toy CLI that mirrors
// the shape of backend/search.py's result cards (title/artist/cover/duration)
// without actually calling anything. run with: go run main.go

package main

import (
	"fmt"
	"strings"
)

// SearchResult mirrors the dicts returned by backend/search.py's
// search_youtube / search_soundcloud / search_apple_music.
type SearchResult struct {
	Title    string
	Artist   string
	CoverURL string
	Duration string
	Source   string
}

func (r SearchResult) String() string {
	return fmt.Sprintf("[%s] %s -- %s (%s)", strings.ToUpper(r.Source), r.Artist, r.Title, r.Duration)
}

type AudioFormat struct {
	Ext      string
	Lossless bool
}

var formats = []AudioFormat{
	{"mp3", false},
	{"flac", true},
	{"wav", true},
	{"m4a", false},
	{"alac", true},
	{"ogg", false},
	{"opus", false},
}

func losslessFormats() []string {
	var out []string
	for _, f := range formats {
		if f.Lossless {
			out = append(out, f.Ext)
		}
	}
	return out
}

func renderProgress(label string, percent int, width int) string {
	if percent > 100 {
		percent = 100
	}
	if percent < 0 {
		percent = 0
	}
	filled := width * percent / 100
	bar := strings.Repeat("#", filled) + strings.Repeat("-", width-filled)
	return fmt.Sprintf("%-20s [%s] %3d%%", label, bar, percent)
}

func main() {
	results := []SearchResult{
		{"MATADORA (Extended)", "SUKA.", "", "3:42", "youtube"},
		{"Aria Math (Epic Version)", "Logan Feece", "", "4:10", "soundcloud"},
	}

	fmt.Println("nexdex.space -- go toy search demo")
	for _, r := range results {
		fmt.Println(r)
	}

	fmt.Println("\nlossless formats:", strings.Join(losslessFormats(), ", "))

	fmt.Println()
	for pct := 0; pct <= 100; pct += 20 {
		fmt.Println(renderProgress("MATADORA (Extended)", pct, 30))
	}

	fmt.Println("\nmade by savsis with <3")
}
