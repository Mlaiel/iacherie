import * as React from "react";
import { cn } from "@/lib/utils";

interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, checked, onCheckedChange, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onCheckedChange?.(e.target.checked);
      onChange?.(e);
    };

    return (
      <label className={cn("relative inline-flex h-6 w-11 items-center", className)}>
        <input
          type="checkbox"
          className="sr-only"
          checked={checked}
          onChange={handleChange}
          ref={ref}
          {...props}
        />
        <span className="block h-6 w-11 rounded-full bg-gray-300 transition-colors peer-checked:bg-blue-600">
          <span 
            className={cn(
              "block h-5 w-5 rounded-full bg-white shadow-lg ring-0 transition-transform translate-x-0.5 translate-y-0.5",
              checked && "translate-x-5"
            )}
          />
        </span>
      </label>
    );
  }
);
Switch.displayName = "Switch";

export { Switch };