interface ProductInfoProps {
  image: string;
  title: string;
  currentPrice: number;
  amazonUrl: string;
  status: 'tracking' | 'alert_set' | 'price_drop';
}

const ProductInfo = ({ image, title, currentPrice, amazonUrl, status }: ProductInfoProps) => {
  const getStatusBadge = () => {
    const statusStyles = {
      tracking: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      alert_set: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      price_drop: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    };

    const statusText = {
      tracking: 'Tracking...',
      alert_set: 'Price Drop Alert Set',
      price_drop: 'Price Drop Alert Sent!',
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status]}`}>
        {statusText[status]}
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex flex-col md:flex-row gap-6">
        <div className="w-full md:w-1/3">
          <img
            src={image}
            alt={title}
            className="w-full h-48 object-contain rounded-lg bg-gray-50 dark:bg-gray-700"
          />
        </div>
        
        <div className="flex-1 space-y-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              {title}
            </h2>
            {getStatusBadge()}
          </div>

          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            ₹{currentPrice.toLocaleString()}
          </div>

          <a
            href={amazonUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
          >
            View on Amazon
            <svg
              className="ml-1 w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
};

export default ProductInfo; 