const STORAGE_KEY = "copycat-hide-personal-details";

/** Default: privacy filter is on. */
export function getHidePersonalDetails(): boolean {
  if (typeof window === "undefined") return true;
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === null) return true;
  return stored === "true";
}

export function setHidePersonalDetails(enabled: boolean): void {
  localStorage.setItem(STORAGE_KEY, String(enabled));
}

export const PRIVACY_SETTING_LABEL = "Hide personal details in recordings";

export const PRIVACY_SETTING_DESCRIPTION =
  "Scan recordings locally for emails, phone numbers, passwords, and ID-like numbers. Sensitive regions are covered with black boxes before any frame is sent to AI analysis.";

export const PRIVACY_STATUS_MESSAGE =
  "Privacy filter applied — sensitive information was hidden before AI analysis.";
