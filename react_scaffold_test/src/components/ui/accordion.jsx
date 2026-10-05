import React, { useState } from 'react';

export const Accordion = ({ children, className = '', ...props }) => (
  <div className={className} {...props}>{children}</div>
);

export const AccordionItem = ({ children, className = '', ...props }) => (
  <div className={`border-b ${className}`} {...props}>{children}</div>
);

export const AccordionTrigger = ({ children, className = '', ...props }) => {
  const [open, setOpen] = useState(false);
  return (
    <button type='button' className={`flex w-full items-center justify-between py-4 text-left font-medium ${className}`} onClick={() => setOpen(v => !v)} {...props}>
      <span>{children}</span><span aria-hidden='true'>{open ? '−' : '+'}</span>
    </button>
  );
};

export const AccordionContent = ({ children, className = '', ...props }) => (
  <div className={`pb-4 text-sm text-muted-foreground ${className}`} {...props}>{children}</div>
);
