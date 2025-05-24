import { Helmet } from "react-helmet-async"

interface MetaProps {
  title?: string
  description?: string
  keywords?: string
  ogImage?: string
  ogUrl?: string
}

const Meta = ({
  title = "PricePulse - Track E-commerce Prices",
  description = "Track prices of your favorite e-commerce products and get notified when they drop.",
  keywords = "price tracker, amazon price tracker, price drop alerts, e-commerce, price history",
  ogImage = "/og-image.png",
  ogUrl,
}: MetaProps) => {
  const siteUrl = ogUrl || (typeof window !== "undefined" ? window.location.href : "")

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content="website" />
      <meta property="og:url" content={siteUrl} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={siteUrl} />
      <meta property="twitter:title" content={title} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={ogImage} />

      {/* Favicon */}
      <link rel="icon" href="/favicon.ico" />
    </Helmet>
  )
}

export default Meta
