export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const calculateSavings = (currentPrice: number, targetPrice: number): number => {
  return Math.max(0, targetPrice - currentPrice);
};

export const calculateSavingsPercentage = (currentPrice: number, targetPrice: number): number => {
  if (currentPrice >= targetPrice) return 0;
  return ((targetPrice - currentPrice) / targetPrice) * 100;
};

export const isValidAmazonUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.includes('amazon.com') || urlObj.hostname.includes('amazon.in');
  } catch {
    return false;
  }
};

export const extractProductId = (url: string): string | null => {
  const match = url.match(/\/dp\/([A-Z0-9]{10})/);
  return match ? match[1] : null;
}; 