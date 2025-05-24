export const formatCurrency = (amount: number, currency = "USD", includeSymbol = true): string => {
  if (amount === undefined || amount === null) {
    return "N/A"
  }

  const formatter = new Intl.NumberFormat("en-US", {
    style: includeSymbol ? "currency" : "decimal",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

  return formatter.format(amount)
}
