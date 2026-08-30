/**
 * Join conditional class names.
 *
 * Deliberately dependency-free — the project has no clsx/tailwind-merge
 * and the design system does not need conflict resolution.
 */
export function cn(
  ...classes: Array<string | false | null | undefined>
): string {
  return classes.filter(Boolean).join(" ");
}

/**
 * Format a file size in bytes for display ("1.4 MB").
 * Values below 1 KB stay in bytes; larger values use one decimal.
 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  const units = ["KB", "MB", "GB", "TB"];
  let value = bytes / 1024;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  return `${value.toFixed(1)} ${units[unitIndex]}`;
}
