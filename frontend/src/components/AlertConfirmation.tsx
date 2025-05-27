interface AlertConfirmationProps {
  targetPrice?: number;
  email?: string;
  isPriceDrop?: boolean;
}

const AlertConfirmation = ({ targetPrice, email, isPriceDrop }: AlertConfirmationProps) => {
  if (!targetPrice && !email && !isPriceDrop) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animate-fade-in">
      <div className="flex items-center space-x-3">
        {isPriceDrop ? (
          <>
            <div className="flex-shrink-0">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-full">
                <svg
                  className="h-6 w-6 text-green-500 dark:text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Price drop alert sent!
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Check your email for details.
              </p>
            </div>
          </>
        ) : (
          <>
            <div className="flex-shrink-0">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-full">
                <svg
                  className="h-6 w-6 text-blue-500 dark:text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Alert scheduled for ₹{targetPrice?.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                You'll be notified at {email}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AlertConfirmation; 