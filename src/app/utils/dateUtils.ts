/**
 * Date Utility Functions
 * Handles timezone-aware date operations for EST/EDT
 */

/**
 * Format a Date object to YYYY-MM-DD in local timezone
 * Prevents timezone shift issues when converting dates
 */
export function formatDateToYYYYMMDD(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Parse a date string and return a Date object in local timezone
 * Handles both ISO strings and YYYY-MM-DD format
 */
export function parseDate(dateString: string): Date {
  // If it's just YYYY-MM-DD, create date at local midnight
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(year, month - 1, day);
  }
  // Otherwise parse as ISO string
  return new Date(dateString);
}

/**
 * Format a date string for display in EST/EDT
 */
export function formatDateForDisplay(dateString: string, options?: Intl.DateTimeFormatOptions): string {
  const date = parseDate(dateString);
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'America/New_York', // EST/EDT
    ...options
  };
  
  return date.toLocaleDateString('en-US', defaultOptions);
}

/**
 * Format a date with time in EST/EDT
 */
export function formatDateTimeForDisplay(dateString: string): string {
  const date = parseDate(dateString);
  
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/New_York', // EST/EDT
  });
}

/**
 * Get today's date in YYYY-MM-DD format (local timezone)
 */
export function getTodayYYYYMMDD(): string {
  return formatDateToYYYYMMDD(new Date());
}

/**
 * Check if a date string is today (in local timezone)
 */
export function isToday(dateString: string): boolean {
  const date = parseDate(dateString);
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}
