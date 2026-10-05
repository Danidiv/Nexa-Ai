import { forwardRef } from 'react';

const Card = forwardRef(({ children, className = '', ...props }, ref) => (
  <div ref={ref} className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
));

const Button = forwardRef(({ children, variant = 'primary', size = 'md', disabled = false, className = '', ...props }, ref) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none';
  const sizeClasses = { md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' };
  const variantClasses = { primary: 'bg-blue-500 hover:bg-blue-600 text-white', secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-800' };

  return (
    <button
      ref={ref}
      disabled={disabled}
      className={`${baseClasses} ${size === 'lg' ? sizeClasses.lg : sizeClasses.md} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
});

export { Card, Button };