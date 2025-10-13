import * as React from "react";
import { cn } from "@/lib/utils";

interface SheetProps {
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const Sheet: React.FC<SheetProps> = ({ children, open, onOpenChange }) => {
  return <div>{children}</div>;
};

const SheetTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, children, ...props }, ref) => (
  <button
    ref={ref}
    className={cn("", className)}
    {...props}
  >
    {children}
  </button>
));
SheetTrigger.displayName = "SheetTrigger";

const SheetContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "fixed z-50 gap-4 bg-white p-6 shadow-lg transition ease-in-out inset-y-0 right-0 h-full w-3/4 border-l sm:max-w-sm",
      className
    )}
    {...props}
  >
    {children}
  </div>
));
SheetContent.displayName = "SheetContent";

export { Sheet, SheetContent, SheetTrigger };