import React from 'react';

export const Avatar = React.forwardRef(({ className = '', children, ...props }, ref) => (
  <span ref={ref} className={`inline-flex h-10 w-10 shrink-0 overflow-hidden rounded-full bg-muted ${className}`} {...props}>
    {children}
  </span>
));
Avatar.displayName = 'Avatar';

export const AvatarImage = React.forwardRef(({ src, alt = '', className = '', ...props }, ref) => (
  <img ref={ref} src={src} alt={alt} className={`aspect-square h-full w-full object-cover ${className}`} {...props} />
));
AvatarImage.displayName = 'AvatarImage';

export const AvatarFallback = React.forwardRef(({ children, className = '', ...props }, ref) => (
  <span ref={ref} className={`flex h-full w-full items-center justify-center rounded-full bg-muted text-sm font-medium ${className}`} {...props}>
    {children}
  </span>
));
AvatarFallback.displayName = 'AvatarFallback';
