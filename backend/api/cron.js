// Serverless function for scheduled price updates
const axios = require("axios")

module.exports = async (req, res) => {
  // Verify the request is authorized
  const authHeader = req.headers.authorization
  const expectedToken = process.env.CRON_SECRET

  if (!authHeader || authHeader !== `Bearer ${expectedToken}`) {
    return res.status(401).json({ error: "Unauthorized" })
  }

  try {
    console.log("Starting scheduled price update")

    // Get all products
    const productsResponse = await axios.get(`${process.env.API_URL}/api/products`)
    const products = productsResponse.data.products

    console.log(`Found ${products.length} products to update`)

    // Update each product
    for (const product of products) {
      try {
        // Fetch current price
        const scrapeResponse = await axios.post(`${process.env.API_URL}/api/products/update`, {
          product_id: product.id,
        })

        console.log(`Updated price for product ${product.id}: ${scrapeResponse.data.message}`)
      } catch (error) {
        console.error(`Error updating product ${product.id}:`, error.message)
      }
    }

    return res.status(200).json({
      success: true,
      message: `Updated prices for ${products.length} products`,
    })
  } catch (error) {
    console.error("Error in cron job:", error.message)
    return res.status(500).json({
      success: false,
      error: error.message,
    })
  }
}
