// a toy terminal progress bar, echoing the shape of the progress_hook
// callbacks used by backend/jobs.py — just rendered with print! here
// instead of pushed over the /api/job/<id> polling endpoint.

pub struct ProgressBar {
    width: usize,
    label: String,
}

impl ProgressBar {
    pub fn new(label: impl Into<String>, width: usize) -> Self {
        ProgressBar {
            width,
            label: label.into(),
        }
    }

    pub fn render(&self, percent: u8) -> String {
        let percent = percent.min(100) as usize;
        let filled = (self.width * percent) / 100;
        let empty = self.width - filled;

        format!(
            "{:<20} [{}{}] {:>3}%",
            self.label,
            "#".repeat(filled),
            "-".repeat(empty),
            percent
        )
    }
}

pub fn simulate_download(label: &str) {
    let bar = ProgressBar::new(label, 30);
    for pct in (0..=100).step_by(20) {
        println!("{}", bar.render(pct));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_percent_is_all_empty() {
        let bar = ProgressBar::new("test", 10);
        assert_eq!(bar.render(0), format!("{:<20} [{}] {:>3}%", "test", "-".repeat(10), 0));
    }

    #[test]
    fn hundred_percent_is_all_filled() {
        let bar = ProgressBar::new("test", 10);
        assert_eq!(bar.render(100), format!("{:<20} [{}] {:>3}%", "test", "#".repeat(10), 100));
    }

    #[test]
    fn clamps_above_100() {
        let bar = ProgressBar::new("test", 10);
        assert_eq!(bar.render(255), bar.render(100));
    }
}
