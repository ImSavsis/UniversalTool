// extras/formats.ts — decorative, not wired into the Flask/JS frontend
// (the real frontend logic lives in app/static/js/app.js, plain JS).
// just a typed reference of the formats the downloader/converter understand.

type AudioFormat = "mp3" | "flac" | "wav" | "m4a" | "alac" | "ogg" | "opus";
type VideoFormat = "mp4" | "avi" | "mov" | "mkv" | "webm" | "gif";
type ImageFormat = "jpg" | "png" | "webp" | "bmp" | "gif" | "tiff" | "ico";
type DocFormat = "pdf" | "pptx";

interface FormatInfo {
  ext: string;
  lossless: boolean;
}

const AUDIO_FORMATS: Record<AudioFormat, FormatInfo> = {
  mp3: { ext: "mp3", lossless: false },
  flac: { ext: "flac", lossless: true },
  wav: { ext: "wav", lossless: true },
  m4a: { ext: "m4a", lossless: false },
  alac: { ext: "alac", lossless: true },
  ogg: { ext: "ogg", lossless: false },
  opus: { ext: "opus", lossless: false },
};

const VIDEO_FORMATS: VideoFormat[] = ["mp4", "avi", "mov", "mkv", "webm", "gif"];
const IMAGE_FORMATS: ImageFormat[] = ["jpg", "png", "webp", "bmp", "gif", "tiff", "ico"];
const DOC_FORMATS: DocFormat[] = ["pdf", "pptx"];

function isLossless(fmt: AudioFormat): boolean {
  return AUDIO_FORMATS[fmt].lossless;
}

interface SearchResult {
  title: string;
  artist: string;
  coverUrl: string | null;
  duration: string;
  source: "youtube" | "soundcloud" | "apple_music";
}

function describeResult(r: SearchResult): string {
  const cover = r.coverUrl ? "with cover" : "no cover";
  return `[${r.source}] ${r.artist} -- ${r.title} (${r.duration}, ${cover})`;
}

interface DownloadJob {
  jobId: string;
  status: "pending" | "downloading" | "processing" | "done" | "error";
  progress: number;
  speed: string;
}

class ProgressBar {
  constructor(private label: string, private width: number) {}

  render(percent: number): string {
    const clamped = Math.max(0, Math.min(100, percent));
    const filled = Math.round((this.width * clamped) / 100);
    const empty = this.width - filled;
    return `${this.label.padEnd(20)} [${"#".repeat(filled)}${"-".repeat(empty)}] ${clamped}%`;
  }
}

function simulateJob(jobId: string): DownloadJob[] {
  const steps: DownloadJob[] = [];
  for (let progress = 0; progress <= 100; progress += 25) {
    steps.push({
      jobId,
      status: progress < 100 ? "downloading" : "done",
      progress,
      speed: progress < 100 ? "1.2MiB/s" : "",
    });
  }
  return steps;
}

console.log("nexdex.space formats reference");
console.log("audio formats:", Object.keys(AUDIO_FORMATS));
console.log("lossless formats:", (Object.keys(AUDIO_FORMATS) as AudioFormat[]).filter(isLossless));
console.log("video formats:", VIDEO_FORMATS);
console.log("image formats:", IMAGE_FORMATS);
console.log("doc formats:", DOC_FORMATS);

const sample: SearchResult = {
  title: "MATADORA (Extended)",
  artist: "SUKA.",
  coverUrl: null,
  duration: "3:42",
  source: "youtube",
};
console.log(describeResult(sample));

const bar = new ProgressBar("MATADORA (Extended)", 30);
for (const job of simulateJob("demo-job")) {
  console.log(bar.render(job.progress), job.status);
}

console.log("made by savsis with <3");
