import { useState, useCallback } from 'react';
import { isValidAmazonUrl } from '../utils/helpers';

interface ProductInputState {
  amazonUrl: string;
  targetPrice: string;
  email: string;
  errors: {
    amazonUrl?: string;
    targetPrice?: string;
    email?: string;
  };
}

export const useProductInput = (onAddProduct: (amazonUrl: string, targetPrice: number, email: string) => Promise<void>) => {
  const [state, setState] = useState<ProductInputState>({
    amazonUrl: '',
    targetPrice: '',
    email: '',
    errors: {}
  });

  const validateForm = useCallback(() => {
    const errors: ProductInputState['errors'] = {};

    if (!state.amazonUrl) {
      errors.amazonUrl = 'Amazon URL is required';
    } else if (!isValidAmazonUrl(state.amazonUrl)) {
      errors.amazonUrl = 'Please enter a valid Amazon URL';
    }

    if (!state.targetPrice) {
      errors.targetPrice = 'Target price is required';
    } else {
      const price = parseFloat(state.targetPrice);
      if (isNaN(price) || price <= 0) {
        errors.targetPrice = 'Please enter a valid price greater than 0';
      }
    }

    if (!state.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email)) {
      errors.email = 'Please enter a valid email address';
    }

    setState(prev => ({ ...prev, errors }));
    return Object.keys(errors).length === 0;
  }, [state.amazonUrl, state.targetPrice, state.email]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        await onAddProduct(
          state.amazonUrl,
          parseFloat(state.targetPrice),
          state.email
        );
        setState({
          amazonUrl: '',
          targetPrice: '',
          email: '',
          errors: {}
        });
      } catch (error) {
        // Error handling is done in the parent component
      }
    }
  }, [state, validateForm, onAddProduct]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setState(prev => ({
      ...prev,
      [name]: value,
      errors: {
        ...prev.errors,
        [name]: undefined
      }
    }));
  }, []);

  return {
    state,
    handleChange,
    handleSubmit
  };
}; 